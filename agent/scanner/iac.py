import re
from pathlib import Path
from typing import List

from agent.scanner.base import BaseScanner
from agent.models import VulFinding, VulnerabilityCategory, VulnerabilitySeverity


class IaCScanner(BaseScanner):
    """Infrastructure-as-Code (IaC) and Container Configuration Scanner.
    
    Inspects Dockerfiles, Kubernetes manifests, and CI/CD workflow YAMLs
    for security misconfigurations.
    """

    def __init__(self):
        super().__init__("IaC Scanner")
        self.rules = [
            {
                "rule_id": "IAC-DOCKER-ROOT",
                "title": "Container Image Runs as Root User",
                "severity": VulnerabilitySeverity.MEDIUM,
                "target_file": re.compile(r"Dockerfile.*", re.IGNORECASE),
                "pattern": re.compile(r"^USER\s+root", re.MULTILINE),
                "description": "Containers running as root increase container escape risks if a vulnerability is exploited.",
                "hint": "Create and specify a non-root user (e.g. USER appuser)."
            },
            {
                "rule_id": "IAC-DOCKER-LATEST",
                "title": "Base Image Uses Unpinned 'latest' Tag",
                "severity": VulnerabilitySeverity.LOW,
                "target_file": re.compile(r"Dockerfile.*", re.IGNORECASE),
                "pattern": re.compile(r"^FROM\s+[^\s:]+:latest", re.MULTILINE),
                "description": "Using ':latest' leads to non-deterministic builds and untested upstream vulnerabilities.",
                "hint": "Pin the base image to an exact immutable digest or specific semver tag."
            },
            {
                "rule_id": "IAC-GHA-PULL-REQUEST-TARGET",
                "title": "Dangerous 'pull_request_target' Trigger with Code Checkout",
                "severity": VulnerabilitySeverity.HIGH,
                "target_file": re.compile(r"\.github/workflows/.*\.ya?ml", re.IGNORECASE),
                "pattern": re.compile(r"pull_request_target"),
                "description": "Using pull_request_target with an explicit checkout of untrusted PR code gives attackers write tokens and repository secrets access.",
                "hint": "Use standard 'pull_request' trigger or avoid checking out untrusted PR head refs."
            },
            {
                "rule_id": "IAC-COMPOSE-ALL-INTERFACES",
                "title": "Container Port Exposed on All Network Interfaces (0.0.0.0)",
                "severity": VulnerabilitySeverity.MEDIUM,
                "target_file": re.compile(r"docker-compose.*\.ya?ml", re.IGNORECASE),
                "pattern": re.compile(r"""(?:["']\s*([0-9]{2,5}:[0-9]{2,5})\s*["']|^\s*-\s*([0-9]{2,5}:[0-9]{2,5})\s*$)""", re.MULTILINE),
                "description": "Exposing container ports to all host interfaces ('0.0.0.0') bypasses local network protections and exposes services directly to untrusted networks.",
                "hint": "Bind container ports to localhost (e.g. '127.0.0.1:8000:8000') or route traffic through a TLS-terminating reverse proxy."
            }
        ]

    def scan(self, repo_dir: Path, severity_threshold: VulnerabilitySeverity) -> List[VulFinding]:
        findings: List[VulFinding] = []
        counter = 0

        for path in repo_dir.rglob("*"):
            if not path.is_file() or self.should_ignore(path):
                continue

            rel_path_str = path.relative_to(repo_dir).as_posix()

            for rule in self.rules:
                if rule["target_file"].search(path.name) or rule["target_file"].search(rel_path_str):
                    try:
                        content = path.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        continue

                    match = rule["pattern"].search(content)
                    if match:
                        counter += 1
                        line_num = content[:match.start()].count("\n") + 1
                        lines = content.splitlines()
                        snippet = lines[line_num - 1] if line_num - 1 < len(lines) else match.group(0)

                        finding = VulFinding(
                            id=f"{rule['rule_id']}-{counter}",
                            title=rule["title"],
                            category=VulnerabilityCategory.IAC,
                            severity=rule["severity"],
                            file_path=rel_path_str,
                            line_number=line_num,
                            end_line_number=line_num,
                            rule_id=rule["rule_id"],
                            cwe_id="CWE-250",
                            mitre_attack_id="T1611",
                            mitre_d3fend_id="D3-SPP",
                            owasp_category="A05:2021-Security Misconfiguration",
                            description=rule["description"],
                            code_snippet=snippet,
                            remediation_hint=rule["hint"],
                            raw_scanner_data={"rule_id": rule["rule_id"]}
                        )
                        if finding.severity.meets_threshold(severity_threshold):
                            findings.append(finding)

        return findings
