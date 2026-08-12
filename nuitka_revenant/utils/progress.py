import time
from .colors import C

class ProgressBar:
    def __init__(self, total, desc="Processing", width=40, spinner='fire'):
        self.total = max(total, 1)
        self.current = 0
        self.desc = desc
        self.width = width
        self.start_time = time.time()
        self.spinner_frames = ['*', '+', 'x', '+']
        self.frame = 0

    def update(self, n=1):
        self.current = min(self.current + n, self.total)
        self.frame = (self.frame + 1) % len(self.spinner_frames)
        self._render()

    def _render(self):
        progress = self.current / self.total
        filled = int(self.width * progress)
        bar = ""
        for i in range(self.width):
            if i < filled:
                if i < self.width * 0.3: bar += f"{C.BRIGHT_RED}#"
                elif i < self.width * 0.6: bar += f"{C.BRIGHT_YELLOW}#"
                else: bar += f"{C.BRIGHT_GREEN}#"
            else: bar += f"{C.DIM}."
        bar += C.RESET
        elapsed = time.time() - self.start_time
        eta = (elapsed / self.current * (self.total - self.current)) if self.current > 0 else 0
        s = self.spinner_frames[self.frame]
        status = (f"\r{C.BOLD}{C.BRIGHT_CYAN}[{s}]{C.RESET} "
                  f"{C.BRIGHT_WHITE}{self.desc}{C.RESET} [{bar}] "
                  f"{C.BRIGHT_YELLOW}{progress*100:5.1f}%{C.RESET} "
                  f"{C.DIM}({self.current}/{self.total}){C.RESET} "
                  f"{C.BRIGHT_MAGENTA}ETA: {int(eta)}s{C.RESET}")
        print(status, end='', flush=True)

    def finish(self, message="Done!"):
        print(f"\r{' ' * 120}\r", end='')
        print(f"{C.BRIGHT_GREEN}[OK]{C.RESET} {C.BRIGHT_WHITE}{self.desc}{C.RESET}: {C.BRIGHT_GREEN}{message}{C.RESET}")
