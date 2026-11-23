#!/usr/bin/env bash
# VulScanAgent — Universal 1-Click Docker Runner (Linux & macOS)
set -e

echo "🛡️ VulScanAgent Docker Launcher"
echo "================================="

# Check for Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH."
    echo "Please install Docker from https://docs.docker.com/get-docker/ and try again."
    exit 1
fi

# Create .env from template if missing
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "ℹ️  No .env file found. Creating from .env.example..."
        cp .env.example .env
        echo "⚠️  Please update your API keys in .env for full remediation features."
    fi
fi

# Ensure output directory exists
mkdir -p scans_output

# Build and start container
echo "📦 Building and starting VulScanAgent container..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

echo ""
echo "✅ VulScanAgent is running!"
echo "🌐 Web Dashboard: http://localhost:8000"
echo "📋 View logs:     docker compose logs -f"
echo "🛑 Stop container: docker compose down"
