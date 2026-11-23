# Universal Docker Deployment Guide

VulScanAgent is engineered to run seamlessly across **any operating system**:
- **Windows**: Docker Desktop (WSL2 or Hyper-V backend)
- **macOS**: Apple Silicon (M1/M2/M3/M4 ARM64) or Intel (x86_64) via Docker Desktop, OrbStack, or Colima
- **Linux**: Ubuntu, Debian, CentOS, RHEL, Fedora, Arch Linux (native Docker daemon)

---

## ⚡ Option 1: One-Click Launch (Recommended)

### On Windows (PowerShell)
```powershell
.\docker-run.ps1
```

### On Linux or macOS (Terminal)
```bash
chmod +x docker-run.sh
./docker-run.sh
```

This automatically:
1. Verifies your Docker engine.
2. Creates `.env` from template if missing.
3. Builds the multi-platform image.
4. Starts the background service and opens port `8000`.

Open **[http://localhost:8000](http://localhost:8000)** in any browser.

---

## 🐳 Option 2: Docker Compose Commands

### Start the Dashboard in Background
```bash
docker compose up -d --build
```

### View Live Streaming Logs
```bash
docker compose logs -f
```

### Stop the Agent
```bash
docker compose down
```

---

## 💻 Option 3: Run Headless CLI Scans Inside Docker

You can run direct CLI scans without starting the web dashboard:

### Scan a Remote GitHub Repository
```bash
docker compose run --rm vulscan-agent scan \
  --repo https://github.com/org/repo \
  --branch main \
  --severity HIGH
```

### Scan a Local Folder from Your Host Machine
Mount your host source code directory into `/workspace` inside the container:

#### On Linux / macOS:
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/my-project:/workspace \
  vulscan-agent:latest scan --local /workspace --severity MEDIUM
```

#### On Windows (PowerShell):
```powershell
docker run --rm `
  --env-file .env `
  -v ${PWD}/my-project:/workspace `
  vulscan-agent:latest scan --local /workspace --severity MEDIUM
```

### Verify Credentials Inside Container
```bash
docker compose run --rm vulscan-agent verify-keys
```

---

## 🔧 Option 4: Standalone `docker build` & `docker run` (No Compose)

### 1. Build the Image
```bash
docker build -t vulscan-agent:latest .
```

### 2. Run the Container
```bash
# Web Dashboard:
docker run -d \
  --name vulscan-agent \
  -p 8000:8000 \
  --env-file .env \
  vulscan-agent:latest

# Or CLI Scan directly:
docker run --rm \
  --env-file .env \
  vulscan-agent:latest scan --repo https://github.com/org/repo --severity HIGH
```

---

## ⚙️ Environment Variables Reference for Docker

You can pass environment variables in three ways:

1. **Via `.env` file** (easiest):
   ```env
   GITHUB_TOKEN=ghp_...
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GEMINI_API_KEY=AIzaSy...
   AI_PROVIDER=auto
   ```

2. **Inline via `-e` flag**:
   ```bash
   docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." -e GITHUB_TOKEN="ghp_..." vulscan-agent:latest
   ```

3. **Inherited from host environment**:
   If already exported in your terminal (`export GITHUB_TOKEN=...`), Docker Compose automatically inherits them!

---

## 🛡️ Container Security Guarantees
- **No-new-privileges**: Prevents privilege escalation inside the container.
- **Isolated Network & Filesystem**: Scanned code and test execution cannot escape the container.
- **Resource Limits**: Configurable in `docker-compose.yml` to prevent runaway CPU or memory usage.
