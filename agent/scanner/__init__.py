from pathlib import Path
from typing import List, Dict
from agent.models import VulFinding, VulnerabilitySeverity
from agent.scanner.base import BaseScanner
from agent.scanner.sast import SASTScanner
from agent.scanner.secrets import SecretsScanner
from agent.scanner.sca import SCAScanner
from agent.scanner.iac import IaCScanner


class CompositeScanner:
    """Orchestrates all enabled scanners and aggregates findings."""

    def __init__(self, enabled_scanners: List[str] = None):
        scanner_registry: Dict[str, BaseScanner] = {
            "sast": SASTScanner(),
            "secrets": SecretsScanner(),
            "sca": SCAScanner(),
            "iac": IaCScanner(),
        }

        if enabled_scanners:
            self.scanners = [scanner_registry[s] for s in enabled_scanners if s in scanner_registry]
        else:
            self.scanners = list(scanner_registry.values())

    def run_all(self, repo_dir: Path, severity_threshold: VulnerabilitySeverity) -> List[VulFinding]:
        all_findings: List[VulFinding] = []
        for scanner in self.scanners:
            findings = scanner.scan(repo_dir, severity_threshold)
            all_findings.extend(findings)

        # Deduplicate by (file_path, line_number, rule_id)
        seen = set()
        deduped = []
        for f in all_findings:
            key = (f.file_path, f.line_number, f.rule_id or f.title)
            if key not in seen:
                seen.add(key)
                deduped.append(f)

        return deduped
