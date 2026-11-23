import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent.models import VulnerabilitySeverity

load_dotenv()


class RepoSettings(BaseModel):
    url: str
    branch: str = "main"
    token_env: str = "GITHUB_TOKEN"
    clone_depth: int = 1

    @property
    def token(self) -> Optional[str]:
        return os.getenv(self.token_env) or os.getenv("GITHUB_TOKEN")


class AISettings(BaseModel):
    provider: str = "auto"
    fallback_order: List[str] = Field(default_factory=lambda: ["anthropic", "openai", "google"])
    max_fix_retries: int = 3
    temperature: float = 0.1
    models: Dict[str, str] = Field(
        default_factory=lambda: {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        }
    )


class ScanningSettings(BaseModel):
    severity_threshold: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    scanners: List[str] = Field(default_factory=lambda: ["sast", "secrets", "sca", "iac"])
    exclude_paths: List[str] = Field(
        default_factory=lambda: ["node_modules/**", "vendor/**", ".git/**", "*.min.js"]
    )


class TestingSettings(BaseModel):
    timeout_seconds: int = 180
    require_pass: bool = True
    generate_ai_tests: bool = True
    custom_test_cmd: str = ""


class PRSettings(BaseModel):
    draft: bool = False
    reviewers: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=lambda: ["security", "vulscan-agent", "automated-fix"])
    one_pr_per_vuln: bool = False
    title_prefix: str = "[VulScanAgent]"


class AppConfig(BaseModel):
    repo: RepoSettings
    ai: AISettings = Field(default_factory=AISettings)
    scanning: ScanningSettings = Field(default_factory=ScanningSettings)
    testing: TestingSettings = Field(default_factory=TestingSettings)
    pr: PRSettings = Field(default_factory=PRSettings)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "AppConfig":
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        config = cls(**data)

        # Environment variable overrides
        if os.getenv("AI_PROVIDER"):
            config.ai.provider = os.getenv("AI_PROVIDER")

        return config
