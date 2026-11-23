# GitHub Integration Guide

## 1. Authentication Options

VulScanAgent supports scanning and pushing remediations to both **public** and **private** GitHub repositories using Personal Access Tokens (PAT) or GitHub Apps.

---

## 2. Setting Up a Personal Access Token (PAT)

### 2.1 Fine-Grained Personal Access Token (Recommended)
1. Go to **GitHub Settings > Developer Settings > Personal access tokens > Fine-grained tokens**.
2. Click **Generate new token**.
3. Set **Resource Owner** to your user or organization.
4. Set **Repository Access**: Select *Only select repositories* (or *All repositories*).
5. Grant the following **Repository Permissions**:
   - **Contents**: `Read and write` (to clone code and push fix branches)
   - **Pull requests**: `Read and write` (to create PRs and assign reviewers)
   - **Metadata**: `Read-only` (default)
6. Generate token and copy the value (`github_pat_...`).
7. Add to your `.env`:
   ```env
   GITHUB_TOKEN=github_pat_123456...
   ```

### 2.2 Classic Token (Alternative)
1. Go to **Developer Settings > Personal access tokens > Tokens (classic)**.
2. Select scope:
   - `repo` (Full control of private repositories)
3. Generate and paste into `.env`.

---

## 3. GitHub Webhook Configuration

Automate scans on every commit or PR event:

1. In your GitHub repository, navigate to **Settings > Webhooks > Add webhook**.
2. Configure:
   - **Payload URL**: `https://<your-server-or-domain>/api/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Optional secret token for payload validation
   - **SSL verification**: Enable SSL verification
3. Which events would you like to trigger this webhook?
   - Select **Let me select individual events**:
     - ✅ **Pushes**
     - ✅ **Pull requests**
4. Click **Add webhook**.

Whenever a developer pushes code, the webhook fires, triggering VulScanAgent to assess and remediate vulnerabilities in the background.
