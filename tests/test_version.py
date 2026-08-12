import pytest
from nuitka_revenant.core import (
    parse_target_python_version,
    set_target_python_override,
    get_target_python_override,
    detect_python_version_from_pe
)


def test_parse_target_python_version_valid():
    assert parse_target_python_version("3.10") == (3, 10)
    assert parse_target_python_version("3.11") == (3, 11)
    assert parse_target_python_version((3, 12)) == (3, 12)


def test_parse_target_python_version_invalid():
    with pytest.raises(ValueError):
        parse_target_python_version("3.999")
    with pytest.raises(ValueError):
        parse_target_python_version("invalid")


def test_set_target_python_override():
    set_target_python_override("3.11")
    assert get_target_python_override() == (3, 11)
    set_target_python_override(None)
    assert get_target_python_override() is None


def test_detect_python_version_from_pe_bytes():
    dummy_pe_data = b"Some binary header python310.dll rest of data"
    ver = detect_python_version_from_pe(dummy_pe_data)
    assert ver == (3, 10)

    dummy_linux_data = b"header libpython3.11.so.1.0 footer"
    ver_linux = detect_python_version_from_pe(dummy_linux_data)
    assert ver_linux == (3, 11)
