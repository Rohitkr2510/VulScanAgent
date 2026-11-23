# Contributing to VulScanAgent

Thank you for your interest in contributing to **VulScanAgent**!

---

## 1. Local Development Setup

1. Fork and clone the repository.
2. Initialize virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

---

## 2. Code Style & Standards

- **Formatting**: Adhere to PEP 8 style standards.
- **Type Annotations**: All agent and scanner methods must include type hints (`Path`, `Optional`, `List`, `Dict`).
- **Defensive Design**: Never execute raw commands with `shell=True` without input sanitization.
- **AST Pre-validation**: New scanner/fix logic must validate code syntax before saving.

---

## 3. Running Tests

Run the full pytest suite before submitting any Pull Request:

```bash
pytest -v
```

All 21+ automated unit and integration tests must pass.

---

## 4. Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-new-scanner`.
2. Commit your changes with conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`).
3. Ensure all tests pass.
4. Submit a Pull Request targeting the `main` branch with a clear description of changes.
