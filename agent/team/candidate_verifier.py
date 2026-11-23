import json
import logging
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel

from agent.team.base_agent import BaseAgent
from agent.models import VulFinding, CandidateStatus, ValidationVerdict
from agent.ai_fix.provider_router import AIProviderRouter

console = Console()
logger = logging.getLogger("VulScanAgent.CandidateVerifier")


class CandidateVerifier(BaseAgent):
    """Cloudflare-inspired Adversarial Candidate Verifier Agent.
    
    Adopts Cloudflare's core principle: 'The agent that hunts is never the agent that validates.'
    Operates as an adversarial auditor whose primary objective is to aggressively challenge
    and attempt to DISPROVE scanner candidate findings before any code changes are made.
    """

    def __init__(self, router: AIProviderRouter):
        system_prompt = """You are the Senior Adversarial Security Verifier for an elite DevSecOps audit team (Cloudflare security-audit-skill standard).

YOUR SOLE MISSION:
Aggressively challenge and attempt to DISPROVE candidate vulnerabilities found by static scanners.
Assume every scanner finding is a potential FALSE POSITIVE until rigorously proven otherwise.

EVALUATION CRITERIA:
1. Reachability: Can untrusted, external adversary input realistically reach this line of code?
2. Intermediate Sanitization: Does a framework layer, middleware, type-caster (Pydantic/dataclass), or regex neutralize the threat?
3. Context Relevance: Is this file a test mock, an internal build script, or dead unreachable code?
4. Exploitation Feasibility: Is there a realistic exploit payload or is the warning purely theoretical?

VERDICT OPTIONS:
- CONFIRMED: The vulnerability is real, untrusted input reaches the sink, and an exploit is practically viable.
- REJECTED: The finding is a false positive (e.g. mitigated by framework, unreachable dead code, sanitized upstream).
- NEEDS_VALIDATION: The finding has high risk potential but depends on runtime deployment config or external environment setup.

OUTPUT INSTRUCTIONS:
You MUST respond with a valid JSON object matching this schema exactly:
{
  "verdict": "CONFIRMED" | "REJECTED" | "NEEDS_VALIDATION",
  "confidence": 1-10,
  "reachability_proven": true | false,
  "disproof_rationale": "Clear, technical explanation of why this was confirmed, rejected, or needs validation.",
  "taint_path": "Source -> Transform -> Sink (or 'None - Unreachable')",
  "prerequisites": "Prerequisites needed for exploit (e.g. 'Public network exposure', 'Authenticated admin')"
}
"""
        self.system_prompt = system_prompt
        super().__init__(name="CandidateVerifier", role="Adversarial Candidate Verifier", router=router, color="magenta")

    def verify_candidate(
        self,
        finding: VulFinding,
        file_content: str,
        repo_architecture_summary: Optional[str] = None
    ) -> ValidationVerdict:
        """Adversarially validates candidate finding to eliminate false positives."""
        prompt = f"""### CANDIDATE VULNERABILITY TO DISPROVE
- Finding ID: {finding.id}
- Title: {finding.title}
- Category: {finding.category.value}
- Severity: {finding.severity.value}
- Target File: {finding.file_path} (Line {finding.line_number})
- Rule / CVE: {finding.cve_id or finding.rule_id}
- Description: {finding.description}
- Scanner Code Snippet:
```
{finding.code_snippet or 'N/A'}
```

### REPOSITORY ARCHITECTURE CONTEXT
{repo_architecture_summary or 'Standard repository architecture'}

### FULL TARGET FILE CONTENT
```{finding.file_path.split('.')[-1]}
{file_content[:5000]}
```

Analyze the code above adversarially. Can you disprove this vulnerability, or is it confirmed reachable and exploitable?
Output JSON only.
"""
        try:
            res = self.ask_json(self.system_prompt, prompt)
            verdict_str = str(res.get("verdict", "CONFIRMED")).upper()
            status_map = {
                "CONFIRMED": CandidateStatus.CONFIRMED,
                "REJECTED": CandidateStatus.REJECTED,
                "NEEDS_VALIDATION": CandidateStatus.NEEDS_VALIDATION,
            }
            status = status_map.get(verdict_str, CandidateStatus.CONFIRMED)
            verdict = ValidationVerdict(
                status=status,
                confidence_score=int(res.get("confidence", 8)),
                reachability_proven=bool(res.get("reachability_proven", True)),
                disproof_rationale=res.get("disproof_rationale", "Verified by adversarial inspection."),
                taint_path=res.get("taint_path"),
                prerequisites=res.get("prerequisites")
            )
        except Exception as e:
            logger.warning(f"CandidateVerifier parsing fallback: {e}")
            verdict = ValidationVerdict(
                status=CandidateStatus.CONFIRMED,
                confidence_score=7,
                reachability_proven=True,
                disproof_rationale=f"Verification fallback: {e}"
            )

        status_emoji = {
            CandidateStatus.CONFIRMED: "🔥 CONFIRMED",
            CandidateStatus.REJECTED: "🛡️ REJECTED (False Positive)",
            CandidateStatus.NEEDS_VALIDATION: "⚠️ NEEDS VALIDATION",
        }.get(verdict.status, verdict.status.value)

        console.print(
            Panel(
                f"[bold]Candidate Evaluation:[/bold] {status_emoji} (Confidence: {verdict.confidence_score}/10)\n"
                f"[bold]Rationale:[/bold] {verdict.disproof_rationale}\n"
                f"[bold]Taint Path:[/bold] {verdict.taint_path or 'N/A'}",
                title="⚖️ CandidateVerifier (Cloudflare Phase 3 Audit)",
                border_style="magenta" if verdict.status == CandidateStatus.CONFIRMED else "green"
            )
        )
        return verdict
