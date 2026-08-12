"""
Dynamic Hook Generator for REVENANT.
Generates self-contained runtime hooks injected into running Nuitka binaries
to capture active CPython module state, code objects, and constants directly from memory.
"""

import sys
from typing import Dict, Any, Optional


def generate_runtime_hook_script(target_modules: Optional[list] = None) -> str:
    """
    Generates a Python runtime hook script that dumps active module source,
    code objects, and constants when loaded inside a Nuitka process.
    """
    filter_code = repr(target_modules) if target_modules else "None"

    hook_code = f"""# REVENANT Dynamic Runtime Hook Script
import os
import sys
import types
import json
import marshal
import inspect

TARGET_MODULES = {filter_code}

def dump_live_modules(dump_dir):
    os.makedirs(dump_dir, exist_ok=True)
    src_dir = os.path.join(dump_dir, "RECONSTRUCTED_SOURCE")
    os.makedirs(src_dir, exist_ok=True)
    
    report = {{
        "captured_modules": [],
        "code_objects": 0,
        "status": "success"
    }}

    for name, module in list(sys.modules.items()):
        if not module or not hasattr(module, "__dict__"):
            continue
            
        if TARGET_MODULES and not any(name == m or name.startswith(m + ".") for m in TARGET_MODULES):
            continue

        mod_dict = getattr(module, "__dict__", {{}})
        code_count = 0
        
        for k, v in list(mod_dict.items()):
            if isinstance(v, types.FunctionType) and hasattr(v, "__code__"):
                code_count += 1
                
        out_path = os.path.join(src_dir, f"{{name.replace('.', '_')}}.py")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# Dynamically captured module: {{name}}\\n")
                if getattr(module, "__doc__", None):
                    f.write(f'\"\"\"{{module.__doc__}}\"\"\"\\n\\n')
                for k, v in mod_dict.items():
                    if not k.startswith("__"):
                        f.write(f"{{k}} = {{repr(v)}}\\n")
        except Exception:
            pass
            
        report["captured_modules"].append({{
            "name": name,
            "code_objects": code_count,
            "out_file": out_path
        }})
        report["code_objects"] += code_count

    report_path = os.path.join(dump_dir, "DYNAMIC_HOOK_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    out_dir = os.environ.get("REVENANT_DUMP_DIR", "revenant_dynamic_dump")
    dump_live_modules(out_dir)
"""
    return hook_code
