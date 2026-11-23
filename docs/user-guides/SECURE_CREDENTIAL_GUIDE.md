# 🔐 Secure Credential Management & Zero-Trust Best Practices

> **Production Security Standard**: How end-users and organizations securely provide API keys to **VulScanAgent** without exposing credentials in code, terminal history, CI/CD logs, or Docker process tables.

---

## 🛡️ Core Principles: Zero Trust Credential Architecture

VulScanAgent follows three non-negotiable security mandates:
1. **Never Hardcode Secrets**: No API keys are ever embedded in source files, docker images, or repositories.
2. **Zero Shell History Exposure**: Sensitive keys must never be typed as raw command-line flags (`--api-key=...`) where they would be saved in `~/.bash_history`, `~/.zsh_history`, or PowerShell logs.
3. **In-Memory Volatility**: Credentials are read into memory at runtime and masked with automated redaction filters (`***REDACTED***`).

---

## ⚡ Method 1: Interactive Masked Configuration (`vulscan configure`)
*Recommended for local developer workstations and laptop environments.*

Similar to `aws configure` or `gh auth login`, users configure their credentials interactively:

```bash
vulscan configure
```

```text
🔐 VulScanAgent Secure Credential Configuration
Keystrokes are masked (*), omitted from shell history, and stored in restricted user profile (600).

Google Gemini API Key (Enter to keep/skip): ********
Anthropic Claude API Key (Optional): ********
OpenAI API Key (Optional): ********
GitHub Token (Optional for PR creation): ********

✅ Credentials securely saved to: ~/.vulscan/credentials.env
[Permissions set to 600: Owner read/write only. Automatically loaded across all runs.]
```

### Why this is secure:
- **Masked Input**: Typer/getpass hides character entry on screen.
- **Omitted from History**: The keys are never entered as command arguments, keeping shell history clean.
- **File System Isolation**: Saved to `~/.vulscan/credentials.env` with `chmod 600` (readable only by the local user account).

---

## ⚡ Method 2: Encrypted CI/CD Secrets (GitHub Actions)
*Recommended for automated repository security pipelines.*

In continuous integration environments, users **never write API keys in workflow YAML files**. Instead, they store them in GitHub Encrypted Secrets:

1. In the target GitHub repository, navigate to:  
   **Settings $\to$ Secrets and variables $\to$ Actions $\to$ New repository secret**.
2. Add secrets:
   - `GEMINI_API_KEY`: User's Google Gemini key.
   - `GH_TOKEN`: User's Personal Access Token.
3. In `.github/workflows/security.yml`, inject the secrets via environment variables:

```yaml
name: VulScanAgent Security Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run VulScanAgent
        uses: Rohitkr2510/VulScanAgent@v1
        with:
          provider: 'google'
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GH_TOKEN }}
```

### Why this is secure:
- GitHub encrypts secrets using **NaCl public-key cryptography** before storing them.
- GitHub Actions automatically masks secret values with `***` in all build logs.

---

## ⚡ Method 3: Secure Docker Injection (`--env-file`)
*Recommended for Docker containers and Kubernetes jobs.*

Avoid passing secrets via `-e GEMINI_API_KEY=xxx` because plain command arguments are visible in `docker ps` and process tables (`ps aux`).

Instead, pass an environment file or use Docker Secrets:

```bash
# Pass the restricted credentials file created by `vulscan configure`
docker run --rm \
  --env-file ~/.vulscan/credentials.env \
  -v $(pwd):/workspace \
  ghcr.io/rohitkr2510/vulscanagent:latest scan --local /workspace
```

---

## ⚡ Method 4: Ephemeral In-Memory Terminal Session
*Recommended for quick ad-hoc scans on shared servers.*

Set the environment variable directly in your active terminal session without writing anything to disk. The secret resides purely in process RAM and is completely wiped the moment you close the terminal window:

```bash
# Linux / macOS (Memory-only)
read -s GEMINI_API_KEY
export GEMINI_API_KEY

# Windows PowerShell (Memory-only)
$env:GEMINI_API_KEY = Read-Host -AsSecureString
```

---

## 🔍 How VulScanAgent Prevents Credential Leaks

1. **Automated Secret Redaction Shield ([`agent/security/guardrails.py`](../agent/security/guardrails.py))**:
   All text output, logs, audit reports, and Pull Request summaries pass through high-entropy regex sanitizers that automatically replace detected keys with `***REDACTED***`.
2. **Strict `.gitignore` Enforcement**:
   Local `.env` and `*.key` files are denied by default.
3. **No Centralized Telemetry**:
   VulScanAgent is 100% decentralized. It makes direct outbound calls to the provider API endpoints chosen by the user and never logs keys to external analytics.
