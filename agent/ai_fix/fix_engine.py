import re
import ast
import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from agent.models import VulFinding, FixAttempt, FixResult
from agent.ai_fix.prompts import SYSTEM_PROMPT, build_fix_prompt
from agent.ai_fix.provider_router import AIProviderRouter
from agent.security.guardrails import AgentGuardrails

logger = logging.getLogger(__name__)


class FixEngine:
    """Manages prompt construction, LLM fix generation, syntax verification, and patch application."""

    def __init__(self, router: AIProviderRouter, max_retries: int = 3):
        self.router = router
        self.max_retries = max_retries

    def attempt_fix(
        self,
        repo_dir: Path,
        finding: VulFinding,
        previous_error: Optional[str] = None,
        attempt_number: int = 1
    ) -> Tuple[Optional[str], Optional[FixAttempt], Optional[str]]:
        """
        Attempts to generate and validate a fix for a given finding.
        Returns: (fixed_content, fix_attempt_metadata, error_message)
        """
        target_file = repo_dir / finding.file_path
        if not target_file.exists():
            return None, None, f"File not found: {finding.file_path}"

        try:
            original_content = target_file.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return None, None, f"Could not read file {finding.file_path}: {e}"

        prompt = build_fix_prompt(
            file_path=finding.file_path,
            file_content=original_content,
            finding_dict=finding.model_dump(),
            previous_error=previous_error
        )

        try:
            raw_response, provider, model = self.router.generate(SYSTEM_PROMPT, prompt)
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return None, None, f"AI generation error: {str(e)}"

        explanation, fixed_content = self._parse_llm_response(raw_response)
        if not fixed_content:
            return None, None, "AI failed to return formatted fixed file content."

        # Validate syntax
        is_valid, syntax_err = self._validate_syntax(target_file.name, fixed_content)
        if not is_valid:
            logger.warning(f"Syntax validation failed on attempt {attempt_number}: {syntax_err}")
            return None, None, f"Syntax error in generated fix: {syntax_err}"

        attempt = FixAttempt(
            attempt_number=attempt_number,
            provider_used=provider,
            model_name=model,
            proposed_diff="",
            explanation=explanation,
            files_modified=[finding.file_path]
        )

        return fixed_content, attempt, None

    def apply_fix_to_disk(self, repo_dir: Path, file_path: str, new_content: str) -> None:
        # Runtime path traversal & resource exhaustion defense
        target = AgentGuardrails.validate_safe_path(repo_dir, file_path)
        AgentGuardrails.validate_patch_size(new_content)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_content, encoding="utf-8")

    def _validate_syntax(self, filename: str, content: str) -> Tuple[bool, Optional[str]]:
        """Verifies syntax before saving."""
        ext = Path(filename).suffix.lower()

        if ext == ".py":
            try:
                ast.parse(content)
                return True, None
            except SyntaxError as e:
                return False, f"Python SyntaxError at line {e.lineno}: {e.msg}"

        elif ext == ".json":
            try:
                json.loads(content)
                return True, None
            except json.JSONDecodeError as e:
                return False, f"JSON parse error: {e}"

        elif ext in [".yaml", ".yml"]:
            try:
                yaml.safe_load(content)
                return True, None
            except yaml.YAMLError as e:
                return False, f"YAML parse error: {e}"

        # Other languages (js, ts, dockerfile) pass basic structural checks
        return True, None

    def _parse_llm_response(self, text: str) -> Tuple[str, Optional[str]]:
        explanation = "Security fix applied."
        if "### EXPLANATION" in text:
            parts = text.split("### EXPLANATION")
            if len(parts) > 1:
                after_exp = parts[1]
                if "### FIXED_FILE" in after_exp:
                    exp_section = after_exp.split("### FIXED_FILE")[0]
                    explanation = exp_section.strip()

        # Extract fixed file block
        fixed_content = None
        if "### FIXED_FILE" in text:
            file_part = text.split("### FIXED_FILE")[1]
            code_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", file_part)
            if code_match:
                fixed_content = code_match.group(1)
        else:
            # Fallback to finding the largest fenced code block
            code_blocks = re.findall(r"```(?:\w+)?\n([\s\S]*?)```", text)
            if code_blocks:
                fixed_content = max(code_blocks, key=len)

        return explanation, fixed_content
