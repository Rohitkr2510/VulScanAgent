# Scanner Extensibility Guide

VulScanAgent is designed around modular, pluggable scanners inheriting from `BaseScanner` (`agent/scanner/base.py`).

---

## 1. The `BaseScanner` Interface

To implement a new scanner, inherit from `BaseScanner` and implement the `scan` method:

```python
from pathlib import Path
from typing import List
from agent.scanner.base import BaseScanner
from agent.models import VulFinding, VulnerabilityCategory, VulnerabilitySeverity

class CustomSecurityScanner(BaseScanner):
    def __init__(self):
        super().__init__("Custom Scanner")

    def scan(self, repo_dir: Path, severity_threshold: VulnerabilitySeverity) -> List[VulFinding]:
        findings: List[VulFinding] = []
        
        # Implement your detection logic here...
        
        return [f for f in findings if f.severity.meets_threshold(severity_threshold)]
```

---

## 2. Adding Custom SAST Rules

To add a new SAST detection rule in `agent/scanner/sast.py`, add a dictionary entry to the `rules` list:

```python
{
    "rule_id": "SEC-PY-HARDCODED-TMP",
    "title": "Insecure temporary file creation via mktemp",
    "severity": VulnerabilitySeverity.MEDIUM,
    "pattern": re.compile(r"""tempfile\.mktemp\s*\("""),
    "exts": [".py"],
    "description": "mktemp is vulnerable to symlink race conditions.",
    "hint": "Use tempfile.NamedTemporaryFile or tempfile.TemporaryDirectory instead."
}
```

---

## 3. Registering with `CompositeScanner`

Register your new scanner in `agent/scanner/__init__.py`:

```python
scanner_registry = {
    "sast": SASTScanner(),
    "secrets": SecretsScanner(),
    "sca": SCAScanner(),
    "iac": IaCScanner(),
    "custom": CustomSecurityScanner(), # Your new scanner
}
```

Enable it in `config/config.yaml`:
```yaml
scanning:
  scanners:
    - "sast"
    - "secrets"
    - "sca"
    - "iac"
    - "custom"
```
