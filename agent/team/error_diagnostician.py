from typing import Dict, Any
from agent.team.base_agent import BaseAgent
from agent.ai_fix.provider_router import AIProviderRouter
from agent.models import VulFinding


class ErrorDiagnostician(BaseAgent):
    """Error Diagnostician Agent (analogous to Kofahi in reference repo).
    
    When compilation, AST validation, or tests fail, diagnoses the exact root cause
    and prescribes adjustments to the Fix Architect.
    """

    def __init__(self, router: AIProviderRouter):
        super().__init__(
            name="ErrorDiagnostician",
            role="Compiler & Test Failure Specialist",
            router=router,
            color="yellow"
        )

    def diagnose_failure(
        self,
        error_output: str,
        file_path: str,
        applied_code: str,
        finding: VulFinding
    ) -> Dict[str, Any]:
        """Diagnoses execution/test failure and returns actionable instructions."""
        system_prompt = (
            "You are an expert compiler and runtime error diagnostician. "
            "A security fix was applied, but testing or validation failed with an error. "
            "Analyze the traceback/compiler error and provide clear, prescriptive instructions "
            "on how to adjust the fix to make it pass. "
            "Respond in JSON format with keys:\n"
            "- 'root_cause': string (why the failure occurred)\n"
            "- 'prescribed_fix': string (step-by-step instructions for the code architect)"
        )

        user_prompt = f"""Target File: {file_path}
Vulnerability Being Remediated: {finding.title}

Applied Code Snippet:
```
{applied_code[:1500]}
```

Error / Traceback:
```
{error_output[:2000]}
```

Analyze the failure and return JSON with root_cause and prescribed_fix."""

        diagnosis = self.ask_json(system_prompt, user_prompt)
        self.log_thought(
            f"Root Cause: {diagnosis.get('root_cause', 'Unknown')}\n"
            f"Prescription: {diagnosis.get('prescribed_fix', 'Inspect error details')}",
            title="🩺 ErrorDiagnostician Diagnosis"
        )
        return diagnosis
