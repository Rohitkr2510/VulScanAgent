# VulScanAgent 🛡️

> **Autonomous AI Security Engineer**: Scans codebases for vulnerabilities, performs intelligent context-aware remediation using OpenAI / Claude / Gemini, validates fixes with automated testing, and raises structured Pull Requests for human review.

---

## ✨ Features

- 🔍 **Multi-Layer Vulnerability Scanning**:
  - **SAST**: SQL Injection, Command Injection, Path Traversal, Dangerous Eval, XSS (Semgrep + built-in AST engine).
  - **Secrets**: API keys (AWS, GitHub, OpenAI), private keys, passwords, database URLs.
  - **SCA**: Vulnerable package manifests (`requirements.txt`, `package.json`, CVE tracking).
  - **IaC & CI/CD**: Container root executions, unpinned image tags, dangerous `pull_request_target` workflows.
- 🤖 **Multi-Provider AI Fix Engine**:
  - Seamlessly route between **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5 Sonnet)**, and **Google (Gemini 2.5 Pro)**.
  - Automatic fallback cascading if one provider hits rate limits or quota errors.
  - Syntax AST pre-validation prevents broken code generation.
- 🧪 **Safety-Gated Test Verification**:
  - Runs repo test suites (`pytest`, `npm test`, `go test`, `mvn test`) before and after applying fixes.
  - Automatic retry feedback loop: if a fix fails tests, error logs are passed back to the LLM to adjust the fix.
  - Automatically synthesizes targeted regression tests for the remediated vulnerability.
- 🚀 **GitHub Pull Request Automation**:
  - Handles **public and private** repositories via Fine-Grained Personal Access Tokens.
  - Creates isolated branches (`fix/vuln-<id>`).
  - Generates comprehensive PR descriptions with CVE references, root-cause analysis, and human reviewer checklists.

---

## 👥 Multi-Agent Collaborative Architecture

Inspired by advanced agentic workflows (e.g. [salah9003/Automated-Vulnerability-Scanning-with-Agentic-AI](https://github.com/salah9003/Automated-Vulnerability-Scanning-with-Agentic-AI)), **VulScanAgent** operates as a specialized multi-agent security team rather than a single generalist prompt:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VulScanAgent Team                               │
│                                                                        │
│   🎯 ScanStrategist        Inspects repository stack & sets priorities │
│          │                                                             │
│          ▼                                                             │
│   🔍 Multi-Layer Scanner   Executes SAST, SCA, Secrets, IaC engines    │
│          │                                                             │
│          ▼                                                             │
│   🛠️ FixArchitect          Crafts surgical, non-breaking patch        │
│          │                                                             │
│          ▼                                                             │
│   🧐 SecurityReviewer      Critiques patch & checks for regressions   │
│          │                                                             │
│          ▼                                                             │
│   🧪 TestVerifier          Executes test suite & generates tests       │
│          │                                                             │
│          ├── (On Test Failures) ──► 🩺 ErrorDiagnostician              │
│          │                         (Diagnoses errors & guides fix)     │
│          ▼ (On Test Pass)                                              │
│   📝 PRAuditor             Compiles audit documentation & raises PR    │
└────────────────────────────────────────────────────────────────────────┘
```

| Agent Persona | Role | Responsibility |
|---|---|---|
| **`ScanStrategist`** | Recon & Planning | Inspects repo topology, manifests (`package.json`, `requirements.txt`, `Dockerfile`) and optimizes scanning rules. |
| **`FixArchitect`** | Remediation | Synthesizes minimal code patches preserving coding style and business logic. |
| **`SecurityReviewer`** | Senior Critic | Rigorously critiques proposed patches before application; prevents secondary vulnerabilities. |
| **`ErrorDiagnostician`** | Failure Specialist | When tests or compilation fail, parses tracebacks and provides actionable fix prescriptions. |
| **`TestVerifier`** | Verification | Coordinates test execution, monitors timeouts, and synthesizes targeted regression tests. |
| **`PRAuditor`** | Technical Writer | Compiles executive security summaries, reviewer checklists, and GitHub Pull Request documentation. |

---

## 🏗️ Architecture

```
                 ┌─────────────────────────────────┐
                 │       User / CLI / Webhook      │
                 └────────────────┬────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │     VulScan Orchestrator     │
                   └──────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Repo Connector  │    │ Multi-Scanner    │    │   Test Runner    │
│  (Clone / Branch)│    │ (SAST/SCA/IaC)   │    │  (pytest / npm)  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │      AI Fix Engine           │
                   │ (OpenAI / Claude / Gemini)   │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │    GitHub PR Creator         │
                   └──────────────────────────────┘
```

---

## 🚀 Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/VulScanAgent.git
cd VulScanAgent

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and insert your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```env
# GitHub token for repository operations & PR creation
GITHUB_TOKEN=ghp_your_github_token_here

# At least one AI provider key is required:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...

# Default provider choice: auto | anthropic | openai | google
AI_PROVIDER=auto
```

### 3. Verify Configuration

```bash
python main.py verify-keys
```

---

## 💻 CLI & Web Dashboard Usage

### Launch Interactive Web Dashboard & Webhooks

```bash
python main.py dashboard --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to view the real-time scanning dashboard, monitor active jobs, inspect vulnerabilities, and launch new scans directly from your browser.

#### GitHub Webhooks
Configure your GitHub repository webhook to:
- **Payload URL**: `http://<your-server>:8000/api/webhook/github`
- **Content type**: `application/json`
- **Events**: `push`, `pull_request`

### Scan a Remote Repository (Public or Private)

```bash
python main.py scan --repo https://github.com/org/private-repo --branch main --severity HIGH
```

### Scan and Test a Local Directory

```bash
python main.py scan --local ./my-project --severity MEDIUM
```

---

## 🐳 Docker Sandboxing

Run VulScanAgent in an isolated container to ensure tests and scanners never access your host environment:

```bash
# Build and start via Docker Compose
docker compose up -d

# View dashboard logs
docker compose logs -f
```

The web dashboard is instantly available at [http://localhost:8000](http://localhost:8000).

---

## 🤖 GitHub Actions CI/CD Integration

VulScanAgent includes a ready-to-use GitHub Action workflow in [`.github/workflows/vulscan.yml`](.github/workflows/vulscan.yml).

To enable automated scanning on every `push` and `pull_request`:
1. Add the workflow file to your repository.
2. In GitHub **Settings > Secrets and variables > Actions**, add your API keys:
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `GEMINI_API_KEY`
   - `GITHUB_TOKEN` is automatically provided by GitHub Actions!

### Select Specific AI Provider

```bash
# Force Claude
python main.py scan --repo https://github.com/example/repo --provider anthropic

# Force Gemini
python main.py scan --repo https://github.com/example/repo --provider google

# Force OpenAI
python main.py scan --repo https://github.com/example/repo --provider openai
```

---

## ⚙️ Configuration (`config/config.yaml`)

Customize rules, thresholds, and behavior:

```yaml
repo:
  url: "https://github.com/org/repo"
  branch: "main"
  token_env: "GITHUB_TOKEN"

ai:
  provider: "auto"
  fallback_order: ["anthropic", "openai", "google"]
  max_fix_retries: 3
  temperature: 0.1

scanning:
  severity_threshold: "MEDIUM"  # LOW | MEDIUM | HIGH | CRITICAL
  scanners: ["sast", "secrets", "sca", "iac"]
  exclude_paths: ["node_modules/**", "vendor/**", ".git/**"]

testing:
  timeout_seconds: 180
  require_pass: true
  generate_ai_tests: true

pr:
  draft: false
  reviewers: ["security-team"]
  labels: ["security", "vulscan-agent"]
```

---

## 🧪 Running Unit Tests

Run VulScanAgent's own test suite:

```bash
pytest -v
```

---

## 🛡️ Security Guarantees

- **No Blind Auto-Merges**: Human security approval is strictly required for every PR.
- **Surgical Code Modifications**: The agent only changes code directly related to the vulnerability and preserves existing business logic.
- **AST Pre-validation**: Code with syntax errors is rejected before testing or committing.
- **Credential Masking**: Detected secrets are never exposed unmasked in PR descriptions.
