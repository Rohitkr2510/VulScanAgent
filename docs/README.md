# VulScanAgent Production Documentation

Welcome to the **VulScanAgent** technical documentation. This documentation repository is structured to support security engineers, developers, DevOps practitioners, and enterprise architects.

---

## 📚 Documentation Sitemap

### 🏛️ Architecture & System Design
- [Architecture Overview](architecture/overview.md) — High-level system design, data flow diagrams, and core subsystems.
- [Multi-Agent Collaborative Framework](architecture/multi_agent_framework.md) — Division of labor across `ScanStrategist`, `FixArchitect`, `SecurityReviewer`, `ErrorDiagnostician`, `TestVerifier`, and `PRAuditor`.
- [Threat Model & Security Boundaries](architecture/threat_model.md) — Sandboxing, AST validation, privilege boundaries, and secret protection.
- [AI Agent Threat Model & Runtime Controls](architecture/agent_threat_model.md) — STRIDE and OWASP Agentic Top 10 threat model & guardrail architecture.
- [Production Security Standards & Framework Mappings](architecture/standards_compliance.md) — Compliance mapping to MITRE ATT&CK, MITRE D3FEND, CWE, OWASP Top 10, and OWASP LLM Top 10.

### 📖 User Guides
- [Getting Started](user-guides/getting_started.md) — Prerequisites, environment variables, and initial setup.
- [CLI Command Reference](user-guides/cli_reference.md) — Comprehensive guide to flags and parameters for `scan`, `dashboard`, and `verify-keys`.
- [Web Dashboard Guide](user-guides/web_dashboard.md) — Using the real-time FastAPI dashboard and monitoring active PRs.

### 🔌 Integrations & Workflows
- [GitHub Integration](integration/github_integration.md) — Configuring Personal Access Tokens (classic & fine-grained), private repos, and Webhooks.
- [CI/CD Pipelines](integration/ci_cd_pipeline.md) — Workflows for GitHub Actions, GitLab CI/CD, and Jenkins pipelines.

### ⚙️ Configuration & AI Models
- [Configuration Specification](configuration/config_specification.md) — Deep dive into `config.yaml` options, thresholds, and exclusions.
- [AI Providers & Model Routing](configuration/ai_providers.md) — Configuring Anthropic Claude, OpenAI GPT, and Google Gemini with auto-fallback.

### 🛠️ Development & Extensibility
- [Contributing Guide](development/contributing.md) — Code style, testing guidelines, and submission workflow.
- [Scanner Extensibility Guide](development/scanner_extensibility.md) — How to author custom SAST, SCA, Secrets, and IaC scanner plugins.

### 🚢 Operations & Support
- [Docker & Kubernetes Deployment](operations/docker_deployment.md) — Containerized deployment with Docker Compose and Kubernetes manifests.
- [Troubleshooting & FAQ](operations/troubleshooting.md) — Common error resolutions, diagnostic steps, and frequently asked questions.
