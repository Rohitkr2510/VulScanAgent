# CLI Command Reference

`VulScanAgent` provides a command-line interface powered by Typer and Rich.

```
Usage: python main.py [OPTIONS] COMMAND [ARGS]...
```

---

## 1. Global Options

| Option | Type | Description |
|---|---|---|
| `--help` | flag | Show usage summary and exit. |

---

## 2. Commands

### 2.1 `scan`
Scan target codebase for vulnerabilities, apply AI fixes, run tests, and open Pull Requests.

```bash
python main.py scan [OPTIONS]
```

#### Options:

| Option | Flag | Default | Description |
|---|---|---|---|
| `--repo` | `-r` | `None` | GitHub repository URL (public or private). |
| `--branch` | `-b` | `main` | Target branch to clone and base PR on. |
| `--config` | `-c` | `config/config.yaml` | Path to custom YAML configuration file. |
| `--local` | `-l` | `None` | Run directly on local directory instead of cloning remote git repo. |
| `--severity` | `-s` | `MEDIUM` | Minimum severity threshold: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. |
| `--provider` | `-p` | `auto` | Force AI provider: `openai`, `anthropic`, `google`, `auto`. |

#### Examples:
```bash
# Scan a remote private repository with Claude 3.5 Sonnet
python main.py scan -r https://github.com/enterprise/backend -b main -s HIGH -p anthropic

# Scan local project folder with Google Gemini
python main.py scan -l ./my-microservice -s MEDIUM -p google

# Use custom configuration file
python main.py scan -c ./config/production.yaml
```

---

### 2.2 `dashboard`
Launch the real-time FastAPI web dashboard and GitHub Webhook server.

```bash
python main.py dashboard [OPTIONS]
```

#### Options:

| Option | Flag | Default | Description |
|---|---|---|---|
| `--host` | `-h` | `127.0.0.1` | Network interface to bind (use `0.0.0.0` for Docker). |
| `--port` | `-p` | `8000` | Port to listen on. |
| `--reload` | `-r` | `False` | Enable auto-reloading on code changes (development). |

#### Example:
```bash
python main.py dashboard --host 0.0.0.0 --port 8000
```

---

### 2.3 `verify-keys`
Inspect and validate configured credentials and API keys in your environment.

```bash
python main.py verify-keys
```

#### Example Output:
```
🔑 Checking API Keys and Connectivity

GitHub Token: Found
Available AI Providers: anthropic, openai, google
Ready to remediate code!
```
