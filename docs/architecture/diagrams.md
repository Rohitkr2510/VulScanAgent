# 🎨 VulScanAgent Architecture & Visual Blueprint

This document provides visual diagrams illustrating VulScanAgent's autonomous multi-agent architecture, remediation lifecycle, failover mechanisms, and security guardrails.

GitHub natively renders all Mermaid diagrams below.

---

## 1. High-Level Multi-Agent Remediation Pipeline

The following diagram illustrates how the 6 autonomous agent roles collaborate with the scanning engines, test runner, and GitHub API:

```mermaid
flowchart TD
    classDef actor fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#f8fafc;
    classDef process fill:#1e293b,stroke:#06b6d4,stroke-width:1.5px,color:#f8fafc;
    classDef decision fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#f8fafc;
    classDef success fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef failure fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#f8fafc;

    Trigger(["🚀 Trigger\n(CLI / Webhook / CI)"]):::actor --> Init["VulScan Orchestrator"]:::process
    Init --> Clone["RepoConnector\n(Clone & Branch Isolation)"]:::process
    Clone --> Strategist["🎯 ScanStrategist\n(Analyze Topology & Tech Stack)"]:::process
    Strategist --> Baseline["🧪 TestRunner\n(Run Baseline Tests)"]:::process
    Baseline --> Scanner["🔍 CompositeScanner\n(SAST, SCA, Secrets, IaC)"]:::process
    
    Scanner --> CheckVulns{"Vulnerabilities\nDetected?"}:::decision
    CheckVulns -- "No" --> SecureEnd(["🎉 Repository Clean!\nZero Findings"]):::success
    CheckVulns -- "Yes" --> Architect["🛠️ FixArchitect\n(Synthesize Precision Patch)"]:::process

    Architect --> ASTCheck{"AST Syntax\nValid?"}:::decision
    ASTCheck -- "No" --> Diagnostician["🩺 ErrorDiagnostician\n(Analyze Syntax Error)"]:::failure
    Diagnostician --> Architect

    ASTCheck -- "Yes" --> Reviewer["🧐 SecurityReviewer\n(Evaluate MITRE/OWASP Standards)"]:::process
    Reviewer --> ReviewCheck{"Reviewer\nApproved?"}:::decision
    ReviewCheck -- "No (Critique)" --> Architect
    
    ReviewCheck -- "Yes" --> Apply["FixEngine\n(Apply Patch to Sandbox Disk)"]:::process
    Apply --> RunTests["🧪 TestRunner\n(Execute Native Test Suite)"]:::process

    RunTests --> TestStatus{"Tests Pass &\nZero Regressions?"}:::decision
    TestStatus -- "No (Tests Broken)" --> DiagTests["🩺 ErrorDiagnostician\n(Parse Stack Trace)"]:::failure
    DiagTests --> Architect
    
    TestStatus -- "Yes" --> ReScan{"Re-scan:\nVulnerability\nEradicated?"}:::decision
    ReScan -- "No" --> Architect
    ReScan -- "Yes" --> Verifier["🧪 TestVerifier\n(Synthesize Regression Test)"]:::process
    
    Verifier --> Auditor["📝 PRAuditor\n(Draft Audit Report)"]:::process
    Auditor --> PRCreator["🔗 PRCreator\n(Commit, Push & Open PR)"]:::process
    PRCreator --> HumanGate(["👤 Human Security Reviewer\n(Mandatory Sign-off Gate)"]):::success
```

---

## 2. Turn-by-Turn Sequence Diagram

This sequence diagram illustrates the synchronous and asynchronous messaging between the orchestrator, specialized agent roles, external AI providers, sandboxed test executions, and GitHub:

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer / Webhook
    participant Orch as VulScan Orchestrator
    participant Strat as ScanStrategist
    participant Scan as CompositeScanner
    participant Arch as FixArchitect
    participant AI as AI Provider (Gemini / Claude / OpenAI)
    participant Rev as SecurityReviewer
    participant Test as TestRunner (Sandbox)
    participant PR as PRCreator (GitHub API)

    Dev->>Orch: Trigger Scan (Repo URL / Local Dir)
    Orch->>Strat: Assess repository manifests & stack
    Strat->>AI: Formulate scanning focus areas
    AI-->>Strat: Attack surface recommendations
    Strat-->>Orch: Strategy report

    Orch->>Scan: Run SAST, SCA, Secrets & IaC scanners
    Scan-->>Orch: Yield normalized VulFindings

    loop For each detected vulnerability
        Orch->>Arch: Request fix (finding + file context)
        Arch->>AI: Synthesize minimal AST patch
        AI-->>Arch: Return patch within XML quarantine
        Arch-->>Orch: Proposed patch & explanation

        Orch->>Rev: Request peer critique
        Rev->>AI: Evaluate patch against MITRE ATT&CK & OWASP
        AI-->>Rev: Critique & approval verdict
        Rev-->>Orch: Verdict: APPROVED (Score: 9/10)

        Orch->>Test: Apply fix & execute repository test suite
        Test-->>Orch: Exit code 0 (5/5 tests passed)

        Orch->>Scan: Re-scan affected file
        Scan-->>Orch: Confirmed: 0 findings remaining

        Orch->>PR: Push isolated branch & raise Pull Request
        PR-->>Dev: Pull Request opened for human approval
    end
```

---

## 3. Defense-in-Depth Security Guardrails

VulScanAgent enforces strict zero-trust controls at every boundary to prevent AI prompt injection, unauthorized privilege escalation, path traversal, or credential disclosure:

```mermaid
flowchart LR
    classDef shield fill:#042f2e,stroke:#14b8a6,stroke-width:2px,color:#f0fdfa;
    classDef blocked fill:#450a0a,stroke:#dc2626,stroke-width:2px,color:#fef2f2;
    classDef safe fill:#064e3b,stroke:#22c55e,stroke-width:2px,color:#f0fdf4;

    Input["Untrusted Input /\nRepo Files"] --> G1["🛡️ Path Traversal Shield\n(Reject '../' & absolute escapes)"]:::shield
    G1 -- "Escape Attempt" --> Block1["⛔ Blocked:\nSecurityViolationError"]:::blocked
    G1 -- "Safe Path" --> G2["🛡️ Command Sanitizer\n(Reject shell metachars `;&|` )"]:::shield
    
    G2 -- "Injection Pattern" --> Block2["⛔ Blocked:\nCommand Execution Aborted"]:::blocked
    G2 -- "Sanitized Cmd" --> G3["🛡️ Secret Redaction Shield\n(Regex masks for AWS, GHP, sk-*)"]:::shield

    G3 --> G4["🛡️ AST Syntax Validator\n(Reject malformed code before disk)"]:::shield
    G4 -- "Syntax Error" --> Retry["🩺 Self-Correction Loop"]:::shield
    G4 -- "Valid AST" --> Out(["✅ Safe Sandboxed Execution"]):::safe
```

---

## 4. Multi-Provider AI Fallback Mechanism

```mermaid
stateDiagram-v2
    [*] --> PrimaryProvider: User Request / Default

    PrimaryProvider --> Success: 200 OK Response
    PrimaryProvider --> TransientError: 503 / 429 Quota Exceeded

    TransientError --> FallbackModel1: Retry with Fast/Lite Model
    FallbackModel1 --> Success: 200 OK Response
    FallbackModel1 --> SecondaryProvider: Model Unavailable / Rate Limit

    SecondaryProvider --> Success: 200 OK Response
    SecondaryProvider --> TertiaryProvider: Failover

    TertiaryProvider --> Success: 200 OK Response
    TertiaryProvider --> FinalError: All Providers Exhausted

    Success --> [*]
    FinalError --> [*]: Graceful Degradation / Rollback
```
