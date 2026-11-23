import pytest
from pathlib import Path
from agent.ai_fix.fix_engine import FixEngine
from agent.ai_fix.provider_router import AIProviderRouter


def test_ast_syntax_validation():
    router = AIProviderRouter()
    engine = FixEngine(router)

    valid_py = "def hello():\n    return 'world'\n"
    invalid_py = "def hello() return 'world'"

    is_valid, err = engine._validate_syntax("test.py", valid_py)
    assert is_valid
    assert err is None

    is_valid, err = engine._validate_syntax("test.py", invalid_py)
    assert not is_valid
    assert "SyntaxError" in err


def test_llm_response_parsing():
    router = AIProviderRouter()
    engine = FixEngine(router)

    response = """Here is the fix:

### EXPLANATION
Parameterized queries were introduced using db placeholders to eliminate SQL injection.

### FIXED_FILE
```python
import sqlite3

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
"""
    explanation, code = engine._parse_llm_response(response)
    assert "Parameterized queries" in explanation
    assert "cursor.execute(" in code
    assert "user_id,)" in code
