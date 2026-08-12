import pytest
import sys
from unittest.mock import patch
from nuitka_revenant.cli import build_arg_parser, main


def test_build_arg_parser():
    parser = build_arg_parser()
    args = parser.parse_args(["--source", "target.exe", "--list-modules"])
    assert (args.source_flag or args.target) == "target.exe"
    assert args.list_modules is True


def test_main_help(capsys):
    with patch.object(sys, "argv", ["nuitka-revenant", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "REVENANT" in captured.out or "usage:" in captured.out
