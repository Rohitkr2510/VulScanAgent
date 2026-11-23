from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from agent.models import VulFinding, VulnerabilitySeverity


class BaseScanner(ABC):
    """Abstract base class for security scanners."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def scan(self, repo_dir: Path, severity_threshold: VulnerabilitySeverity) -> List[VulFinding]:
        """Scan target repository and return normalized findings meeting the threshold."""
        pass

    def should_ignore(self, path: Path, exclude_patterns: List[str] = None) -> bool:
        """Utility to check if a file or directory should be ignored."""
        exclude = exclude_patterns or [
            "node_modules", "vendor", ".git", ".venv", "venv", "__pycache__", "dist", "build"
        ]
        path_str = str(path).replace("\\", "/")
        return any(pattern in path_str for pattern in exclude)
