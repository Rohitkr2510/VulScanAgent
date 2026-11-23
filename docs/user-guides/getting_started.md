# Getting Started with VulScanAgent

## 1. Prerequisites

- **Python**: 3.11 or 3.12+
- **Git**: 2.30+ installed and on system PATH
- **GitHub Token**: Personal Access Token (classic or fine-grained) with `repo` scope
- **AI Provider API Key**: At least one of the following:
  - OpenAI (`OPENAI_API_KEY`)
  - Anthropic (`ANTHROPIC_API_KEY`)
  - Google Gemini (`GEMINI_API_KEY` or `GOOGLE_API_KEY`)

---

## 2. Installation

### 2.1 Clone Repository
```bash
git clone https://github.com/your-org/VulScanAgent.git
cd VulScanAgent
```

### 2.2 Create Virtual Environment
```bash
# On Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Environment Configuration

Copy the example environment template:
```bash
cp .env.example .env
```

Configure your `.env` file:
```env
# GitHub Personal Access Token for repo operations & PR generation
GITHUB_TOKEN=ghp_your_github_token_here

# AI Provider API Keys (at least one is required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...

# Provider choice: auto | anthropic | openai | google
AI_PROVIDER=auto
```

---

## 4. Verification

Run the built-in key verification check:
```bash
python main.py verify-keys
```

Expected output:
```
🔑 Checking API Keys and Connectivity

GitHub Token: Found
Available AI Providers: anthropic, openai, google
Ready to remediate code!
```

---

## 5. Your First Scan

### Scan a Local Repository
```bash
python main.py scan --local ./samples/demo_repo --severity MEDIUM
```

### Scan a Remote GitHub Repository
```bash
python main.py scan --repo https://github.com/org/repo --branch main --severity HIGH
```

### Launch the Web Dashboard
```bash
python main.py dashboard --port 8000
```
Open [http://localhost:8000](http://localhost:8000) to view active scan activity and trigger scans visually.
