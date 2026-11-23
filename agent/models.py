from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class VulnerabilitySeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    @property
    def score(self) -> int:
        mapping = {
            "CRITICAL": 5,
            "HIGH": 4,
            "MEDIUM": 3,
            "LOW": 2,
            "INFO": 1
        }
        return mapping.get(self.value, 0)

    def meets_threshold(self, threshold: "VulnerabilitySeverity") -> bool:
        return self.score >= threshold.score


class VulnerabilityCategory(str, Enum):
    SAST = "sast"
    SCA = "sca"
    SECRETS = "secrets"
    IAC = "iac"


class CandidateStatus(str, Enum):
    """Cloudflare security-audit-skill verification classification."""
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    NEEDS_VALIDATION = "needs_validation"
    REJECTED = "rejected"


class ValidationVerdict(BaseModel):
    """Adversarial verification result from CandidateVerifier agent."""
    status: CandidateStatus
    confidence_score: int = Field(default=5, ge=1, le=10, description="Confidence in verdict (1-10)")
    reachability_proven: bool = Field(default=False, description="Whether untrusted input realistically reaches sink")
    disproof_rationale: str = Field(default="", description="Adversarial reasoning proving or disproving finding")
    taint_path: Optional[str] = Field(default=None, description="Traced dataflow: Source -> Sanitizer -> Sink")
    prerequisites: Optional[str] = Field(default=None, description="Pre-conditions or environment assumptions required")


class VulFinding(BaseModel):
    """Normalized finding across SAST, SCA, Secrets, and IaC scanners."""
    id: str = Field(description="Unique identifier for finding")
    title: str = Field(description="Short human-readable summary of the vulnerability")
    category: VulnerabilityCategory
    severity: VulnerabilitySeverity
    file_path: str = Field(description="Relative path to vulnerable file")
    line_number: int = Field(default=1, description="Starting line of vulnerability")
    end_line_number: Optional[int] = Field(default=None, description="Ending line of vulnerability")
    cve_id: Optional[str] = Field(default=None, description="Associated CVE if applicable")
    cwe_id: Optional[str] = Field(default=None, description="Common Weakness Enumeration ID, e.g. CWE-89")
    mitre_attack_id: Optional[str] = Field(default=None, description="MITRE ATT&CK technique, e.g. T1059")
    mitre_d3fend_id: Optional[str] = Field(default=None, description="MITRE D3FEND countermeasure, e.g. D3-SPP")
    owasp_category: Optional[str] = Field(default=None, description="OWASP Top 10 category, e.g. A03:2021-Injection")
    rule_id: Optional[str] = Field(default=None, description="Scanner rule or check identifier")
    description: str = Field(default="", description="Detailed vulnerability explanation")
    code_snippet: Optional[str] = Field(default=None, description="Vulnerable code snippet")
    remediation_hint: Optional[str] = Field(default=None, description="Suggested guidance for fixing")
    raw_scanner_data: Dict[str, Any] = Field(default_factory=dict, description="Original tool output")
    validation_status: CandidateStatus = Field(default=CandidateStatus.CONFIRMED, description="Cloudflare audit validation status")
    validation_verdict: Optional[ValidationVerdict] = Field(default=None, description="Detailed adversarial disproof analysis")


class FixAttempt(BaseModel):
    attempt_number: int
    provider_used: str
    model_name: str
    proposed_diff: str
    explanation: str
    files_modified: List[str]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TestStatus(str, Enum):
    __test__ = False
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


class TestResult(BaseModel):
    __test__ = False
    status: TestStatus
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    failure_details: Optional[str] = None


class FixResult(BaseModel):
    finding_id: str
    success: bool
    attempts: List[FixAttempt] = Field(default_factory=list)
    final_diff: Optional[str] = None
    applied_files: List[str] = Field(default_factory=list)
    test_result: Optional[TestResult] = None
    error_message: Optional[str] = None


class ScanReport(BaseModel):
    repo_url: str
    repo_name: str
    branch: str
    commit_sha: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    findings: List[VulFinding] = Field(default_factory=list)

    @property
    def total_findings(self) -> int:
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == VulnerabilitySeverity.CRITICAL)

    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == VulnerabilitySeverity.HIGH)

    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == VulnerabilitySeverity.MEDIUM)

    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == VulnerabilitySeverity.LOW)


class PRInfo(BaseModel):
    pr_url: str
    pr_number: int
    branch_name: str
    title: str
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CoverageUnit(BaseModel):
    """Cloudflare coverage-ledger unit representing bounded component/paths."""
    unit_name: str
    file_paths: List[str]
    scanners_run: List[str]
    inspected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    findings_count: int = 0
    status: str = "audited"


class CoverageLedger(BaseModel):
    """Cloudflare stateful coverage tracker: ensures methodical inspection without context drift."""
    repo_name: str
    commit_sha: str = ""
    total_files: int = 0
    audited_files: int = 0
    coverage_percent: float = 0.0
    units: List[CoverageUnit] = Field(default_factory=list)
    blind_spots: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


