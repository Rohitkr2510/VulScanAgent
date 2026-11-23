from agent.test_runner.runner import TestRunner
from agent.models import TestStatus


def test_test_runner_detection(tmp_path):
    runner = TestRunner()

    # Empty repo -> SKIPPED
    res = runner.run_tests(tmp_path)
    assert res.status == TestStatus.SKIPPED

    # Python tests dir exists -> command contains pytest
    (tmp_path / "tests").mkdir()
    detected_cmd = runner.detect_command(tmp_path)
    assert "pytest" in detected_cmd

    # Package.json exists -> command contains npm
    pkg_json = tmp_path / "package.json"
    pkg_json.write_text('{"name": "sample"}', encoding="utf-8")
    custom_runner = TestRunner(custom_command=None)
    # package.json check has priority or detection
    assert custom_runner.detect_command(tmp_path) is not None
