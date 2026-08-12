from .colors import C

def print_section(title: str):
    line = "=" * 70
    print(f"\n{C.V3}{line}{C.RESET}")
    print(f"{C.BOLD}{C.V1}  {title}{C.RESET}")
    print(f"{C.V3}{line}{C.RESET}\n")

def log(msg: str):
    print(f"{C.BRIGHT_CYAN}[**]{C.RESET} {msg}")

def log_ok(msg: str):
    print(f"{C.BRIGHT_GREEN}[OK]{C.RESET} {msg}")

def log_err(msg: str):
    print(f"{C.BRIGHT_RED}[!!]{C.RESET} {msg}")

def log_warn(msg: str):
    print(f"{C.BRIGHT_YELLOW}[!!]{C.RESET} {msg}")

def log_fire(msg: str):
    print(f"{C.BRIGHT_RED}[>>]{C.RESET} {C.BOLD}{msg}{C.RESET}")
