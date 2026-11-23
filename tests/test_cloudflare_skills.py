import json
from pathlib import Path
from unittest.mock import patch

from agent.models import (
    VulFinding,
    VulnerabilityCategory,
    VulnerabilitySeverity,
    CandidateStatus,
    CoverageLedger,
    FixResult,
    TestResult,
    TestStatus,
)
from agent.ai_fix.provider_router import AIProviderRouter
from agent.team.candidate_verifier import CandidateVerifier
from agent.team.strategist import ScanStrategist
from agent.team.pr_auditor import PRAuditor


def test_candidate_verifier_confirms_valid_finding():
    finding = VulFinding(
        id="SEC-PY-SQLI-1",
        title="SQL Injection in user route",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.HIGH,
        file_path="routes/users.py",
        line_number=25,
        code_snippet="cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')",
        description="Dynamic query formatting allows SQL injection.",
    )

    mock_json_response = json.dumps({
        "verdict": "CONFIRMED",
        "confidence": 9,
        "reachability_proven": True,
        "disproof_rationale": "Directly accessible via HTTP GET /users?id= parameter without sanitization.",
        "taint_path": "HTTP query param user_id -> f-string -> cursor.execute()",
        "prerequisites": "None. Publicly exposed endpoint."
    })

    router = AIProviderRouter(preferred_provider="mock")
    verifier = CandidateVerifier(router)

    with patch.object(router, "generate", return_value=(mock_json_response, "mock", "test-model")):
        verdict = verifier.verify_candidate(finding, "def get_user(user_id): cursor.execute(f'SELECT...')")
        assert verdict.status == CandidateStatus.CONFIRMED
        assert verdict.reachability_proven is True
        assert verdict.confidence_score == 9
        assert "HTTP query param" in verdict.taint_path


def test_candidate_verifier_rejects_false_positive():
    finding = VulFinding(
        id="SEC-PY-CMD-INJ-2",
        title="Command execution in test mock",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.CRITICAL,
        file_path="tests/mock_env.py",
        line_number=10,
        code_snippet="os.system('echo test')",
        description="os.system call detected in test file.",
    )

    mock_json_response = json.dumps({
        "verdict": "REJECTED",
        "confidence": 10,
        "reachability_proven": False,
        "disproof_rationale": "Static hardcoded command in test mock file. No untrusted input can reach this line.",
        "taint_path": "None - Static test string",
        "prerequisites": "Internal unit test execution only."
    })

    router = AIProviderRouter(preferred_provider="mock")
    verifier = CandidateVerifier(router)

    with patch.object(router, "generate", return_value=(mock_json_response, "mock", "test-model")):
        verdict = verifier.verify_candidate(finding, "def test_mock(): os.system('echo test')")
        assert verdict.status == CandidateStatus.REJECTED
        assert verdict.reachability_proven is False
        assert "hardcoded" in verdict.disproof_rationale.lower()


def test_strategist_generates_architecture_and_ledger(tmp_path):
    (tmp_path / "app.py").write_text("print('hello')", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='demo'", encoding="utf-8")
    (tmp_path / "docker-compose.yml").write_text("version: '3'", encoding="utf-8")

    router = AIProviderRouter(preferred_provider="mock")
    strategist = ScanStrategist(router)

    mock_plan = json.dumps({
        "primary_language": "Python",
        "recommended_scanners": ["sast", "sca", "iac"],
        "focus_areas": ["FastAPI endpoints", "TOML dependencies"],
        "trust_boundaries": ["Internet <-> FastAPI"],
        "entry_points": ["HTTP GET /health"]
    })

    with patch.object(router, "generate", return_value=(mock_plan, "mock", "test-model")):
        plan = strategist.assess_repository(tmp_path)
        assert plan["primary_language"] == "Python"

        arch_file = tmp_path / "architecture.md"
        assert arch_file.exists()
        assert "Cloudflare-Style Architecture" in arch_file.read_text(encoding="utf-8")

        ledger_file = tmp_path / "coverage-ledger.json"
        assert ledger_file.exists()
        ledger_data = json.loads(ledger_file.read_text(encoding="utf-8"))
        assert ledger_data["total_files"] >= 3
        assert ledger_data["coverage_percent"] == 100.0


def test_pr_auditor_generates_multi_report_artifacts(tmp_path):
    router = AIProviderRouter(preferred_provider="mock")
    auditor = PRAuditor(router)

    finding = VulFinding(
        id="SCA-CVE-2024-56326-jinja2",
        title="Vulnerable Dependency: jinja2",
        category=VulnerabilityCategory.SCA,
        severity=VulnerabilitySeverity.HIGH,
        file_path="pyproject.toml",
        line_number=8,
        description="Jinja2 sandbox escape",
    )

    fix_res = FixResult(
        finding_id=finding.id,
        success=True,
        applied_files=["pyproject.toml"],
        test_result=TestResult(status=TestStatus.PASSED, command="pytest", duration_seconds=1.2),
    )

    artifacts = auditor.generate_audit_artifacts(
        repo_dir=tmp_path,
        all_candidates=[finding],
        confirmed_findings=[finding],
        fix_results=[fix_res]
    )

    assert "REPORT.md" in artifacts
    assert "FINDINGS-DETAIL.md" in artifacts
    assert "NEEDS-VALIDATION.md" in artifacts

    report_text = (tmp_path / "REPORT.md").read_text(encoding="utf-8")
    assert "Cloudflare security-audit-skill Framework" in report_text
    assert "Total Candidates Flagged" in report_text

    detail_text = (tmp_path / "FINDINGS-DETAIL.md").read_text(encoding="utf-8")
    assert "SCA-CVE-2024-56326-jinja2" in detail_text
