import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.table import Table

from config.config_loader import AppConfig
from agent.models import (
    VulFinding,
    FixAttempt,
    FixResult,
    ScanReport,
    TestResult,
    TestStatus,
    PRInfo,
    VulnerabilitySeverity,
    CandidateStatus,
    CoverageLedger,
)
from agent.scanner import CompositeScanner
from agent.ai_fix.provider_router import AIProviderRouter
from agent.ai_fix.fix_engine import FixEngine
from agent.test_runner.runner import TestRunner
from agent.repo_connector import RepoConnector
from agent.pr_creator import PRCreator
from agent.team import (
    ScanStrategist,
    SecurityReviewer,
    ErrorDiagnostician,
    FixArchitect,
    TestVerifier,
    CandidateVerifier,
    PRAuditor,
)

console = Console()
logger = logging.getLogger("VulScanAgent")


class VulScanOrchestrator:
    """The central brain orchestrating the collaborative multi-agent security team."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.scanner = CompositeScanner(config.scanning.scanners)
        self.router = AIProviderRouter(
            preferred_provider=config.ai.provider,
            fallback_order=config.ai.fallback_order,
            model_overrides=config.ai.models,
            temperature=config.ai.temperature,
        )
        self.fix_engine = FixEngine(self.router, max_retries=config.ai.max_fix_retries)
        self.test_runner = TestRunner(
            timeout_seconds=config.testing.timeout_seconds,
            custom_command=config.testing.custom_test_cmd or None,
        )
        self.pr_creator = PRCreator(token=config.repo.token)

        # Multi-Agent Collaborative Team (inspired by salah9003 Agentic AI pattern)
        self.strategist = ScanStrategist(self.router)
        self.fix_architect = FixArchitect(self.router)
        self.security_reviewer = SecurityReviewer(self.router)
        self.error_diagnostician = ErrorDiagnostician(self.router)
        self.test_verifier = TestVerifier(self.router)
        self.candidate_verifier = CandidateVerifier(self.router)
        self.pr_auditor = PRAuditor(self.router)

    def run(self, local_repo_override: Optional[Path] = None) -> Dict[str, Any]:
        """Collaborative multi-agent execution loop."""
        console.print("\n[bold cyan]🛡️ VulScanAgent Collaborative Multi-Agent Pipeline[/bold cyan]\n")

        # 1. Acquire Repository
        connector = None
        if local_repo_override:
            repo_dir = Path(local_repo_override)
            console.print(f"[bold green]📂 Operating on local directory:[/bold green] {repo_dir}")
        else:
            connector = RepoConnector(
                repo_url=self.config.repo.url,
                base_branch=self.config.repo.branch,
                token=self.config.repo.token,
            )
            console.print(f"[bold yellow]🔄 Cloning target repository:[/bold yellow] {self.config.repo.url}")
            repo_dir = connector.clone()

        try:
            # 2. Agent 1: ScanStrategist assesses repository
            try:
                self.strategist.assess_repository(repo_dir)
            except Exception as e:
                logger.warning(f"Strategist assessment note: {e}")

            # 3. Baseline Test Execution
            console.print("[bold cyan]🧪 Running baseline test suite...[/bold cyan]")
            baseline_result = self.test_runner.run_tests(repo_dir)
            console.print(f"Baseline test status: [bold]{baseline_result.status.value}[/bold] (exit code {baseline_result.exit_code})")

            # 4. Multi-Layer Vulnerability Scan (Cloudflare Phase 2: Coverage-Led Hunting)
            console.print(f"\n[bold magenta]🔍 Phase 2 — Multi-Layer Codebase Scan (Threshold: {self.config.scanning.severity_threshold.value})...[/bold magenta]")
            raw_findings = self.scanner.run_all(repo_dir, self.config.scanning.severity_threshold)

            self._display_findings_table(raw_findings)

            if not raw_findings:
                console.print("\n[bold green]🎉 Zero vulnerabilities found meeting threshold. Repository is secure![/bold green]\n")
                return {"status": "clean", "findings": 0, "fixed": 0, "prs": []}

            # Phase 3: Cloudflare Adversarial Candidate Validation
            console.print("\n[bold magenta]⚖️ Phase 3 — Adversarial Candidate Validation (Cloudflare Audit Principle)...[/bold magenta]")
            confirmed_findings: List[VulFinding] = []
            for candidate in raw_findings:
                file_path = repo_dir / candidate.file_path
                content = file_path.read_text(encoding="utf-8", errors="ignore") if file_path.exists() else ""
                verdict = self.candidate_verifier.verify_candidate(candidate, content)
                candidate.validation_status = verdict.status
                candidate.validation_verdict = verdict
                if verdict.status in [CandidateStatus.CONFIRMED, CandidateStatus.NEEDS_VALIDATION]:
                    confirmed_findings.append(candidate)
                else:
                    console.print(f"  [dim yellow]Skipping disproved candidate {candidate.id}: {verdict.disproof_rationale}[/dim yellow]")

            if not confirmed_findings:
                console.print("\n[bold green]🎉 All scanner candidates were disproved as false positives. Repository is secure![/bold green]\n")
                return {"status": "clean", "findings": 0, "fixed": 0, "prs": []}

            # 5. Multi-Agent Remediation Loop
            fix_results: List[FixResult] = []
            prs_created: List[PRInfo] = []

            for idx, finding in enumerate(confirmed_findings, start=1):
                console.print(f"\n[bold yellow]━━━ Remediating Finding {idx}/{len(confirmed_findings)}: [{finding.severity.value}] {finding.title} ━━━[/bold yellow]")
                safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", finding.id.lower())
                branch_name = f"fix/{safe_id}"

                if connector:
                    connector.create_fix_branch(branch_name)

                original_file_path = repo_dir / finding.file_path
                original_backup = original_file_path.read_text(encoding="utf-8", errors="ignore") if original_file_path.exists() else ""

                fix_success = False
                attempts_history: List[FixAttempt] = []
                last_test_res: Optional[TestResult] = None
                reviewer_feedback: Optional[str] = None
                error_prescription: Optional[str] = None
                latest_review: Dict[str, Any] = {}

                for attempt_num in range(1, self.config.ai.max_fix_retries + 1):
                    console.print(f"  [cyan]Step {attempt_num}A — FixArchitect proposes patch...[/cyan]")
                    try:
                        explanation, fixed_content = self.fix_architect.propose_patch(
                            file_path=finding.file_path,
                            original_content=original_backup,
                            finding=finding,
                            reviewer_feedback=reviewer_feedback,
                            error_prescription=error_prescription,
                        )
                    except Exception as e:
                        console.print(f"  [red]FixArchitect failed:[/red] {e}")
                        break

                    # AST Syntax Pre-validation
                    is_valid, syntax_err = self.fix_engine._validate_syntax(finding.file_path, fixed_content)
                    if not is_valid:
                        console.print(f"  [yellow]Syntax error detected. Calling ErrorDiagnostician...[/yellow]")
                        diagnosis = self.error_diagnostician.diagnose_failure(
                            error_output=syntax_err or "Syntax error",
                            file_path=finding.file_path,
                            applied_code=fixed_content,
                            finding=finding,
                        )
                        error_prescription = diagnosis.get("prescribed_fix")
                        continue

                    # Step B: Senior Security Reviewer Agent critiques the fix
                    console.print(f"  [green]Step {attempt_num}B — SecurityReviewer critiques patch...[/green]")
                    try:
                        latest_review = self.security_reviewer.review_fix(
                            finding=finding,
                            original_code=original_backup,
                            proposed_code=fixed_content,
                            explanation=explanation,
                        )
                    except Exception as e:
                        latest_review = {"approved": True, "feedback": f"Review bypass: {e}"}

                    if not latest_review.get("approved", True) and attempt_num < self.config.ai.max_fix_retries:
                        console.print(f"  [yellow]SecurityReviewer requested revisions. Re-prompting FixArchitect...[/yellow]")
                        reviewer_feedback = latest_review.get("feedback")
                        continue

                    # Step C: Apply fix and verify with tests
                    self.fix_engine.apply_fix_to_disk(repo_dir, finding.file_path, fixed_content)

                    attempt_info = FixAttempt(
                        attempt_number=attempt_num,
                        provider_used=self.config.ai.provider,
                        model_name=self.config.ai.models.get(self.config.ai.provider, "default"),
                        proposed_diff="",
                        explanation=explanation,
                        files_modified=[finding.file_path],
                    )
                    attempts_history.append(attempt_info)

                    console.print("  [magenta]Step C — Running test verification...[/magenta]")
                    test_res = self.test_runner.run_tests(repo_dir)
                    last_test_res = test_res

                    if test_res.status in [TestStatus.PASSED, TestStatus.SKIPPED]:
                        # Re-scan file to confirm vulnerability is eradicated
                        recheck_findings = self.scanner.run_all(repo_dir, self.config.scanning.severity_threshold)
                        still_vulnerable = any(f.file_path == finding.file_path and f.rule_id == finding.rule_id for f in recheck_findings)

                        if not still_vulnerable:
                            console.print(f"  [bold green]✅ Verified! Tests pass and vulnerability resolved.[/bold green]")
                            fix_success = True

                            # Step D: TestVerifier synthesizes targeted regression test
                            if self.config.testing.generate_ai_tests and original_backup:
                                try:
                                    self.test_verifier.generate_regression_test(
                                        repo_dir=repo_dir,
                                        finding=finding,
                                        original_code=original_backup,
                                        fixed_code=fixed_content,
                                    )
                                except Exception as e:
                                    logger.warning(f"Regression test generation note: {e}")
                            break
                        else:
                            console.print("  [yellow]Vulnerability still detectable after modification. Diagnosing...[/yellow]")
                            error_prescription = f"Scanner still flags rule {finding.rule_id}. Further hardening needed."
                    else:
                        console.print(f"  [red]Tests failed after patch. Calling ErrorDiagnostician...[/red]")
                        diagnosis = self.error_diagnostician.diagnose_failure(
                            error_output=test_res.failure_details or test_res.stderr or test_res.stdout,
                            file_path=finding.file_path,
                            applied_code=fixed_content,
                            finding=finding,
                        )
                        error_prescription = diagnosis.get("prescribed_fix")

                fix_res = FixResult(
                    finding_id=finding.id,
                    success=fix_success,
                    attempts=attempts_history,
                    final_diff="",
                    applied_files=[finding.file_path] if fix_success else [],
                    test_result=last_test_res,
                    error_message=error_prescription if not fix_success else None,
                )
                fix_results.append(fix_res)

                if fix_success:
                    # Commit, Push & Raise PR with PRAuditor report
                    if connector:
                        commit_msg = f"fix(security): resolve {finding.title} in {finding.file_path}"
                        connector.commit_changes(commit_msg)
                        try:
                            connector.push(branch_name)
                        except Exception as e:
                            logger.error(f"Could not push branch: {e}")

                    console.print(f"  [purple]Step D — PRAuditor drafting formal Pull Request documentation...[/purple]")
                    try:
                        pr_body = self.pr_auditor.build_pr_documentation(finding, fix_res, latest_review)
                    except Exception:
                        pr_body = self.pr_creator._build_pr_body(finding, fix_res)

                    pr_info = self.pr_creator.create_pull_request(
                        repo_url=self.config.repo.url if connector else "https://github.com/dry-run/local",
                        base_branch=self.config.repo.branch,
                        fix_branch=branch_name,
                        finding=finding,
                        fix_result=fix_res,
                        labels=self.config.pr.labels,
                        reviewers=self.config.pr.reviewers,
                        draft=self.config.pr.draft,
                    )
                    pr_info.body = pr_body
                    prs_created.append(pr_info)
                    console.print(f"  [bold green]🔗 PR Created:[/bold green] {pr_info.pr_url}")
                    console.print(f"\n[bold cyan]📋 Pull Request Preview for {finding.id}:[/bold cyan]\n{pr_body[:800]}...\n")

                else:
                    # Rollback if fix didn't succeed
                    if original_backup and original_file_path.exists():
                        original_file_path.write_text(original_backup, encoding="utf-8")
                        console.print(f"  [yellow]↩️ Reverted changes to {finding.file_path} due to failed fix/tests.[/yellow]")

            # Phase 6: Cloudflare-Style Target-Neutral Multi-Report Artifacts
            try:
                artifacts = self.pr_auditor.generate_audit_artifacts(
                    repo_dir=repo_dir,
                    all_candidates=raw_findings,
                    confirmed_findings=confirmed_findings,
                    fix_results=fix_results
                )
                console.print(f"[bold cyan]📑 Audit Artifacts Generated:[/bold cyan] {', '.join(artifacts.keys())}")
            except Exception as e:
                logger.warning(f"Audit artifact generation note: {e}")

            console.print("\n[bold green]🏁 VulScanAgent Collaborative Execution Complete.[/bold green]")
            return {
                "status": "complete",
                "findings": len(confirmed_findings),
                "candidates": len(raw_findings),
                "confirmed": len(confirmed_findings),
                "fixed": sum(1 for f in fix_results if f.success),
                "prs": [pr.pr_url for pr in prs_created],
            }

        finally:
            if connector:
                connector.cleanup()

    def _display_findings_table(self, findings: List[VulFinding]) -> None:
        table = Table(title="🔍 Detected Vulnerabilities", show_header=True, header_style="bold magenta")
        table.add_column("Severity", style="bold", width=12)
        table.add_column("Category", width=10)
        table.add_column("Location", width=30)
        table.add_column("Vulnerability Title")

        for f in findings:
            sev_color = {
                VulnerabilitySeverity.CRITICAL: "red on black",
                VulnerabilitySeverity.HIGH: "red",
                VulnerabilitySeverity.MEDIUM: "yellow",
                VulnerabilitySeverity.LOW: "cyan",
                VulnerabilitySeverity.INFO: "dim",
            }.get(f.severity, "white")

            loc = f"{f.file_path}:{f.line_number}"
            table.add_row(f"[{sev_color}]{f.severity.value}[/{sev_color}]", f.category.value.upper(), loc, f.title)

        console.print(table)
