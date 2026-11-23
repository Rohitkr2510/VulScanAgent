import sys
import time
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

from agent.models import TestResult, TestStatus
from agent.security.guardrails import AgentGuardrails

logger = logging.getLogger(__name__)


class TestRunner:
    """Detects and runs project test suites (pytest, npm test, etc.) to ensure fixes don't break code."""
    __test__ = False

    def __init__(self, timeout_seconds: int = 180, custom_command: Optional[str] = None):
        self.timeout_seconds = timeout_seconds
        self.custom_command = custom_command

    def detect_command(self, repo_dir: Path) -> Optional[List[str]]:
        """Automatically detects test runner based on repository layout."""
        if self.custom_command:
            return self.custom_command.split()

        # 1. Python (pytest or unittest)
        if (repo_dir / "pytest.ini").exists() or (repo_dir / "pyproject.toml").exists() or (repo_dir / "setup.cfg").exists() or any(repo_dir.glob("tests")):
            return [sys.executable, "-m", "pytest", "-o", "pythonpath=.", "-v"]

        # 2. Node / JS (npm test)
        if (repo_dir / "package.json").exists():
            return ["npm", "test"]

        # 3. Go
        if (repo_dir / "go.mod").exists():
            return ["go", "test", "./..."]

        # 4. Java / Maven
        if (repo_dir / "pom.xml").exists():
            return ["mvn", "test"]

        # Default fallback to pytest if python files are present
        if list(repo_dir.rglob("*.py")):
            return [sys.executable, "-m", "pytest"]

        return None

    def run_tests(self, repo_dir: Path) -> TestResult:
        """Executes repository tests and captures stdout, stderr, exit code."""
        cmd_list = self.detect_command(repo_dir)

        if not cmd_list:
            logger.info("No test framework detected; marking tests as SKIPPED.")
            return TestResult(
                status=TestStatus.SKIPPED,
                command="none",
                stdout="No test suite detected in repository.",
                exit_code=0,
                duration_seconds=0.0
            )

        # Enforce deny-by-default execution policy
        cmd_list = AgentGuardrails.sanitize_command(cmd_list)
        cmd_str = " ".join(cmd_list)
        logger.info(f"Running test command: {cmd_str} in {repo_dir}")
        start_time = time.time()

        try:
            res = subprocess.run(
                cmd_list,
                cwd=str(repo_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False
            )
            duration = round(time.time() - start_time, 2)
            passed = (res.returncode == 0)

            return TestResult(
                status=TestStatus.PASSED if passed else TestStatus.FAILED,
                command=cmd_str,
                stdout=res.stdout,
                stderr=res.stderr,
                exit_code=res.returncode,
                duration_seconds=duration,
                failure_details=res.stderr if not passed else None
            )

        except subprocess.TimeoutExpired:
            duration = round(time.time() - start_time, 2)
            return TestResult(
                status=TestStatus.ERROR,
                command=cmd_str,
                stdout="",
                stderr=f"Test run timed out after {self.timeout_seconds} seconds.",
                exit_code=124,
                duration_seconds=duration,
                failure_details="Timeout expired."
            )
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            return TestResult(
                status=TestStatus.ERROR,
                command=cmd_str,
                stdout="",
                stderr=str(e),
                exit_code=1,
                duration_seconds=duration,
                failure_details=str(e)
            )
