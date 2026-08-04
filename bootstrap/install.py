from pathlib import Path
import json
import sys

###################################################################################################
# Config
###################################################################################################
PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
OPENCODE_ROOT = HOME / ".config/opencode"

PLUGIN_ROOT = PROJECT_ROOT / "opencode/claptrap-plugin"

INSTRUCTIONS_LINK = OPENCODE_ROOT / "claptrap/instructions.md"
INSTRUCTIONS_ENTRY = "~/.config/opencode/claptrap/instructions.md"

LINKS = {
    INSTRUCTIONS_LINK: PLUGIN_ROOT / "instructions.md",
    # plugin.ts imports ./logic; Bun resolves that against the symlink's real
    # path in the repo, so logic.ts needs no link of its own.
    OPENCODE_ROOT / "claptrap/plugin.ts": PLUGIN_ROOT / "plugin.ts",
    OPENCODE_ROOT / "agents/claptrap": PLUGIN_ROOT / "agents",
    OPENCODE_ROOT / "commands/claptrap": PLUGIN_ROOT / "commands",
}

SWEEP_ROOTS = [
    OPENCODE_ROOT / "agents",
    OPENCODE_ROOT / "skills",
    OPENCODE_ROOT / "commands",
    OPENCODE_ROOT / "claptrap",
    HOME / ".claude/agents",
    HOME / ".claude/skills",
    HOME / ".claude/commands",
    HOME / ".cursor/agents",
    HOME / ".cursor/skills",
    HOME / ".cursor/commands",
]

###################################################################################################
# Output Formatting
###################################################################################################
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def success(msg): print(f"{GREEN}✓{RESET} {msg}")
def warning(msg): print(f"{YELLOW}⚠{RESET} {msg}")
def info(msg): print(f"{CYAN}→{RESET} {msg}")
def header(msg): print(f"\n{BOLD}📦 {msg}{RESET}")


def fail(msg):
    print(f"{YELLOW}✗{RESET} {msg}", file=sys.stderr)
    raise SystemExit(1)


###################################################################################################
# Symlink helpers
###################################################################################################
def resolves_into_repo(path: Path) -> bool:
    try: target = path.resolve(strict=False)
    except OSError: return False
    return target == PROJECT_ROOT or PROJECT_ROOT in target.parents


def remove_repo_link(path: Path) -> bool:
    if not path.is_symlink() or not resolves_into_repo(path):
        return False
    path.unlink()
    print(f"Removed repo-owned symlink: {path}")
    return True


def prepare_claptrap_directory() -> None:
    path = OPENCODE_ROOT / "claptrap"
    if path.is_symlink():
        known_conflict = (OPENCODE_ROOT / "commands").resolve(strict=False)
        if not resolves_into_repo(path) and path.resolve(strict=False) != known_conflict:
            fail(f"Refusing to replace non-repo claptrap symlink: {path}")
        path.unlink()
        info(f"Removed conflicting claptrap symlink: {path}")
    elif path.exists() and not path.is_dir():
        fail(f"Cannot create {path}: a non-directory already exists")
    path.mkdir(parents=True, exist_ok=True)


def sweep_repo_links() -> None:
    for root in SWEEP_ROOTS:
        if not root.exists() or not root.is_dir():
            continue
        for entry in list(root.iterdir()):
            remove_repo_link(entry)


def link(source: Path, target: Path) -> None:
    source = source.resolve()
    if not source.exists(): fail(f"Missing repo source: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink():
        if not resolves_into_repo(target):
            fail(f"Refusing to replace non-repo symlink: {target}")
        target.unlink()
    elif target.exists():
        fail(f"Refusing to replace non-repo file or directory: {target}")
    target.symlink_to(source, target_is_directory=source.is_dir())
    success(f"Linked {target} -> {source}")


###################################################################################################
# OpenCode configuration guidance
###################################################################################################
def config_contains(path: Path, key: str, value: str) -> bool:
    if not path.exists(): return False
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return value in path.read_text(errors="replace")
    return any(item == value or (isinstance(item, list) and item and item[0] == value) for item in data.get(key, []))


def print_config_warnings() -> None:
    config = OPENCODE_ROOT / "opencode.json"
    # `instructions` entries resolve against the *project* cwd, not the config
    # file, so a relative "./claptrap/instructions.md" silently loads nothing
    # outside ~/.config/opencode. "~/" and absolute paths both work; accept
    # either so an existing absolute entry keeps validating.
    missing_instructions = not any(
        config_contains(config, "instructions", value)
        for value in (INSTRUCTIONS_ENTRY, str(INSTRUCTIONS_LINK))
    )
    missing_plugin = not config_contains(config, "plugin", "./claptrap/plugin.ts")
    if missing_instructions or missing_plugin:
        warning("Add these entries to ~/.config/opencode/opencode.json, merging with existing arrays:")
        print(f'  "instructions": ["{INSTRUCTIONS_ENTRY}"],')
        print('  "plugin": ["./claptrap/plugin.ts"]')
    else:
        success("OpenCode instructions and plugin are registered")
    config_text = config.read_text(errors="replace") if config.exists() else ""
    for alias, label in (("skill-gardener", "Skill Gardener"), ("skill-harvester", "Skill Harvester")):
        if alias in config_text:
            success(f"{alias} model is registered")
        else:
            warning(f"Add the {alias} model to provider.9router.models in opencode.json:")
            print(f'  "{alias}": {{"name": "{label}"}}')


###################################################################################################
# Main
###################################################################################################
def main() -> None:
    header("Installing Claptrap OpenCode continuous learning")
    prepare_claptrap_directory()
    sweep_repo_links()
    for target, source in LINKS.items():
        link(source, target)
    print_config_warnings()
    success("Done.")


if __name__ == "__main__":
    main()
