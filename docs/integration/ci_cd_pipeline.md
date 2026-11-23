# CI/CD Pipeline Integration

VulScanAgent can be integrated directly into continuous integration workflows to enforce security gates and automatically remediate vulnerabilities.

---

## 1. GitHub Actions

VulScanAgent includes a native workflow template in [`.github/workflows/vulscan.yml`](file:///c:/Users/rkrah/OneDrive/Desktop/DevOps/VulScanAgent/.github/workflows/vulscan.yml).

```yaml
name: VulScanAgent Automated Security Remediation

on:
  push:
    branches: [ "main", "master" ]
  pull_request:
    branches: [ "main", "master" ]
  schedule:
    - cron: '0 2 * * 1' # Weekly Monday scan
  workflow_dispatch:

jobs:
  vulscan:
    name: Security Scan & Remediation
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: |
          pip install semgrep
          pip install -r requirements.txt

      - name: Execute VulScanAgent
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          python main.py scan --local . --severity HIGH
```

---

## 2. GitLab CI/CD

Add the following job to your `.gitlab-ci.yml`:

```yaml
vulscan_agent:
  image: python:3.12-slim
  stage: test
  before_script:
    - apt-get update && apt-get install -y git curl
    - pip install -r requirements.txt
  script:
    - python main.py scan --local . --severity HIGH
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

---

## 3. Jenkins Pipeline

In your `Jenkinsfile`:

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
        }
    }
    environment {
        GITHUB_TOKEN = credentials('github-token-secret')
        OPENAI_API_KEY = credentials('openai-api-key')
    }
    stages {
        stage('VulScan Remediation') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python main.py scan --local . --severity HIGH'
            }
        }
    }
}
```
