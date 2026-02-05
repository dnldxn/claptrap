GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def success(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


def info(msg):
    print(f"{CYAN}→{RESET} {msg}")


def header(msg):
    print(f"\n{BOLD}📦 {msg}{RESET}")


def step(num, msg):
    print(f"\n{BOLD}[{num}]{RESET} {msg}")
