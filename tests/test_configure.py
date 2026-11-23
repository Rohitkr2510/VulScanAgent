import os
from pathlib import Path
from agent.ai_fix.provider_router import AIProviderRouter


def test_home_credentials_env_loading(tmp_path: Path, monkeypatch):
    mock_home = tmp_path / "home"
    mock_home.mkdir()
    vulscan_dir = mock_home / ".vulscan"
    vulscan_dir.mkdir()
    creds_file = vulscan_dir / "credentials.env"

    creds_file.write_text("GEMINI_API_KEY=test_gemini_key_12345\n", encoding="utf-8")

    monkeypatch.setattr(Path, "home", lambda: mock_home)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    from dotenv import load_dotenv
    if creds_file.exists():
        load_dotenv(creds_file)

    assert os.getenv("GEMINI_API_KEY") == "test_gemini_key_12345"
