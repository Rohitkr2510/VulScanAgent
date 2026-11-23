# VulScanAgent — Universal 1-Click Docker Runner (Windows PowerShell)
$ErrorActionPreference = "Stop"

Write-Host "🛡️ VulScanAgent Docker Launcher (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check for Docker installation
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "❌ Error: Docker is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows from https://docs.docker.com/desktop/install/windows-install/ and ensure it is running." -ForegroundColor Yellow
    exit 1
}

# Create .env from template if missing
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Write-Host "ℹ️  No .env file found. Creating from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "⚠️  Please configure your API keys in .env for full remediation features." -ForegroundColor Yellow
    }
}

# Ensure output directory exists
if (-not (Test-Path scans_output)) {
    New-Item -ItemType Directory -Path scans_output | Out-Null
}

Write-Host "📦 Building and starting VulScanAgent container..." -ForegroundColor Green
docker compose up -d --build

Write-Host ""
Write-Host "✅ VulScanAgent is running!" -ForegroundColor Green
Write-Host "🌐 Web Dashboard: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📋 View logs:     docker compose logs -f" -ForegroundColor White
Write-Host "🛑 Stop container: docker compose down" -ForegroundColor White
