# Web Dashboard User Guide

## 1. Overview

**VulScanAgent Web Dashboard** is a modern, responsive web application built with FastAPI and Tailwind CSS. It enables security teams, developers, and DevOps engineers to visually manage, initiate, and monitor autonomous vulnerability scans and Pull Requests.

---

## 2. Launching the Dashboard

```bash
python main.py dashboard --host 127.0.0.1 --port 8000
```

Navigate to **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 3. Dashboard Features

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🛡️ VulScanAgent                       ● Engine Online                  │
├────────────────────────────────────────────────────────────────────────┤
│  [Total Scans: 12]  [Vulnerabilities: 47]  [Remediated: 39]  [PRs: 39] │
├────────────────────────────────────────────────────────────────────────┤
│ ⚡ Launch Autonomous Vulnerability Scan                                │
│ [ Repo URL: https://github.com/org/repo ] [ Branch: main ]             │
│ [ Severity: MEDIUM ▾ ] [ Provider: Auto ▾ ]  [   SCAN NOW   ]          │
├────────────────────────────────────────────────────────────────────────┤
│ 📋 Scan Activity & Pull Requests                       (Auto-refresh)  │
│ Job ID │ Repository      │ Branch │ Threshold │ Status    │ PR Link    │
│ 8a3f12 │ org/backend     │ main   │ HIGH      │ COMPLETED │ PR #14 🔗  │
│ b49e01 │ org/auth-svc    │ dev    │ CRITICAL  │ RUNNING   │ —          │
└────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Real-Time Metrics Row
- **Total Scans**: Cumulative number of scan jobs executed.
- **Vulnerabilities Found**: Aggregated findings across SAST, SCA, Secrets, and IaC.
- **Auto-Remediated**: Number of vulnerabilities successfully fixed and validated by test suites.
- **Pull Requests Raised**: Direct links to open GitHub PRs.

### 3.2 Trigger Scan Form
Submit any public or private GitHub repository URL:
- **Repository URL**: Git clone URL (e.g. `https://github.com/owner/repository`).
- **Branch**: Base branch to clone and target.
- **Minimum Severity**: Filter out low-priority findings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **AI Provider**: Choose `Auto` (cascading fallback), `Claude 3.5 Sonnet`, `OpenAI GPT-4o`, or `Google Gemini`.

### 3.3 Dynamic Scan Activity Table
- Polls automatically every 5 seconds without full page refreshes.
- Displays job execution state:
  - `QUEUED`: Awaiting background thread worker.
  - `RUNNING`: Actively scanning, repairing, or executing tests.
  - `COMPLETED`: Finished with all verified PRs created.
  - `FAILED`: Scan halted due to fatal network or authentication error.
- Direct clickable links to the generated GitHub Pull Requests.

---

## 4. REST API Endpoints

The dashboard exposes a programmatic REST API for integration:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard HTML view. |
| `POST` | `/scan/trigger` | Trigger a new scan job asynchronously. |
| `GET` | `/api/jobs` | Retrieve JSON list of all scan jobs and summaries. |
| `GET` | `/api/jobs/{job_id}` | Retrieve detailed status, logs, and findings for a specific job. |
| `POST` | `/api/webhook/github` | Webhook listener for GitHub `push` and `pull_request` events. |
