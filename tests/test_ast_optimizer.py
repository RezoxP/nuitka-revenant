import pytest
from nuitka_revenant.decompiler.ast_optimizer import (
    validate_and_format_code,
    repair_empty_blocks,
)


def test_repair_empty_blocks():
    raw_code = "def foo():\n\ndef bar():\n    x = 1"
    repaired = repair_empty_blocks(raw_code)
    assert "pass" in repaired


def test_validate_and_format_code_valid():
    raw_code = "def add(a, b):\n    return a + b\n    print('dead code')"
    formatted, is_valid, err = validate_and_format_code(raw_code)
    assert is_valid
    assert err is None
    assert "def add(a, b):" in formatted
    # Dead code after return should be eliminated by DeadCodeTransformer
    assert "print('dead code')" not in formatted


def test_validate_and_format_code_syntax_recovery():
    broken_code = "class MyClass:\n\ndef helper():\n    pass"
    formatted, is_valid, err = validate_and_format_code(broken_code)
    assert is_valid
    assert "class MyClass:" in formatted
