import pytest
from fastapi.testclient import TestClient
from dashboard.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_dashboard_homepage_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "VulScanAgent" in response.text
    assert "Autonomous Vulnerability Scan" in response.text


def test_api_jobs_list(client):
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_trigger_scan_endpoint(client):
    response = client.post(
        "/scan/trigger",
        data={
            "repo_url": "https://github.com/mock/repo",
            "branch": "main",
            "severity": "HIGH",
            "provider": "auto",
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["QUEUED", "RUNNING", "COMPLETED", "FAILED"]


def test_github_webhook_ping(client):
    response = client.post(
        "/api/webhook/github",
        headers={"x-github-event": "ping"},
        json={"zen": "Non-blocking is better than blocking."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "pong"


def test_github_webhook_push_event(client):
    push_payload = {
        "ref": "refs/heads/feature-x",
        "repository": {
            "clone_url": "https://github.com/example/test-repo.git",
            "html_url": "https://github.com/example/test-repo",
        },
    }
    response = client.post(
        "/api/webhook/github",
        headers={"x-github-event": "push"},
        json=push_payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "triggered"
    assert data["event"] == "push"
    assert data["branch"] == "feature-x"


def test_github_webhook_hmac_signature(client, monkeypatch):
    import hmac
    import hashlib
    import json

    secret = "my-super-secret-key"
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", secret)

    payload = {"ref": "refs/heads/main", "repository": {"clone_url": "https://github.com/test/repo"}}
    raw_bytes = json.dumps(payload).encode("utf-8")
    valid_sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()

    # 1. Missing header -> 401
    res = client.post("/api/webhook/github", headers={"x-github-event": "push"}, content=raw_bytes)
    assert res.status_code == 401

    # 2. Invalid signature -> 403
    res = client.post(
        "/api/webhook/github",
        headers={"x-github-event": "push", "x-hub-signature-256": "sha256=invalid"},
        content=raw_bytes,
    )
    assert res.status_code == 403

    # 3. Valid signature -> 200
    res = client.post(
        "/api/webhook/github",
        headers={"x-github-event": "push", "x-hub-signature-256": valid_sig},
        content=raw_bytes,
    )
    assert res.status_code == 200
    assert res.json()["status"] == "triggered"
