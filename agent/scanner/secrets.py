import re
from pathlib import Path
from typing import List

from agent.scanner.base import BaseScanner
from agent.models import VulFinding, VulnerabilityCategory, VulnerabilitySeverity


class SecretsScanner(BaseScanner):
    """Scanner for hardcoded secrets, tokens, API keys, and credentials."""

    def __init__(self):
        super().__init__("Secrets Scanner")
        self.secret_patterns = [
            {
                "rule_id": "SEC-SECRET-AWS",
                "title": "Hardcoded AWS Access Key",
                "severity": VulnerabilitySeverity.CRITICAL,
                "pattern": re.compile(r"""\b(AKIA[0-9A-Z]{16})\b"""),
                "description": "Exposing AWS Access Keys allows unauthorized infrastructure access.",
                "hint": "Remove hardcoded credentials and load them from environment variables or IAM roles."
            },
            {
                "rule_id": "SEC-SECRET-GITHUB",
                "title": "Hardcoded GitHub Personal Access Token",
                "severity": VulnerabilitySeverity.CRITICAL,
                "pattern": re.compile(r"""\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b"""),
                "description": "Leaked GitHub tokens allow full read/write access to repositories and organizations.",
                "hint": "Revoke the token immediately and inject it via GitHub Secrets or environment variables."
            },
            {
                "rule_id": "SEC-SECRET-OPENAI",
                "title": "Hardcoded OpenAI API Key",
                "severity": VulnerabilitySeverity.CRITICAL,
                "pattern": re.compile(r"""\b(sk-[a-zA-Z0-9]{32,64}|sk-proj-[a-zA-Z0-9-_]{48,128})\b"""),
                "description": "Exposing OpenAI keys allows unauthorized AI model consumption and billing charges.",
                "hint": "Store API keys in environment variables (e.g. os.getenv('OPENAI_API_KEY'))."
            },
            {
                "rule_id": "SEC-SECRET-PRIVATE-KEY",
                "title": "Private Cryptographic Key in Source Code",
                "severity": VulnerabilitySeverity.CRITICAL,
                "pattern": re.compile(r"""-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"""),
                "description": "Committed private keys compromise encryption and identity guarantees.",
                "hint": "Move the private key to a secret store (Vault, AWS Secrets Manager, or file outside git)."
            },
            {
                "rule_id": "SEC-SECRET-GENERIC",
                "title": "Hardcoded Generic Secret or Password Assignment",
                "severity": VulnerabilitySeverity.HIGH,
                "pattern": re.compile(r"""(?i)(api[_-]?key|auth[_-]?token|secret[_-]?key|password|passwd)\s*[:=]\s*["']([A-Za-z0-9+/=_\-~@!#$%^&*]{16,})["']"""),
                "description": "Hardcoding credentials or API secrets in source files exposes them to all repository readers.",
                "hint": "Replace with environment variable lookups (e.g., os.getenv('...')) or a config file excluded by .gitignore."
            }
        ]

    def scan(self, repo_dir: Path, severity_threshold: VulnerabilitySeverity) -> List[VulFinding]:
        findings: List[VulFinding] = []
        counter = 0

        # Scan code files, configuration files, and env templates
        for path in repo_dir.rglob("*"):
            if not path.is_file() or self.should_ignore(path):
                continue

            # Skip common test fixtures or sample env templates if explicitly named .env.example
            if path.name in [".env.example", ".env.sample"]:
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
            except Exception:
                continue

            rel_path = path.relative_to(repo_dir).as_posix()

            for line_idx, line in enumerate(lines, start=1):
                # Ignore comment-only explanations
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                    continue

                for rule in self.secret_patterns:
                    match = rule["pattern"].search(line)
                    if match:
                        counter += 1
                        # Mask the secret in snippet
                        secret_val = match.group(0)
                        masked_val = secret_val[:4] + "*" * (len(secret_val) - 8) + secret_val[-4:] if len(secret_val) > 8 else "****"
                        masked_line = line.replace(secret_val, masked_val)

                        finding = VulFinding(
                            id=f"{rule['rule_id']}-{counter}",
                            title=rule["title"],
                            category=VulnerabilityCategory.SECRETS,
                            severity=rule["severity"],
                            file_path=rel_path,
                            line_number=line_idx,
                            end_line_number=line_idx,
                            rule_id=rule["rule_id"],
                            cwe_id="CWE-798",
                            mitre_attack_id="T1552.001",
                            mitre_d3fend_id="D3-CH",
                            owasp_category="A07:2021-Identification and Authentication Failures",
                            description=rule["description"],
                            code_snippet=masked_line,
                            remediation_hint=rule["hint"],
                            raw_scanner_data={"masked_finding": masked_val}
                        )
                        if finding.severity.meets_threshold(severity_threshold):
                            findings.append(finding)

        return findings
