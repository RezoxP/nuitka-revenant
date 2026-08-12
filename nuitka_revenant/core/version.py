"""
Python target ABI version detection and override parsing for REVENANT.
"""

import re
from typing import Optional, Tuple, Union

SUPPORTED_TARGET_PYTHONS = {
    (2, 7),
    (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9),
    (3, 10), (3, 11), (3, 12), (3, 13), (3, 14)
}

_TARGET_PYTHON_OVERRIDE: Optional[Tuple[int, int]] = None


def parse_target_python_version(version: Union[str, Tuple[int, int]]) -> Tuple[int, int]:
    """Parses MAJOR.MINOR version strings or tuples."""
    if isinstance(version, str):
        match = re.fullmatch(r'\s*(\d+)\.(\d+)\s*', version)
        if not match:
            raise ValueError("target Python must be exactly MAJOR.MINOR")
        parsed = (int(match.group(1)), int(match.group(2)))
    else:
        try:
            parsed = (int(version[0]), int(version[1]))
        except Exception as exc:
            raise ValueError("target Python must be a (major, minor) pair") from exc

    if parsed not in SUPPORTED_TARGET_PYTHONS:
        raise ValueError(
            f"unsupported target Python {parsed[0]}.{parsed[1]}; "
            "supported layouts are 2.7 and 3.0 through 3.14"
        )
    return parsed


def set_target_python_override(version: Optional[Union[str, Tuple[int, int]]]):
    """Sets the global target ABI override."""
    global _TARGET_PYTHON_OVERRIDE
    if version is None:
        _TARGET_PYTHON_OVERRIDE = None
        return
    _TARGET_PYTHON_OVERRIDE = parse_target_python_version(version)


def get_target_python_override() -> Optional[Tuple[int, int]]:
    return _TARGET_PYTHON_OVERRIDE


def detect_python_version_from_pe(pe_data: bytes) -> Optional[Tuple[int, int]]:
    """Detects embedded CPython ABI from PE/ELF data."""
    try:
        import pefile
        pe = pefile.PE(data=pe_data)
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode('ascii', errors='replace').lower()
                m = re.fullmatch(r'python(\d)(\d{1,2})(?:t)?(?:_d)?\.dll', dll_name)
                if m:
                    try:
                        return parse_target_python_version(m.groups())
                    except ValueError:
                        continue
        for section in pe.sections:
            sec_data = section.get_data()
            for match in re.finditer(rb'python(\d)(\d{1,2})(?:t)?(?:_d)?\.dll', sec_data, re.IGNORECASE):
                try:
                    return parse_target_python_version(match.groups())
                except ValueError:
                    continue
    except Exception:
        pass

    try:
        for pattern in (
            rb'python(\d)(\d{1,2})(?:t)?(?:_d)?\.dll',
            rb'libpython(\d)\.(\d{1,2})(?:t)?(?:m|d)?(?:\.so(?:\.\d+)*|\.dylib|\x00)',
            rb'Python\.framework/Versions/(\d)\.(\d{1,2})'
        ):
            match = re.search(pattern, pe_data or b'', re.IGNORECASE)
            if match:
                try:
                    return parse_target_python_version(match.groups())
                except ValueError:
                    continue
    except Exception:
        pass

    return None
