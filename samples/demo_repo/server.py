import os

def ping_host(host: str) -> int:
    """Vulnerable function executing system command with untrusted input."""
    return os.system("ping -c 1 " + host)

def safe_greet(name: str) -> str:
    """Safe function."""
    return f"Hello, {name}!"
