import os
import pytest
from nuitka_revenant.dynamic import (
    generate_runtime_hook_script,
    DynamicProcessInjector,
    DynamicAutoTuner,
)


def test_generate_runtime_hook_script():
    hook_code = generate_runtime_hook_script(["__main__", "myapp"])
    assert "TARGET_MODULES = ['__main__', 'myapp']" in hook_code
    assert "dump_live_modules" in hook_code


def test_dynamic_auto_tuner(tmp_path):
    dummy_bin = tmp_path / "test.exe"
    dummy_bin.write_bytes(b"\x00" * 1024 * 1024)

    profile = DynamicAutoTuner.calculate_analysis_profile(str(dummy_bin))
    assert "live_max_funcs" in profile
    assert profile["live_max_funcs"] > 0
    assert "system_resources" in profile


def test_dynamic_process_injector(tmp_path):
    out_dir = str(tmp_path / "dynamic_out")
    injector = DynamicProcessInjector(out_dir=out_dir, timeout=1)
    assert injector.out_dir == out_dir
    assert injector.timeout == 1
