import tempfile
from pathlib import Path
from agent.models import VulnerabilitySeverity, VulnerabilityCategory
from agent.scanner.sast import SASTScanner
from agent.scanner.secrets import SecretsScanner
from agent.scanner.sca import SCAScanner
from agent.scanner.iac import IaCScanner
from agent.scanner import CompositeScanner


def test_sast_scanner_detects_sqli_and_cmd_injection(tmp_path):
    vulnerable_py = tmp_path / "vulnerable.py"
    vulnerable_py.write_text(
        """
import os
import sqlite3

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute(query) # sqli

def run_command(cmd):
    os.system("ping " + cmd) # cmd injection
""",
        encoding="utf-8",
    )

    scanner = SASTScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.MEDIUM)

    rule_ids = [f.rule_id for f in findings]
    assert "SEC-PY-SQLI" in rule_ids
    assert "SEC-PY-CMD-INJ" in rule_ids
    assert any(f.severity == VulnerabilitySeverity.CRITICAL for f in findings)


def test_secrets_scanner_detects_aws_and_token(tmp_path):
    config_py = tmp_path / "credentials.py"
    config_py.write_text(
        """
AWS_KEY = "AKIA1234567890ABCDEF"
GITHUB_KEY = "ghp_123456789012345678901234567890123456"
""",
        encoding="utf-8",
    )

    scanner = SecretsScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.HIGH)

    assert len(findings) >= 2
    rule_ids = [f.rule_id for f in findings]
    assert "SEC-SECRET-AWS" in rule_ids
    assert "SEC-SECRET-GITHUB" in rule_ids


def test_sca_scanner_detects_vulnerable_requests(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("requests==2.28.0\nflask==2.1.0\n", encoding="utf-8")

    scanner = SCAScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.HIGH)

    assert len(findings) >= 1
    assert any("CVE-2023-32681" in f.id for f in findings)


def test_sca_scanner_detects_pyproject_toml(tmp_path):
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        """[project]
name = "testapp"
dependencies = [
    "jinja2>=3.1,<4",
    "requests==2.28.0",
]
""",
        encoding="utf-8",
    )

    scanner = SCAScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.HIGH)

    assert len(findings) >= 2
    cves = [f.cve_id for f in findings]
    assert "CVE-2024-56326" in cves
    assert "CVE-2023-32681" in cves


def test_iac_scanner_detects_compose_all_interfaces(tmp_path):
    dc = tmp_path / "docker-compose.yml"
    dc.write_text(
        """services:
  web:
    ports:
      - "8000:8000"
""",
        encoding="utf-8",
    )

    scanner = IaCScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.LOW)
    rule_ids = [f.rule_id for f in findings]
    assert "IAC-COMPOSE-ALL-INTERFACES" in rule_ids


def test_iac_scanner_detects_root_in_dockerfile(tmp_path):
    df = tmp_path / "Dockerfile"
    df.write_text("FROM python:latest\nUSER root\nCMD ['python']\n", encoding="utf-8")

    scanner = IaCScanner()
    findings = scanner.scan(tmp_path, VulnerabilitySeverity.LOW)

    rule_ids = [f.rule_id for f in findings]
    assert "IAC-DOCKER-ROOT" in rule_ids
    assert "IAC-DOCKER-LATEST" in rule_ids


def test_composite_scanner_deduplication(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("AWS_KEY = 'AKIA1234567890ABCDEF'\n", encoding="utf-8")

    composite = CompositeScanner(["secrets"])
    findings = composite.run_all(tmp_path, VulnerabilitySeverity.HIGH)
    assert len(findings) == 1
