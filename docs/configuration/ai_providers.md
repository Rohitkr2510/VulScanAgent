# AI Providers & Model Routing

VulScanAgent features a universal model router (`agent/ai_fix/provider_router.py`) that abstracts interactions with **Anthropic Claude**, **OpenAI GPT**, and **Google Gemini**.

---

## 1. Supported Providers & Models

| Provider | Default Model | Key Environment Variable | Best For |
|---|---|---|---|
| **Anthropic** | `claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` | Complex code logic, architectural reasoning, and minimal diff generation. |
| **OpenAI** | `gpt-4o` | `OPENAI_API_KEY` | Broad multi-language fluency and structured JSON output. |
| **Google** | `gemini-2.5-pro` | `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Long file context windows (up to 2M tokens) and rapid inference. |

---

## 2. Automatic Fallback Cascading (`provider: "auto"`)

When `ai.provider` is set to `"auto"` (the default), the router queries available API keys in your environment and evaluates them against the `fallback_order` configuration:

```
                  ┌──────────────────────┐
                  │ Request Patch / Fix  │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Try Provider 1       │
                  │ (Anthropic Claude)   │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼ (Success)                       ▼ (Rate Limit / Failure)
     [Return Patch]               ┌──────────────────────┐
                                  │ Try Provider 2       │
                                  │ (OpenAI GPT-4o)      │
                                  └──────────┬───────────┘
                                             │
                            ┌────────────────┴────────────────┐
                            ▼ (Success)                       ▼ (Failure)
                     [Return Patch]               ┌──────────────────────┐
                                                  │ Try Provider 3       │
                                                  │ (Google Gemini)      │
                                                  └──────────────────────┘
```

This ensures uninterrupted operations even during cloud provider outages, quota limits, or network throttling.

---

## 3. Cost & Performance Optimization

- **Low Temperature**: Default temperature is set to `0.1` for maximum code stability and deterministic fixes.
- **AST Pre-flight Checks**: Patches are parsed before testing to avoid wasting API tokens on broken syntax.
- **Minimal Context Truncation**: Only the affected file and surrounding relevant definitions are passed, minimizing prompt token consumption.
