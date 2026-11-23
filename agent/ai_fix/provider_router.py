import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

user_creds = Path.home() / ".vulscan" / "credentials.env"
if user_creds.exists():
    load_dotenv(user_creds)
load_dotenv()

logger = logging.getLogger(__name__)

class AIProviderRouter:
    """Manages routing between OpenAI, Anthropic, and Google Gemini with auto-fallback."""

    def __init__(
        self,
        preferred_provider: str = "auto",
        fallback_order: list[str] = None,
        model_overrides: Dict[str, str] = None,
        temperature: float = 0.1
    ):
        self.preferred_provider = preferred_provider.lower()
        self.fallback_order = fallback_order or ["anthropic", "openai", "google"]
        self.model_overrides = model_overrides or {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        }
        self.temperature = temperature

    def _get_available_providers(self) -> list[str]:
        available = []
        if os.getenv("ANTHROPIC_API_KEY"):
            available.append("anthropic")
        if os.getenv("OPENAI_API_KEY"):
            available.append("openai")
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            available.append("google")
        return available

    def generate(self, system_prompt: str, user_prompt: str) -> Tuple[str, str, str]:
        """
        Generates completion using preferred provider or cascading fallbacks.
        Returns: (response_text, provider_name, model_name)
        """
        available = self._get_available_providers()
        if not available:
            raise ValueError(
                "No AI provider API key found. Please set at least one of: "
                "ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY in .env or environment."
            )

        # Determine evaluation order
        order = []
        if self.preferred_provider in available and self.preferred_provider != "auto":
            order.append(self.preferred_provider)

        for p in self.fallback_order:
            if p in available and p not in order:
                order.append(p)

        last_error = None
        for provider in order:
            try:
                logger.info(f"Attempting completion with provider: {provider}")
                if provider == "openai":
                    text, model = self._call_openai(system_prompt, user_prompt)
                    return text, provider, model
                elif provider == "anthropic":
                    text, model = self._call_anthropic(system_prompt, user_prompt)
                    return text, provider, model
                elif provider == "google":
                    text, model = self._call_gemini(system_prompt, user_prompt)
                    return text, provider, model
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}. Trying fallback...")
                last_error = e

        raise RuntimeError(f"All configured AI providers failed. Last error: {last_error}")

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = self.model_overrides.get("openai", "gpt-4o")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature
        )
        return response.choices[0].message.content or "", model

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        model = self.model_overrides.get("anthropic", "claude-3-5-sonnet-20241022")
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self.temperature
        )
        # Extract text from Anthropic response block
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text
        return text, model

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Tuple[str, str]:
        import time
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=api_key)
        preferred = os.getenv("GEMINI_MODEL") or self.model_overrides.get("google", "gemini-3.5-flash")
        candidate_models = [preferred]
        for fallback in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]:
            if fallback not in candidate_models:
                candidate_models.append(fallback)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=self.temperature
        )
        last_err = None
        for model in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model,
                        contents=user_prompt,
                        config=config
                    )
                    return response.text or "", model
                except Exception as e:
                    err_msg = str(e)
                    if "404" in err_msg:
                        break  # model doesn't exist, don't retry same model
                    logger.warning(f"Gemini model {model} attempt {attempt+1} failed: {e}. Backing off...")
                    last_err = e
                    time.sleep(1.0)

        raise last_err or RuntimeError("All Gemini candidate models failed.")
