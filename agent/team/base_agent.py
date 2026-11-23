import json
import logging
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel

from agent.ai_fix.provider_router import AIProviderRouter

console = Console()
logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for specialized collaborative security agents."""

    def __init__(self, name: str, role: str, router: AIProviderRouter, color: str = "cyan"):
        self.name = name
        self.role = role
        self.router = router
        self.color = color
        self.chat_history: List[Dict[str, str]] = []

    def log_thought(self, message: str, title: Optional[str] = None) -> None:
        """Formatted terminal log for agent deliberations."""
        panel_title = title or f"[{self.color}]{self.name} — {self.role}[/{self.color}]"
        console.print(Panel(message, title=panel_title, border_style=self.color, expand=False))

    def ask(self, system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
        """Invokes LLM via the unified multi-provider router with context history."""
        full_system = f"You are {self.name}, {self.role}.\n{system_prompt}"
        if json_mode:
            full_system += "\nYou MUST return valid JSON ONLY, without markdown code fences or conversational text."

        raw_response, provider, model = self.router.generate(full_system, user_prompt)
        self.chat_history.append({"role": "user", "content": user_prompt})
        self.chat_history.append({"role": "assistant", "content": raw_response})

        return raw_response.strip()

    def ask_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Convenience method that queries the LLM and guarantees a parsed JSON dictionary."""
        response_text = self.ask(system_prompt, user_prompt, json_mode=True)
        # Clean any accidental markdown code fences
        cleaned = response_text
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"{self.name} failed to return valid JSON: {cleaned}. Fallback wrapper used.")
            return {"raw_text": response_text, "error": str(e)}
