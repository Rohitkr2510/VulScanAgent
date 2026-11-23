## 🛡️ VulScanAgent v1.0.0 Production Release

**Autonomous AI DevSecOps Security Engineer**: Scans codebases for vulnerabilities, performs context-aware AST remediation using Google Gemini, Anthropic Claude, or OpenAI, validates fixes with automated testing, and raises structured Pull Requests for human review.

---

### 🚀 Quickstart Usage Options

#### Option 1: Docker Container (No Installation Needed)
```bash
# Run with environment file (recommended)
docker run --rm \
  --env-file ~/.vulscan/credentials.env \
  -v $(pwd):/workspace \
  ghcr.io/rohitkr2510/vulscanagent:latest scan --local /workspace
```

#### Option 2: Python / PyPI CLI
```bash
# Install globally
pip install git+https://github.com/Rohitkr2510/VulScanAgent.git@v1.0.0

# Configure credentials interactively (masked input)
vulscan configure

# Run scan
vulscan scan --repo https://github.com/org/repo
```

#### Option 3: Native GitHub Action
Add to `.github/workflows/security.yml`:
```yaml
name: Autonomous Security Audit
on: [push, pull_request]

jobs:
  vulscan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run VulScanAgent
        uses: Rohitkr2510/VulScanAgent@v1
        with:
          provider: 'google'
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
          severity: 'MEDIUM'
```

---

### 📊 Benchmark Scorecard Highlights
- **Target Benchmark**: `Rohitkr2510/face-recognition-devops`
- **Detection Precision**: **100.0%** (via Adversarial `CandidateVerifier`)
- **Remediation Rate**: **100% (2 / 2 fixed)**
- **Regression Rate**: **0% (5 / 5 unit tests passed)**
- **Cloudflare Audit Artifacts**: `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md`, `architecture.md`, `coverage-ledger.json`
