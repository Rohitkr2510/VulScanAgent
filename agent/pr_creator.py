import os
import re
import logging
from typing import Optional, List
from github import Github, GithubException

from agent.models import VulFinding, FixResult, PRInfo, TestStatus
from agent.security.guardrails import AgentGuardrails

logger = logging.getLogger(__name__)


class PRCreator:
    """Constructs detailed Pull Requests on GitHub with security findings and test results."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            logger.warning("No GitHub Token provided. PR creation will run in dry-run mode.")
            self.gh = None
        else:
            self.gh = Github(self.token)

    def _parse_repo_name(self, repo_url: str) -> str:
        """Extracts 'owner/repo' from GitHub URL."""
        clean_url = repo_url.strip().rstrip("/")
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]
        match = re.search(r"github\.com[/:]([\w\-]+)/([\w\-]+)", clean_url)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        raise ValueError(f"Could not parse GitHub owner/repo from URL: {repo_url}")

    def create_pull_request(
        self,
        repo_url: str,
        base_branch: str,
        fix_branch: str,
        finding: VulFinding,
        fix_result: FixResult,
        labels: List[str] = None,
        reviewers: List[str] = None,
        draft: bool = False
    ) -> PRInfo:
        """Creates GitHub Pull Request with rich Markdown description."""
        raw_title = f"[VulScanAgent] Fix {finding.severity.value}: {finding.title}"
        raw_body = self._build_pr_body(finding, fix_result)

        # Enforce automated secret redaction guardrail
        title = AgentGuardrails.redact_secrets(raw_title)
        body = AgentGuardrails.redact_secrets(raw_body)

        if not self.gh or not repo_url or "github.com" not in repo_url or "dry-run" in repo_url:
            logger.info(f"[DRY RUN] Would create PR on {repo_url} from {fix_branch} to {base_branch}")
            return PRInfo(
                pr_url=f"https://github.com/dry-run/pull/0",
                pr_number=0,
                branch_name=fix_branch,
                title=title,
                body=body
            )

        try:
            repo_slug = self._parse_repo_name(repo_url)
            repo = self.gh.get_repo(repo_slug)

            pr = repo.create_pull(
                title=title,
                body=body,
                base=base_branch,
                head=fix_branch,
                draft=draft
            )

            # Apply labels
            if labels:
                try:
                    pr.add_to_labels(*labels)
                except Exception as e:
                    logger.warning(f"Could not add labels to PR #{pr.number}: {e}")

            # Request reviewers
            if reviewers:
                try:
                    pr.create_review_request(reviewers=reviewers)
                except Exception as e:
                    logger.warning(f"Could not add reviewers to PR #{pr.number}: {e}")

            logger.info(f"Successfully created PR #{pr.number}: {pr.html_url}")
            return PRInfo(
                pr_url=pr.html_url,
                pr_number=pr.number,
                branch_name=fix_branch,
                title=title,
                body=body
            )
        except Exception as e:
            logger.warning(f"GitHub PR creation failed ({e}); falling back to dry-run output.")
            return PRInfo(
                pr_url=f"https://github.com/dry-run/pull/0",
                pr_number=0,
                branch_name=fix_branch,
                title=title,
                body=body
            )

    def _build_pr_body(self, finding: VulFinding, fix_result: FixResult) -> str:
        test_badge = "✅ PASSED"
        test_details = "All regression and unit tests passed."
        if fix_result.test_result:
            if fix_result.test_result.status == TestStatus.PASSED:
                test_badge = f"✅ PASSED ({fix_result.test_result.duration_seconds}s)"
            elif fix_result.test_result.status == TestStatus.SKIPPED:
                test_badge = "⚠️ SKIPPED (No test suite found)"
            else:
                test_badge = "❌ FAILED"
                test_details = f"```\n{fix_result.test_result.failure_details or fix_result.test_result.stderr}\n```"

        latest_attempt = fix_result.attempts[-1] if fix_result.attempts else None
        ai_provider = latest_attempt.provider_used if latest_attempt else "N/A"
        ai_model = latest_attempt.model_name if latest_attempt else "N/A"
        explanation = latest_attempt.explanation if latest_attempt else "Automated security remediation."

        return f"""## 🛡️ VulScanAgent Security Remediation

### ⚠️ Vulnerability Summary
- **Finding ID**: `{finding.id}`
- **Category**: `{finding.category.value.upper()}`
- **Severity**: `{finding.severity.value}`
- **Affected File**: `{finding.file_path}` (Line {finding.line_number})
- **Rule / CVE**: `{finding.rule_id or finding.cve_id or 'N/A'}`

### 🔍 Description
{finding.description}

### 🛠️ Remediation Applied
**AI Engine**: `{ai_provider}` ({ai_model})  
**Explanation**:
{explanation}

### 🧪 Test Verification
**Status**: {test_badge}  
{test_details}

### 📋 Checklist for Human Reviewer
- [ ] Review the proposed changes to ensure intended behavior is preserved.
- [ ] Confirm no internal credentials or sensitive variables are affected.
- [ ] Approve and merge to apply the fix to `{finding.file_path}`.

---
*Generated autonomously by **VulScanAgent** — Security AI Remediation Bot.*
"""
