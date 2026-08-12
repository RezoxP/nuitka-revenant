"""
Multi-Platform Dynamic Process Launcher & Hook Injector for REVENANT.
Supports Windows DLL Injection, Linux LD_PRELOAD, and macOS DYLD_INSERT_LIBRARIES.
"""

import os
import sys
import time
import subprocess
from typing import Optional, Dict, Any, List
from ..utils.logging import log, log_ok, log_err, log_warn


class DynamicProcessInjector:
    """
    Multi-platform dynamic launcher and process injector.
    """
    def __init__(self, out_dir: str = "dynamic_output", timeout: int = 120):
        self.out_dir = out_dir
        self.timeout = timeout
        os.makedirs(self.out_dir, exist_ok=True)

    def launch_with_preload(self, executable_path: str, hook_library_path: str, env_vars: Optional[Dict[str, str]] = None) -> Optional[subprocess.Popen]:
        """
        Launches executable under Linux LD_PRELOAD or macOS DYLD_INSERT_LIBRARIES.
        """
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        env["REVENANT_DUMP_DIR"] = self.out_dir

        if sys.platform.startswith("linux"):
            env["LD_PRELOAD"] = hook_library_path
            log(f"Launching {executable_path} with LD_PRELOAD={hook_library_path}...")
        elif sys.platform == "darwin":
            env["DYLD_INSERT_LIBRARIES"] = hook_library_path
            log(f"Launching {executable_path} with DYLD_INSERT_LIBRARIES={hook_library_path}...")
        else:
            log_err("Preload dynamic launch is supported on Linux and macOS.")
            return None

        try:
            proc = subprocess.Popen([executable_path], env=env)
            log_ok(f"Process launched with PID {proc.pid}")
            return proc
        except Exception as e:
            log_err(f"Failed to launch process: {e}")
            return None

    def inject_windows_dll(self, pid: int, dll_path: str) -> bool:
        """
        Injects hook DLL into target Windows process.
        """
        if sys.platform != "win32":
            log_warn("Windows DLL injection requested on non-Windows host.")
            return False

        try:
            import ctypes
            from ctypes import wintypes

            PROCESS_ALL_ACCESS = 0x1F0FFF
            MEM_COMMIT = 0x1000
            MEM_RESERVE = 0x2000
            PAGE_READWRITE = 0x04

            kernel32 = ctypes.windll.kernel32
            h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            if not h_process:
                log_err(f"Could not open target PID {pid}")
                return False

            dll_bytes = dll_path.encode("utf-16le") + b"\x00\x00"
            arg_address = kernel32.VirtualAllocEx(
                h_process, None, len(dll_bytes), MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
            )
            
            written = ctypes.c_size_t(0)
            kernel32.WriteProcessMemory(h_process, arg_address, dll_bytes, len(dll_bytes), ctypes.byref(written))

            h_kernel32 = kernel32.GetModuleHandleW("kernel32.dll")
            h_loadlibrary = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryW")

            thread_id = wintypes.DWORD(0)
            h_thread = kernel32.CreateRemoteThread(
                h_process, None, 0, h_loadlibrary, arg_address, 0, ctypes.byref(thread_id)
            )

            if h_thread:
                log_ok(f"Successfully injected DLL into PID {pid}")
                kernel32.CloseHandle(h_thread)
                kernel32.CloseHandle(h_process)
                return True
            else:
                log_err("Failed to create remote thread for injection")
                kernel32.CloseHandle(h_process)
                return False

        except Exception as e:
            log_err(f"DLL Injection error: {e}")
            return False

    def wait_for_dump(self, dump_dir: Optional[str] = None) -> bool:
        """
        Waits up to self.timeout seconds for dynamic dump artifacts to appear.
        """
        target_dir = dump_dir or self.out_dir
        start_time = time.time()
        log(f"Waiting up to {self.timeout}s for dynamic dump in {target_dir}...")

        while time.time() - start_time < self.timeout:
            report_file = os.path.join(target_dir, "DYNAMIC_HOOK_REPORT.json")
            if os.path.exists(report_file):
                log_ok(f"Dynamic dump captured successfully in {target_dir}")
                return True
            time.sleep(1)

        log_warn("Timeout waiting for dynamic dump.")
        return False
