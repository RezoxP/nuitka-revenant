"""
Command-line interface entry point for REVENANT.
"""

import os
import sys
import argparse
import platform
from typing import Optional, List

from .utils.colors import C
from .utils.logging import log, log_ok, log_err, log_warn, log_fire, print_section


def build_arg_parser() -> argparse.ArgumentParser:
    _script_dir = os.path.dirname(os.path.abspath(__file__))
    _default_dll = os.path.join(
        _script_dir,
        "hook64.dll" if platform.machine().endswith("64") else "hook32.dll"
    )
    _default_hook = os.path.join(_script_dir, "__hook__.py")

    parser = argparse.ArgumentParser(
        description="REVENANT - Static Nuitka source recovery engine",
        epilog="""
Examples:
  # Static source recovery
  nuitka-revenant --source authorized_app.exe --emit-all-source out_source

  # List modules inside target
  nuitka-revenant --source authorized_app.exe --list-modules

  # Decompile a single module
  nuitka-revenant --source authorized_app.exe --live-decompile __main__ --emit-source main.py
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--source', '-s', dest='source_flag', default=None, metavar='FILE',
                        help='Authorized .exe or .dll compiled with Nuitka')
    parser.add_argument('target', nargs='?', default=None,
                        help='Authorized .exe or .dll (positional - same as --source)')
    parser.add_argument('--output', '-o', default=None, help='Output directory')
    parser.add_argument('--all', '-a', action='store_true', help='Also analyze library modules')
    parser.add_argument('--only', default=None, metavar='MODS',
                        help='Comma-separated module names/globs to process')
    parser.add_argument('--list-modules', action='store_true', dest='list_modules',
                        help='List all module names in the blob and exit')
    parser.add_argument('--filter', default=None, metavar='STR', dest='filter_str',
                        help='Filter module list')
    parser.add_argument('--live-decompile', default=None, metavar='MODULE[:0xVA]', dest='live_decompile',
                        help='Native->Python for ONE module')
    parser.add_argument('--emit-source', default=None, metavar='OUT.py', nargs='?', const='-',
                        dest='emit_source', help='Emit single module source')
    parser.add_argument('--emit-all-source', default=None, metavar='OUT_DIR', dest='emit_all_source',
                        help='Emit all modules to directory')
    parser.add_argument('--emit-fast', action='store_true', dest='emit_fast',
                        help='Fast emission profile')
    parser.add_argument('--refine-partial', action='store_true', dest='refine_partial',
                        help='Refine partial modules from previous run')
    parser.add_argument('--target-python', default=None, metavar='VER', dest='target_python',
                        help='Override target Python version (e.g. 3.11)')
    parser.add_argument('--clean', action='store_true', dest='clean_source',
                        help='Clean recovery comments from output')

    # Dynamic options
    parser.add_argument('--inject', action='store_true', help='Enable dynamic injection phase')
    parser.add_argument('--pid', type=int, default=None, help='Target process ID for injection')
    parser.add_argument('--launch', action='store_true', help='Launch target process before injection')
    parser.add_argument('--dll', default=_default_dll, help='Hook DLL path')
    parser.add_argument('--hook-script', default=_default_hook, help='Python hook script path')
    parser.add_argument('--dump-timeout', type=int, default=120, help='Max seconds to wait for dump')

    return parser


def main(args_list: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(args_list)

    target = args.source_flag or args.target
    if not target and not args_list:
        parser.print_help()
        return 0

    # Dynamic resource auto-tuning for reliability
    if target and os.path.isfile(target):
        from .dynamic.auto_tuner import DynamicAutoTuner
        profile = DynamicAutoTuner.calculate_analysis_profile(target)
        if not getattr(args, 'live_max_funcs', None):
            args.live_max_funcs = profile['live_max_funcs']
        if not getattr(args, 'live_max_bytes', None):
            args.live_max_bytes = profile['live_max_bytes']

    # Delegate to nuitka_decompiler module execution logic
    try:
        import nuitka_decompiler
        return nuitka_decompiler._legacy_main_with_args(args)
    except Exception as e:
        log_err(f"Execution error: {e}")
        return 1
