import os
import hmac
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, BackgroundTasks, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from dashboard.scan_manager import ScanManager

app = FastAPI(
    title="VulScanAgent Dashboard",
    description="Autonomous Vulnerability Scanning & Remediation Management Dashboard",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
manager = ScanManager()


class TriggerScanRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    severity: str = "MEDIUM"
    provider: str = "auto"


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard visual overview."""
    jobs = manager.get_all_jobs()
    total_scans = len(jobs)
    total_findings = sum(j.findings_count for j in jobs)
    total_fixed = sum(j.fixed_count for j in jobs)
    total_prs = sum(len(j.prs) for j in jobs)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "jobs": jobs,
            "stats": {
                "total_scans": total_scans,
                "total_findings": total_findings,
                "total_fixed": total_fixed,
                "total_prs": total_prs,
            }
        }
    )


@app.post("/scan/trigger")
async def trigger_scan_form(
    repo_url: str = Form(...),
    branch: str = Form("main"),
    severity: str = Form("MEDIUM"),
    provider: str = Form("auto")
):
    """Trigger a new scan from the HTML form."""
    job = manager.create_job(
        repo_url=repo_url.strip(),
        branch=branch.strip(),
        severity=severity.strip(),
        provider=provider.strip()
    )
    return JSONResponse(status_code=202, content={"job_id": job.id, "status": job.status})


@app.get("/api/jobs")
async def get_all_jobs_api():
    """Returns JSON list of all scanning jobs."""
    jobs = manager.get_all_jobs()
    return [j.model_dump() for j in jobs]


@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Returns detailed status and logs for a specific scan job."""
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.model_dump()


@app.post("/api/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    GitHub Webhook receiver for 'push' and 'pull_request' events.
    Verifies HMAC-SHA256 signature when GITHUB_WEBHOOK_SECRET is set.
    """
    raw_body = await request.body()
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")

    # Production-grade cryptographic signature verification (RFC 2104 / GitHub Webhook standard)
    if webhook_secret:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header")

        expected_sig = "sha256=" + hmac.new(
            webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, x_hub_signature_256):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    import json
    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    logger_event = x_github_event or "unknown"

    if logger_event == "ping":
        return {"status": "pong", "message": "GitHub Webhook registered successfully"}

    if logger_event in ["push", "pull_request"]:
        repo_data = payload.get("repository", {})
        repo_url = repo_data.get("clone_url") or repo_data.get("html_url")
        ref = payload.get("ref", "refs/heads/main")
        branch = ref.split("/")[-1] if "/" in ref else "main"

        if repo_url:
            job = manager.create_job(
                repo_url=repo_url,
                branch=branch,
                severity="MEDIUM",
                provider="auto"
            )
            return {
                "status": "triggered",
                "job_id": job.id,
                "event": logger_event,
                "repository": repo_url,
                "branch": branch
            }

    return {"status": "ignored", "event": logger_event}
