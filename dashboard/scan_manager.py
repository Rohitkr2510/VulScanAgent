import uuid
import threading
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from config.config_loader import AppConfig
from agent.orchestrator import VulScanOrchestrator
from agent.models import VulnerabilitySeverity

logger = logging.getLogger(__name__)


class ScanJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    repo_url: str
    branch: str = "main"
    severity_threshold: VulnerabilitySeverity = VulnerabilitySeverity.MEDIUM
    provider: str = "auto"
    status: str = "QUEUED"  # QUEUED, RUNNING, COMPLETED, FAILED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    findings_count: int = 0
    fixed_count: int = 0
    prs: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)


class ScanManager:
    """Thread-safe manager for background scanning jobs."""

    def __init__(self, base_config_path: str = "config/config.yaml"):
        self.base_config_path = base_config_path
        self.jobs: Dict[str, ScanJob] = {}
        self._lock = threading.Lock()

    def get_all_jobs(self) -> List[ScanJob]:
        with self._lock:
            # Sort newest first
            return sorted(self.jobs.values(), key=lambda j: j.created_at, reverse=True)

    def get_job(self, job_id: str) -> Optional[ScanJob]:
        with self._lock:
            return self.jobs.get(job_id)

    def create_job(
        self,
        repo_url: str,
        branch: str = "main",
        severity: str = "MEDIUM",
        provider: str = "auto",
        local_dir: Optional[str] = None
    ) -> ScanJob:
        sev_enum = VulnerabilitySeverity(severity.upper())
        job = ScanJob(
            repo_url=repo_url,
            branch=branch,
            severity_threshold=sev_enum,
            provider=provider
        )

        with self._lock:
            self.jobs[job.id] = job

        # Launch execution in a background daemon thread
        thread = threading.Thread(
            target=self._run_job_worker,
            args=(job.id, local_dir),
            daemon=True
        )
        thread.start()
        return job

    def _run_job_worker(self, job_id: str, local_dir: Optional[str] = None) -> None:
        job = self.get_job(job_id)
        if not job:
            return

        with self._lock:
            job.status = "RUNNING"
            job.started_at = datetime.now(timezone.utc)
            job.logs.append(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Job started for {job.repo_url}")

        try:
            # Load and configure orchestrator
            config = AppConfig.from_yaml(self.base_config_path)
            config.repo.url = job.repo_url
            config.repo.branch = job.branch
            config.scanning.severity_threshold = job.severity_threshold
            if job.provider and job.provider != "auto":
                config.ai.provider = job.provider

            orchestrator = VulScanOrchestrator(config)
            local_path = Path(local_dir) if local_dir else None

            result = orchestrator.run(local_repo_override=local_path)

            with self._lock:
                job.status = "COMPLETED"
                job.completed_at = datetime.now(timezone.utc)
                job.findings_count = result.get("findings", 0)
                job.fixed_count = result.get("fixed", 0)
                job.prs = result.get("prs", [])
                job.logs.append(
                    f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Completed: "
                    f"Found {job.findings_count}, Remediated {job.fixed_count}, PRs: {len(job.prs)}"
                )

        except Exception as e:
            logger.error(f"Scan job {job_id} failed: {e}", exc_info=True)
            with self._lock:
                job.status = "FAILED"
                job.completed_at = datetime.now(timezone.utc)
                job.error = str(e)
                job.logs.append(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] Error: {str(e)}")
