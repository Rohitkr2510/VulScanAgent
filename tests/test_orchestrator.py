from unittest.mock import MagicMock, patch
from pathlib import Path
from config.config_loader import AppConfig
from agent.orchestrator import VulScanOrchestrator
from agent.models import VulnerabilitySeverity, TestResult, TestStatus


def test_orchestrator_end_to_end_mock(tmp_path):
    # Setup test file
    app_py = tmp_path / "app.py"
    app_py.write_text(
        """
import os
def run_ping(ip):
    os.system("ping " + ip)
""",
        encoding="utf-8",
    )

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("def test_ok(): assert True\n", encoding="utf-8")

    config = AppConfig(
        repo={"url": "https://github.com/mock/repo", "branch": "main"},
        ai={"provider": "mock", "max_fix_retries": 1},
        scanning={"severity_threshold": VulnerabilitySeverity.HIGH},
        testing={"require_pass": True, "generate_ai_tests": False},
        pr={"draft": True},
    )

    orchestrator = VulScanOrchestrator(config)

    # Mock the LLM generation to return a remediated function using subprocess.run without shell=True
    mock_fixed_code = """
import subprocess
def run_ping(ip):
    subprocess.run(["ping", ip], check=True)
"""
    mock_response = f"""### EXPLANATION
Replaced os.system with safe subprocess list call.

### FIXED_FILE
```python
{mock_fixed_code}
```
"""

    with patch.object(orchestrator.router, "generate", return_value=(mock_response, "mock", "test-model")):
        # Mock test runner to pass
        with patch.object(
            orchestrator.test_runner,
            "run_tests",
            return_value=TestResult(status=TestStatus.PASSED, command="pytest", exit_code=0, duration_seconds=0.1),
        ):
            summary = orchestrator.run(local_repo_override=tmp_path)

            assert summary["status"] == "complete"
            assert summary["findings"] >= 1
            assert summary["fixed"] >= 1
            assert len(summary["prs"]) == 1
            assert "https://github.com/dry-run/pull/0" in summary["prs"][0]
