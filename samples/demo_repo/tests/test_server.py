from server import safe_greet

def test_safe_greet():
    assert safe_greet("Security") == "Hello, Security!"
