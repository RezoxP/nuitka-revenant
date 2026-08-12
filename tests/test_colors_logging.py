import pytest
from nuitka_revenant.utils import Colors, C
from nuitka_revenant.utils.logging import log, log_ok, log_err, log_warn, log_fire, print_section
from nuitka_revenant.utils.progress import ProgressBar


def test_colors_presence():
    assert hasattr(C, "RESET")
    assert hasattr(C, "BRIGHT_GREEN")
    assert hasattr(C, "BOLD")


def test_logging_functions(capsys):
    log("Test message")
    log_ok("Success message")
    log_err("Error message")
    log_warn("Warning message")
    log_fire("Fire message")
    print_section("SECTION TITLE")

    captured = capsys.readouterr()
    assert "Test message" in captured.out
    assert "Success message" in captured.out
    assert "Error message" in captured.out
    assert "Warning message" in captured.out
    assert "Fire message" in captured.out
    assert "SECTION TITLE" in captured.out


def test_progress_bar(capsys):
    pb = ProgressBar(total=10, desc="Testing Progress")
    pb.update(5)
    pb.finish("Completed")

    captured = capsys.readouterr()
    assert "Testing Progress" in captured.out
    assert "Completed" in captured.out
