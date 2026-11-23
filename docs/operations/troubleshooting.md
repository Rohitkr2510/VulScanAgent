# Troubleshooting & FAQ

## 1. Common Issues & Solutions

### 1.1 "No AI provider API key found"
**Cause**: The agent could not find `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY` in environment variables or `.env`.  
**Solution**:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Insert a valid API key for at least one provider.
3. Verify with `python main.py verify-keys`.

---

### 1.2 "Could not parse GitHub owner/repo from URL"
**Cause**: The repository URL passed via `--repo` or Webhook payload was malformed.  
**Solution**: Ensure the URL matches standard GitHub formats:
- `https://github.com/organization/repository`
- `https://github.com/organization/repository.git`

---

### 1.3 "Dry-run mode: PR not created"
**Cause**: `GITHUB_TOKEN` is missing from `.env` or system environment.  
**Solution**: Provide a valid GitHub Personal Access Token with `repo` scope to enable real PR generation.

---

### 1.4 Tests Fail Repeatedly and Changes Revert
**Cause**: The agent is configured with `testing.require_pass: true`, and the generated patch broke existing unit test assertions.  
**Solution**:
1. Inspect the test failure details output in the terminal.
2. The `ErrorDiagnostician` agent automatically retries up to `ai.max_fix_retries` times.
3. If the repository's baseline tests were already failing prior to the scan, ensure the base branch tests pass before running VulScanAgent.

---

## 2. Frequently Asked Questions (FAQ)

**Q: Can VulScanAgent automatically merge the Pull Requests?**  
A: No. By design, VulScanAgent follows a strict **Zero Auto-Merge Policy**. Every PR must be reviewed and approved by a human engineer.

**Q: Does VulScanAgent send proprietary repository code to third parties?**  
A: Only the vulnerable file context is transmitted to the AI provider you configure (Anthropic, OpenAI, or Google). If you require complete on-prem data isolation, you can configure local models or enterprise private endpoints via `AIProviderRouter`.

**Q: How does VulScanAgent avoid creating duplicate PRs?**  
A: Fix branches are deterministically named after the finding ID (`fix/<finding-id>`). If an existing branch or PR exists, VulScanAgent updates the existing branch rather than opening duplicates.
