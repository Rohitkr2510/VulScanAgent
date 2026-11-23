# Configuration Specification (`config.yaml`)

The primary configuration file is located at `config/config.yaml`. It governs repository credentials, AI routing, scan rules, test behavior, and PR settings.

---

## 1. Schema Breakdown

```yaml
# Target repository configuration
repo:
  url: "https://github.com/example/sample-repo" # Remote GitHub repo URL
  branch: "main"                               # Base branch to clone and target
  token_env: "GITHUB_TOKEN"                     # Environment variable name containing PAT
  clone_depth: 1                               # Git clone depth (shallow clone)

# Multi-provider AI Fix Engine settings
ai:
  provider: "auto"                             # openai | anthropic | google | auto
  fallback_order:                              # Order of precedence when provider is 'auto'
    - "anthropic"
    - "openai"
    - "google"
  max_fix_retries: 3                           # Maximum retry loops per vulnerability
  temperature: 0.1                             # Deterministic temperature for code generation
  models:
    openai: "gpt-4o"
    anthropic: "claude-3-5-sonnet-20241022"
    google: "gemini-2.5-pro"

# Scanner suite parameters
scanning:
  severity_threshold: "MEDIUM"                 # LOW | MEDIUM | HIGH | CRITICAL
  scanners:
    - "sast"                                   # Static code analysis
    - "secrets"                                # Credential & API key detection
    - "sca"                                    # Dependency vulnerability audit
    - "iac"                                    # Dockerfile & workflow security
  exclude_paths:
    - "node_modules/**"
    - "vendor/**"
    - ".git/**"
    - "*.min.js"
    - "dist/**"
    - "build/**"

# Verification & test execution
testing:
  timeout_seconds: 180                         # Subprocess timeout limit per test run
  require_pass: true                           # If true, PR is created only when tests pass
  generate_ai_tests: true                      # Auto-synthesize targeted regression tests
  custom_test_cmd: ""                          # Optional override for test command (e.g. 'pytest tests/security')

# Pull Request options
pr:
  draft: false                                 # Create PRs as draft PRs
  reviewers:                                   # GitHub usernames/teams to request reviews from
    - "security-team"
    - "lead-architect"
  labels:                                      # GitHub labels to attach to PR
    - "security"
    - "vulscan-agent"
    - "automated-fix"
  one_pr_per_vuln: false                       # false = batch fixes per run into single PR
  title_prefix: "[VulScanAgent]"
```

---

## 2. Environment Variable Overrides

Configuration parameters can be overridden at runtime via environment variables:

| Environment Variable | Config Path Overridden |
|---|---|
| `AI_PROVIDER` | `ai.provider` |
| `GITHUB_TOKEN` | `repo.token` |
| `OPENAI_API_KEY` | OpenAI client auth |
| `ANTHROPIC_API_KEY` | Anthropic client auth |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google Gemini client auth |
