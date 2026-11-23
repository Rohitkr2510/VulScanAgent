# 🚀 Production Release & Distribution Guide

> **Official Guide**: How to release, publish, and distribute **VulScanAgent** across GitHub Releases, GitHub Container Registry (GHCR), GitHub Marketplace Actions, PyPI, and Docker Hub.

---

## 📦 Distribution Channels Overview

VulScanAgent is configured for 5 ready-to-use distribution channels:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. GitHub Action (@v1)          -> Plug-and-play into any repository's CI/CD workflow │
│ 2. Docker Container (GHCR)      -> Run anywhere with 0 setup (macOS/Linux/Windows)     │
│ 3. Python Package (pip)         -> Global `vulscan` CLI command on developer machines   │
│ 4. GitHub Release (v1.0.0)      -> Official release notes, assets, and source tarballs │
│ 5. Self-Hosted Web Dashboard    -> 24/7 FastAPI server with HMAC GitHub webhook daemon │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Step-by-Step: Releasing Version 1.0.0

### Step 1: Pre-Release Quality Verification

Before tagging a release, ensure all 33 unit tests pass:

```bash
pytest -v
```

### Step 2: Tag & Push Semantic Version

Creating and pushing a Git tag automatically triggers the automated release pipeline in `.github/workflows/release.yml`:

```bash
# 1. Ensure you are on the main branch and up to date
git checkout main
git pull origin main

# 2. Create the annotated release tag
git tag -a v1.0.0 -m "Release v1.0.0: Autonomous AI DevSecOps Security Engineer"

# 3. Push the tag to GitHub
git push origin v1.0.0
```

### Step 3: What Happens Automatically

When you push `v1.0.0`, GitHub Actions executes `.github/workflows/release.yml`:
1. **Test Gate**: Runs the full 33-test suite on Ubuntu.
2. **Docker Publish**: Builds the production Docker image and publishes it to **GitHub Container Registry (GHCR)**:
   - `ghcr.io/rohitkr2510/vulscanagent:v1.0.0`
   - `ghcr.io/rohitkr2510/vulscanagent:latest`
3. **GitHub Release**: Creates the official GitHub Release with changelogs, markdown reports, and binary download links.

---

## 👥 How End-Users Run Your Ready-to-Use Agent

Once released, developers can run VulScanAgent in 4 different ways:

### 1. As a GitHub Action (Zero Installation)
Any developer can add VulScanAgent to their repository by adding `.github/workflows/security.yml`:

```yaml
name: Autonomous Security Audit
on:
  push:
    branches: [main]
  pull_request:

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

### 2. Via Docker (Zero Dependencies)
Users without Python installed can run the container directly:

```bash
# Scan a remote GitHub repo
docker run --rm \
  -e GEMINI_API_KEY="AIzaSy..." \
  -e GITHUB_TOKEN="ghp_..." \
  ghcr.io/rohitkr2510/vulscanagent:latest scan --repo https://github.com/org/repo

# Or scan local directory mounted as volume
docker run --rm -v $(pwd):/workspace \
  -e GEMINI_API_KEY="AIzaSy..." \
  ghcr.io/rohitkr2510/vulscanagent:latest scan --local /workspace
```

### 3. As a CLI Tool via pip
Users can install VulScanAgent globally via pip:

```bash
# Direct install from GitHub
pip install git+https://github.com/Rohitkr2510/VulScanAgent.git

# Verify CLI
vulscan --help

# Run scan
vulscan scan --repo https://github.com/Rohitkr2510/face-recognition-devops
```

### 4. Running the 24/7 Web Dashboard & Webhook Server
For teams hosting their own internal security service:

```bash
docker compose up -d
# Dashboard available at http://localhost:8000
```

---

## 🏷️ Publishing to the GitHub Actions Marketplace

To make VulScanAgent searchable in the official [GitHub Marketplace](https://github.com/marketplace?type=actions):

1. Navigate to your repository on GitHub: `https://github.com/Rohitkr2510/VulScanAgent`.
2. Click the **Releases** tab on the right sidebar.
3. Click **Draft a new release**.
4. Check the box: **"Publish this Action to the GitHub Marketplace"**.
5. Select the primary category (**Security**) and secondary category (**Continuous Integration**).
6. Set the tag to `v1.0.0`.
7. Click **Publish release**.

---

## 📦 Optional: Publishing to PyPI (`pip install vulscanagent`)

To publish to the official Python Package Index (PyPI):

```bash
# 1. Install build tools
pip install build twine

# 2. Build wheel and source archive
python -m build

# 3. Upload to PyPI (requires PyPI API Token)
twine upload dist/*
```
Once uploaded, anyone in the world can run:
```bash
pip install vulscanagent
vulscan scan --repo <url>
```
