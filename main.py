import sys
from pathlib import Path
import typer
from rich.console import Console

from config.config_loader import AppConfig
from agent.orchestrator import VulScanOrchestrator
from agent.models import VulnerabilitySeverity

app = typer.Typer(
    name="VulScanAgent",
    help="Autonomous AI agent that scans, repairs, tests, and raises PRs for code vulnerabilities.",
    add_completion=False,
)
console = Console()


@app.command()
def scan(
    repo_url: str = typer.Option(None, "--repo", "-r", help="GitHub repository URL (public or private)"),
    branch: str = typer.Option("main", "--branch", "-b", help="Target branch name"),
    config_file: str = typer.Option("config/config.yaml", "--config", "-c", help="Path to config.yaml"),
    local_dir: str = typer.Option(None, "--local", "-l", help="Run directly on a local folder instead of cloning"),
    severity: str = typer.Option("MEDIUM", "--severity", "-s", help="Minimum severity: LOW, MEDIUM, HIGH, CRITICAL"),
    provider: str = typer.Option(None, "--provider", "-p", help="AI provider: openai, anthropic, google, auto"),
):
    """Scan repository for vulnerabilities, fix with AI, test, and raise Pull Requests."""
    config_path = Path(config_file)
    if not config_path.exists():
        console.print(f"[bold red]Configuration file not found:[/bold red] {config_path}")
        raise typer.Exit(code=1)

    config = AppConfig.from_yaml(config_path)

    # CLI option overrides
    if repo_url:
        config.repo.url = repo_url
    if branch:
        config.repo.branch = branch
    if severity:
        config.scanning.severity_threshold = VulnerabilitySeverity(severity.upper())
    if provider:
        config.ai.provider = provider.lower()

    orchestrator = VulScanOrchestrator(config)
    local_path = Path(local_dir) if local_dir else None
    result = orchestrator.run(local_repo_override=local_path)

    if result.get("fixed", 0) > 0:
        console.print(f"[bold green]✨ Remediated {result['fixed']} vulnerabilities and generated PRs![/bold green]")
    else:
        console.print("[dim]No fixes required or generated.[/dim]")


@app.command()
def dashboard(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host interface to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload for development"),
):
    """Launch the VulScanAgent Web Dashboard & Webhook Server."""
    import uvicorn
    console.print(f"\n[bold green]🛡️ Launching VulScanAgent Web Dashboard at http://{host}:{port}[/bold green]\n")
    uvicorn.run("dashboard.app:app", host=host, port=port, reload=reload)


@app.command()
def verify_keys():
    """Verify that your AI and GitHub API keys are configured and functional."""
    from agent.ai_fix.provider_router import AIProviderRouter
    import os

    console.print("\n[bold cyan]🔑 Checking API Keys and Connectivity[/bold cyan]\n")

    gh_token = os.getenv("GITHUB_TOKEN")
    console.print(f"GitHub Token: {'[green]Found[/green]' if gh_token else '[yellow]Missing (PRs will run in dry-run mode)[/yellow]'}")

    router = AIProviderRouter()
    providers = router._get_available_providers()
    console.print(f"Available AI Providers: [bold green]{', '.join(providers) if providers else '[red]None[/red]'}[/bold green]")

    if not providers:
        console.print("[yellow]Tip: Add your OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY to .env[/yellow]")
    else:
        console.print("[green]Ready to remediate code![/green]")


if __name__ == "__main__":
    app()
