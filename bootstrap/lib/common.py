import json
import shutil
import subprocess
from pathlib import Path

from . import installer
from .output import BOLD, RESET, info


def parse_json_with_comments(content: str) -> dict | None:
    # Parse JSON content, stripping // comments. Returns None on parse error.
    lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
    try:
        return json.loads("\n".join(lines))
    except json.JSONDecodeError:
        return None


GLOBAL_SKILLS = [
    ("https://github.com/anthropics/skills", "skill-creator"),
    ("https://github.com/anthropics/skills", "frontend-design"),
    ("https://github.com/forrestchang/andrej-karpathy-skills", "karpathy-guidelines"),
]

MCP_SERVERS = list(installer.CONFIG.get("mcp_servers", {}).keys())

GITIGNORE_ENTRIES = [
    ".claude/",
    ".codex/",
    ".cursor/",
    ".gemini/",
    ".github/",
    ".opencode/",
    ".claptrap/",
    ".serena/",
]


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def detect_environments():
    # Detect which environments have their CLI tool installed.
    available = []
    for env, cfg in installer.CONFIG["environments"].items():
        cli = cfg.get("cli")
        if not cli:
            continue
        if shutil.which(cli):
            result = run_cmd([cli, "--version"])
            version = (
                result.stdout.strip().splitlines()[0]
                if result.stdout.strip()
                else "unknown"
            )
            available.append((env, cfg, version))
        else:
            info(f"Skipping {env} ({cli} not found)")
    return available


def select_environment():
    # Prompt user to select from detected environments.
    available = detect_environments()

    print("\nSelect installation target:\n")
    if len(available) > 1:
        print(f"  {BOLD}0{RESET}) All environments")
    for i, (env, cfg, version) in enumerate(available, 1):
        print(f"  {BOLD}{i}{RESET}) {env} ({cfg['cli']} {version})")
    print()

    # If only one environment detected, default to it
    default = "1" if len(available) == 1 else "0"

    while True:
        try:
            choice = (
                input(
                    f"Enter {'0-' if len(available) > 1 else ''}{len(available)} [{default}]: "
                ).strip()
                or default
            )
            idx = int(choice)
            if idx == 0 and len(available) > 1:
                return None
            if 1 <= idx <= len(available):
                return available[idx - 1][0]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nAborted.")
            raise SystemExit(1)
        max_val = len(available)
        low = 0 if len(available) > 1 else 1
        print(f"Please enter a number between {low} and {max_val}.")


def check_mcp_server_cli(server_name: str, cli: str) -> bool | None:
    from .mcp import check_mcp_server_cli as _check

    return _check(server_name, cli)


def check_mcp_server_config(server_name: str, config_path: Path) -> bool | None:
    from .mcp import check_mcp_server_config as _check

    return _check(server_name, config_path)


def check_mcp_server(server_name: str, cli: str | None = None) -> bool | None:
    from .mcp import check_mcp_server as _check

    return _check(server_name, cli)


