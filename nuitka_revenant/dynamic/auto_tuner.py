"""
Dynamic Configuration & Resource Auto-Tuner for REVENANT.
Dynamically calculates optimal RAM budgets, disasm limits, and AST pass parameters
based on binary size and available host CPU/RAM resources.
"""

import os
import psutil
from typing import Dict, Any


class DynamicAutoTuner:
    """
    Auto-tunes REVENANT analysis budgets dynamically.
    """
    @staticmethod
    def get_system_resources() -> Dict[str, Any]:
        """
        Queries available host RAM and CPU core count.
        """
        try:
            mem = psutil.virtual_memory()
            total_ram_mb = mem.total // (1024 * 1024)
            available_ram_mb = mem.available // (1024 * 1024)
        except Exception:
            total_ram_mb = 8192
            available_ram_mb = 4096

        cpu_count = os.cpu_count() or 4
        return {
            "total_ram_mb": total_ram_mb,
            "available_ram_mb": available_ram_mb,
            "cpu_count": cpu_count
        }

    @classmethod
    def calculate_analysis_profile(cls, binary_path: str) -> Dict[str, Any]:
        """
        Dynamically calculates max functions, disasm limits, and recursion depth.
        """
        sys_res = cls.get_system_resources()
        avail_ram = sys_res["available_ram_mb"]

        try:
            file_size_mb = os.path.getsize(binary_path) // (1024 * 1024)
        except Exception:
            file_size_mb = 10

        # Dynamic profile calculation
        if avail_ram > 16384: # >16GB RAM available
            max_funcs = 2500
            max_bytes = 131072
            body_bytes = 65536
            recursion_depth = 64
        elif avail_ram > 8192: # >8GB RAM available
            max_funcs = 1200
            max_bytes = 65536
            body_bytes = 32768
            recursion_depth = 32
        else: # Low RAM environment
            max_funcs = 500
            max_bytes = 32768
            body_bytes = 16384
            recursion_depth = 16

        # Adjust for very large binaries (>50MB)
        if file_size_mb > 50:
            max_funcs = int(max_funcs * 1.5)

        return {
            "live_max_funcs": max_funcs,
            "live_max_bytes": max_bytes,
            "live_body_bytes": body_bytes,
            "live_recursion_depth": recursion_depth,
            "system_resources": sys_res,
            "binary_size_mb": file_size_mb
        }
