# Multi-platform production Dockerfile for VulScanAgent
# Runs seamlessly on Linux (amd64/arm64), macOS (Intel/Apple Silicon), and Windows
FROM python:3.12-slim

# Prevent interactive prompts & unbuffered python logs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install runtime dependencies: Git, build tools, curl, and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Semgrep for SAST analysis
RUN pip install semgrep

WORKDIR /app

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy codebase
COPY . .

# Expose Web Dashboard port
EXPOSE 8000

# Flexible entrypoint allows running any CLI command (dashboard, scan, verify-keys)
ENTRYPOINT ["python", "main.py"]
CMD ["dashboard", "--host", "0.0.0.0", "--port", "8000"]
