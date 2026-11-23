from typing import Dict, Any
from agent.team.base_agent import BaseAgent
from agent.ai_fix.provider_router import AIProviderRouter
from agent.models import VulFinding


class SecurityReviewer(BaseAgent):
    """Senior Security Reviewer Agent (analogous to Hassan in reference repo).
    
    Critiques proposed fixes before application, confirming they eliminate the vulnerability
    without introducing regressions or secondary flaws.
    """

    def __init__(self, router: AIProviderRouter):
        super().__init__(
            name="SecurityReviewer",
            role="Senior Application Security Auditor & Critic",
            router=router,
            color="green"
        )

    def review_fix(
        self,
        finding: VulFinding,
        original_code: str,
        proposed_code: str,
        explanation: str
    ) -> Dict[str, Any]:
        """Critically reviews proposed patch."""
        system_prompt = (
            "You are a rigorous Senior Application Security Auditor. "
            "Your role is to review a proposed security patch and determine if it should be approved. "
            "Verify that:\n"
            "1. The vulnerability is genuinely eliminated.\n"
            "2. No new vulnerabilities (e.g. bypasses, weak sanitization, unhandled exceptions) are introduced.\n"
            "3. Existing business functionality is preserved.\n\n"
            "Respond in JSON format with keys:\n"
            "- 'approved': boolean (true if ready for testing, false if adjustments needed)\n"
            "- 'feedback': string (actionable technical critique and advice)\n"
            "- 'confidence_score': integer (1 to 10)"
        )

        user_prompt = f"""Vulnerability: [{finding.severity.value}] {finding.title}
File: {finding.file_path}
Rule: {finding.rule_id or finding.cve_id}

Original Code snippet:
```
{finding.code_snippet or original_code[:1500]}
```

Proposed Fix:
```
{proposed_code[:2000]}
```

Fix Explanation:
{explanation}

Please conduct a strict review and respond in JSON format."""

        review = self.ask_json(system_prompt, user_prompt)
        approved = review.get("approved", True)
        status_icon = "✅ APPROVED" if approved else "⚠️ REVISIONS REQUIRED"

        self.log_thought(
            f"Review Verdict: {status_icon} (Confidence: {review.get('confidence_score', 'N/A')}/10)\n"
            f"Critique: {review.get('feedback', 'No additional feedback.')}",
            title="🧐 SecurityReviewer Assessment"
        )

        return review
