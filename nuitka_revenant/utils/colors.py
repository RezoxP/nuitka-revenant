import sys

class Colors:
    BLACK = '\033[30m'; RED = '\033[31m'; GREEN = '\033[32m'
    YELLOW = '\033[33m'; BLUE = '\033[34m'; MAGENTA = '\033[35m'
    CYAN = '\033[36m'; WHITE = '\033[37m'
    BRIGHT_RED = '\033[91m'; BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'; BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'; BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    BOLD = '\033[1m'; DIM = '\033[2m'; UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    BG_RED = '\033[41m'; BG_GREEN = '\033[42m'; BG_CYAN = '\033[46m'
    V1 = '\033[38;5;177m'; V2 = '\033[38;5;141m'; V3 = '\033[38;5;99m'
    V4 = '\033[38;5;93m'; V5 = '\033[38;5;55m'; V6 = '\033[38;5;54m'
    GREY = '\033[38;5;245m'; DKGREY = '\033[38;5;240m'

C = Colors()

if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        for attr in dir(C):
            if not attr.startswith('_'):
                setattr(C, attr, '')
