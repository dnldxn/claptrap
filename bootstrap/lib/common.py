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

MCP_SERVERS = ["serena", "context7", "snowflake"]

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
    # Check MCP server via CLI command (e.g., `opencode mcp list`).
    # Returns True if configured, False if not configured, None if CLI not found.
    try:
        result = run_cmd([cli, "mcp", "list"])
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if server_name.lower() in line.lower():
                    return "failed" not in line.lower()
            return False
    except FileNotFoundError:
        pass
    return None


def check_mcp_server_config(server_name: str, config_path: Path) -> bool | None:
    # Check MCP server via config file (e.g., ~/.copilot/mcp-config.json).
    # Returns True if configured, False if not configured, None if file not found.
    if not config_path.exists():
        return None
    try:
        content = parse_json_with_comments(config_path.read_text())
        if content and "mcpServers" in content:
            servers = content["mcpServers"]
            return server_name.lower() in [s.lower() for s in servers.keys()]
        return False
    except Exception:
        return None


def check_mcp_server(server_name: str, cli: str | None = None) -> bool | None:
    # Legacy function for backward compatibility - checks any available CLI.
    for cmd_cli in ["opencode", "claude", "agent", "codex", "gemini"]:
        result = check_mcp_server_cli(server_name, cmd_cli)
        if result is not None:
            return result
    return None
