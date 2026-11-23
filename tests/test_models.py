import pytest
from agent.models import (
    VulnerabilitySeverity,
    VulnerabilityCategory,
    VulFinding,
    ScanReport,
    TestResult,
    TestStatus,
)


def test_severity_ordering():
    assert VulnerabilitySeverity.CRITICAL.meets_threshold(VulnerabilitySeverity.MEDIUM)
    assert VulnerabilitySeverity.HIGH.meets_threshold(VulnerabilitySeverity.HIGH)
    assert not VulnerabilitySeverity.LOW.meets_threshold(VulnerabilitySeverity.HIGH)
    assert VulnerabilitySeverity.INFO.score < VulnerabilitySeverity.LOW.score


def test_vulfinding_serialization():
    finding = VulFinding(
        id="SEC-001",
        title="SQL Injection",
        category=VulnerabilityCategory.SAST,
        severity=VulnerabilitySeverity.HIGH,
        file_path="app/db.py",
        line_number=42,
        rule_id="SEC-PY-SQLI",
        description="Dynamic SQL query",
        code_snippet="cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')",
        remediation_hint="Use parameterized queries",
    )
    dumped = finding.model_dump()
    assert dumped["id"] == "SEC-001"
    assert dumped["severity"] == "HIGH"
    assert dumped["category"] == "sast"


def test_scan_report_counts():
    report = ScanReport(
        repo_url="https://github.com/example/test-repo",
        repo_name="test-repo",
        branch="main",
        findings=[
            VulFinding(
                id="1",
                title="Crit 1",
                category=VulnerabilityCategory.SECRETS,
                severity=VulnerabilitySeverity.CRITICAL,
                file_path="key.py",
            ),
            VulFinding(
                id="2",
                title="High 1",
                category=VulnerabilityCategory.SAST,
                severity=VulnerabilitySeverity.HIGH,
                file_path="app.py",
            ),
            VulFinding(
                id="3",
                title="Med 1",
                category=VulnerabilityCategory.IAC,
                severity=VulnerabilitySeverity.MEDIUM,
                file_path="Dockerfile",
            ),
        ],
    )
    assert report.total_findings == 3
    assert report.critical_count == 1
    assert report.high_count == 1
    assert report.medium_count == 1
    assert report.low_count == 0
