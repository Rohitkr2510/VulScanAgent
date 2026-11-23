import pytest
from pathlib import Path
from agent.security.guardrails import AgentGuardrails, SecurityViolationError


def test_path_traversal_blocked(tmp_path):
    repo_dir = tmp_path / "my_repo"
    repo_dir.mkdir()

    # Valid internal path succeeds
    safe_path = AgentGuardrails.validate_safe_path(repo_dir, "app/routes/api.py")
    assert str(safe_path).startswith(str(repo_dir.resolve()))

    # Directory escape attempts must be rejected
    with pytest.raises(SecurityViolationError):
        AgentGuardrails.validate_safe_path(repo_dir, "../../etc/passwd")

    with pytest.raises(SecurityViolationError):
        AgentGuardrails.validate_safe_path(repo_dir, "../outside.txt")


def test_command_sanitization():
    # Safe command passes
    safe_cmd = ["pytest", "-v", "tests/"]
    assert AgentGuardrails.sanitize_command(safe_cmd) == safe_cmd

    # Dangerous destructive commands blocked
    with pytest.raises(SecurityViolationError):
        AgentGuardrails.sanitize_command(["rm", "-rf", "/"])

    # Shell chaining tokens blocked
    with pytest.raises(SecurityViolationError):
        AgentGuardrails.sanitize_command(["pytest", "&&", "cat", "/etc/shadow"])

    with pytest.raises(SecurityViolationError):
        AgentGuardrails.sanitize_command(["python", ";", "whoami"])


def test_secret_redaction():
    text_with_secrets = (
        "Found AWS key AKIA1234567890ABCDEF and GitHub token "
        "ghp_123456789012345678901234567890123456 in source. "
        "Also OpenAI sk-abcdef12345678901234567890123456."
    )
    redacted = AgentGuardrails.redact_secrets(text_with_secrets)

    assert "AKIA1234567890ABCDEF" not in redacted
    assert "ghp_123456789012345678901234567890123456" not in redacted
    assert "sk-abcdef12345678901234567890123456" not in redacted
    assert "AKIA[REDACTED_AWS_KEY]" in redacted
    assert "[REDACTED_GITHUB_TOKEN]" in redacted
    assert "sk-[REDACTED_API_KEY]" in redacted


def test_patch_size_limit():
    small_content = "def hello(): pass"
    AgentGuardrails.validate_patch_size(small_content, max_chars=100)

    massive_content = "A" * 150
    with pytest.raises(SecurityViolationError):
        AgentGuardrails.validate_patch_size(massive_content, max_chars=100)
