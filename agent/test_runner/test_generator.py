import re
import logging
from pathlib import Path
from typing import Optional

from agent.models import VulFinding
from agent.ai_fix.prompts import SYSTEM_PROMPT, build_test_prompt
from agent.ai_fix.provider_router import AIProviderRouter

logger = logging.getLogger(__name__)


class AITestGenerator:
    """Synthesizes targeted regression tests for fixed security vulnerabilities."""

    def __init__(self, router: AIProviderRouter):
        self.router = router

    def generate_test_case(
        self,
        repo_dir: Path,
        finding: VulFinding,
        original_content: str,
        fixed_content: str
    ) -> Optional[Path]:
        """Generates a test file in the repository's test directory."""
        prompt = build_test_prompt(
            file_path=finding.file_path,
            original_content=original_content,
            fixed_content=fixed_content,
            finding_dict=finding.model_dump()
        )

        try:
            response_text, provider, model = self.router.generate(SYSTEM_PROMPT, prompt)
            code_match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", response_text)
            test_code = code_match.group(1) if code_match else response_text

            # Determine where to write the test
            tests_dir = repo_dir / "tests"
            if not tests_dir.exists():
                tests_dir.mkdir(parents=True, exist_ok=True)

            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", finding.id.lower())
            ext = Path(finding.file_path).suffix or ".py"
            test_file = tests_dir / f"test_vulscan_{safe_name}{ext}"

            test_file.write_text(test_code, encoding="utf-8")
            logger.info(f"Generated verification test at {test_file}")
            return test_file

        except Exception as e:
            logger.warning(f"Could not generate AI test case: {e}")
            return None
