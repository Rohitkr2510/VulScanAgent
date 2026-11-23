from pathlib import Path
from typing import Dict, Any, List
from agent.team.base_agent import BaseAgent
from agent.ai_fix.provider_router import AIProviderRouter


class ScanStrategist(BaseAgent):
    """Strategist Agent (analogous to Ammar in reference repo).
    
    Inspects repository topology, detects tech stacks, and recommends tailored scanning priorities.
    """

    def __init__(self, router: AIProviderRouter):
        super().__init__(
            name="Strategist",
            role="Application Security Strategist & Recon Specialist",
            router=router,
            color="blue"
        )

    def assess_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Examines files in repository and devises scanning strategy."""
        exts = set()
        special_files = []
        for p in repo_dir.rglob("*"):
            if not p.is_file() or ".git" in p.parts or ".venv" in p.parts:
                continue
            exts.add(p.suffix.lower())
            if p.name in ["package.json", "requirements.txt", "Dockerfile", "go.mod", "pom.xml", ".env"]:
                special_files.append(p.name)

        summary = f"Detected file extensions: {sorted(list(exts))}\nManifests/Configs present: {special_files}"

        system_prompt = (
            "Analyze the target codebase structure and recommend scanner prioritization. "
            "Return JSON with keys: 'primary_language', 'recommended_scanners' (array), 'focus_areas' (array)."
        )
        user_prompt = f"Repository structure analysis:\n{summary}\nProvide tailored scan strategy recommendations."

        plan = self.ask_json(system_prompt, user_prompt)
        self.log_thought(
            f"Strategy formulated for {plan.get('primary_language', 'detected stack')}.\n"
            f"Focus areas: {', '.join(plan.get('focus_areas', []))}",
            title="🎯 Scan Strategist Assessment"
        )
        return plan
