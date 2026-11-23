import re
from pathlib import Path
from typing import Optional
from agent.team.base_agent import BaseAgent
from agent.ai_fix.provider_router import AIProviderRouter
from agent.models import VulFinding


class TestVerifier(BaseAgent):
    """Test Verifier Agent (analogous to Rakan in reference repo).
    
    Synthesizes automated regression test cases that exercise both safe inputs
    and malicious exploit payloads to verify patch resilience.
    """

    def __init__(self, router: AIProviderRouter):
        super().__init__(
            name="TestVerifier",
            role="QA & Security Verification Specialist",
            router=router,
            color="magenta"
        )

    def generate_regression_test(
        self,
        repo_dir: Path,
        finding: VulFinding,
        original_code: str,
        fixed_code: str
    ) -> Optional[Path]:
        """Generates targeted verification test for the fixed vulnerability."""
        system_prompt = (
            "You are a Security Test Engineer. "
            "Write a standalone unit test to verify that the security fix functions correctly "
            "with valid inputs AND safely handles exploit inputs (e.g. injection payloads). "
            "Return ONLY the test code inside a markdown code block."
        )

        user_prompt = f"""Vulnerability: {finding.title}
File: {finding.file_path}

Patched Code:
```
{fixed_code[:2000]}
```

Generate automated unit test code."""

        response = self.ask(system_prompt, user_prompt)
        match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", response)
        test_code = match.group(1) if match else response

        tests_dir = repo_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        safe_id = re.sub(r"[^a-zA-Z0-9_]", "_", finding.id.lower())
        ext = Path(finding.file_path).suffix or ".py"
        test_path = tests_dir / f"test_vulscan_{safe_id}{ext}"
        test_path.write_text(test_code, encoding="utf-8")

        self.log_thought(f"Generated regression test at {test_path.name}", title="🧪 TestVerifier Generated Test")
        return test_path
