from unittest.mock import patch
from agent.ai_fix.provider_router import AIProviderRouter
from agent.team import (
    ScanStrategist,
    SecurityReviewer,
    ErrorDiagnostician,
    FixArchitect,
    PRAuditor,
)
from agent.models import (
    VulFinding,
    VulnerabilityCategory,
    VulnerabilitySeverity,
    FixResult,
    FixAttempt,
    TestResult,
    TestStatus,
)


def test_scan_strategist(tmp_path):
    (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("requests==2.28.0", encoding="utf-8")

    router = AIProviderRouter()
    strategist = ScanStrategist(router)

    mock_plan = (
        '{"primary_language": "Python", "recommended_scanners": ["sast", "sca"], '
        '"focus_areas": ["Dependency CVEs", "Injection vectors"]}'
    )

    with patch.object(router, "generate", return_value=(mock_plan, "mock", "gpt-4o")):
        plan = strategist.assess_repository(tmp_path)
        assert plan["primary_language"] == "Python"
        assert "sast" in plan["recommended_scanners"]


def test_security_reviewer():
    router = AIProviderRouter()
    reviewer = SecurityReviewer(router)

    finding = VulFinding(
        id="SEC-01",
        title="SQL Injection",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.HIGH,
        file_path="db.py",
    )

    mock_review = '{"approved": true, "feedback": "Patch uses parameterized query. Approved.", "confidence_score": 9}'

    with patch.object(router, "generate", return_value=(mock_review, "mock", "claude")):
        review = reviewer.review_fix(finding, "query = f'SELECT...'", "cursor.execute(sql, (id,))", "Param query")
        assert review["approved"] is True
        assert review["confidence_score"] == 9


def test_error_diagnostician():
    router = AIProviderRouter()
    diagnostician = ErrorDiagnostician(router)

    finding = VulFinding(
        id="SEC-02",
        title="Command Injection",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.CRITICAL,
        file_path="cmd.py",
    )

    mock_diag = '{"root_cause": "Missing import shlex", "prescribed_fix": "Add import shlex at top of file"}'

    with patch.object(router, "generate", return_value=(mock_diag, "mock", "gemini")):
        diagnosis = diagnostician.diagnose_failure("NameError: name 'shlex' is not defined", "cmd.py", "shlex.split()", finding)
        assert "shlex" in diagnosis["root_cause"]
        assert "import shlex" in diagnosis["prescribed_fix"]


def test_pr_auditor():
    router = AIProviderRouter()
    auditor = PRAuditor(router)

    finding = VulFinding(
        id="SEC-03",
        title="Insecure Deserialization",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.HIGH,
        file_path="serialize.py",
        description="pickle.loads used on untrusted data",
    )

    fix_res = FixResult(
        finding_id="SEC-03",
        success=True,
        attempts=[
            FixAttempt(
                attempt_number=1,
                provider_used="anthropic",
                model_name="claude-3-5-sonnet",
                proposed_diff="",
                explanation="Replaced pickle with json.loads.",
                files_modified=["serialize.py"],
            )
        ],
        test_result=TestResult(status=TestStatus.PASSED, command="pytest", duration_seconds=0.4),
    )

    doc = auditor.build_pr_documentation(finding, fix_res, {"feedback": "Approved by Senior Reviewer."})
    assert "Insecure Deserialization" in doc
    assert "PASSED" in doc
    assert "Checklist for Human Reviewer" in doc
