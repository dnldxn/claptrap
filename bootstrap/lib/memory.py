import json
import shutil
from datetime import datetime
from pathlib import Path

from . import installer
from .common import parse_json_with_comments
from .output import info, success, warning

ENFORCEMENT_PLUGIN = "claptrap-enforcement.ts"


def _build_hook_entry(env: str, hook_def: dict) -> dict:
    # Format a single hook entry based on env-specific schema.
    cmd = hook_def["command"]
    matcher = hook_def.get("matcher", "*")

    if env == "claude":
        return {"matcher": matcher, "hooks": [{"type": "command", "command": cmd}]}
    if env == "github-copilot":
        return {"type": "command", "bash": cmd}
    if env == "cursor":
        entry = {"command": cmd}
        if matcher != "*":
            entry["matcher"] = matcher
        return entry
    return {"matcher": matcher, "command": cmd}


def generate_hooks_config(env: str):
    env_cfg = installer.CONFIG["environments"].get(env, {})
    hooks_cfg = env_cfg.get("hooks")

    if not hooks_cfg or hooks_cfg is False or env == "opencode":
        return None

    events = hooks_cfg.get("events", {})
    common_hooks = installer.CONFIG.get("hooks", {})
    if not events or not common_hooks:
        return None

    hooks_output = {}
    for canonical_name, hook_def in common_hooks.items():
        event_name = events.get(canonical_name)
        if event_name:
            hooks_output[event_name] = [_build_hook_entry(env, hook_def)]

    if not hooks_output:
        return None
    if env in {"github-copilot", "cursor"}:
        return {"version": 1, "hooks": hooks_output}
    return {"hooks": hooks_output}


def backup_config(config_path: Path):
    if not config_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.with_suffix(f".{timestamp}.backup")
    shutil.copy2(config_path, backup_path)
    return backup_path


def install_hooks(env: str, target_dir: Path):
    env_cfg = installer.CONFIG["environments"].get(env, {})
    hooks_cfg = env_cfg.get("hooks")

    if not hooks_cfg or hooks_cfg is False:
        warning(f"{env} doesn't support hooks (soft enforcement only)")
        return

    # OpenCode uses plugin system instead of JSON hooks
    if env == "opencode":
        install_opencode_plugin(env_cfg)
        return

    config = generate_hooks_config(env)
    if not config:
        return

    project_dir = hooks_cfg.get("project_dir")
    if project_dir:
        config_path = target_dir / project_dir / hooks_cfg["file"]
    else:
        root = Path(env_cfg["root"]).expanduser()
        config_path = root / hooks_cfg["file"]

    if config_path.exists():
        backup_path = backup_config(config_path)
        if backup_path:
            info(f"Backed up existing config -> {backup_path.name}")

    if config_path.exists():
        existing = parse_json_with_comments(config_path.read_text())
        if existing:
            existing.setdefault("hooks", {}).update(config.get("hooks", {}))
            config = existing
        else:
            warning(
                f"Could not parse existing {config_path.name} - creating new config"
            )

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    success(f"Configured memory hooks -> {config_path}")


def install_opencode_plugin(env_cfg: dict):
    claptrap_path = Path(__file__).resolve().parent.parent.parent
    src = claptrap_path / "src" / "plugins" / ENFORCEMENT_PLUGIN
    if not src.exists():
        warning(f"Enforcement plugin not found: {src}")
        return

    root = Path(env_cfg["root"]).expanduser()
    plugins_dir = root / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)

    dest = plugins_dir / ENFORCEMENT_PLUGIN
    shutil.copy2(src, dest)
    success(f"Installed enforcement plugin -> {dest}")

    configure_opencode_formatter(root)


def configure_opencode_formatter(root: Path):
    # Disable formatter in opencode.jsonc (insert after $schema line).
    config_path = root / "opencode.jsonc"
    if not config_path.exists():
        info("opencode.jsonc not found, skipping formatter config")
        return

    content = config_path.read_text()
    if '"formatter"' in content:
        info("formatter already configured in opencode.jsonc")
        return

    # Insert after the $schema line
    import re

    updated = re.sub(
        r'("\\$schema"\s*:\s*"[^"]*",?\s*\n)',
        r'\1  "formatter": false,\n',
        content,
        count=1,
    )

    if updated == content:
        warning("Could not find $schema line in opencode.jsonc")
        return

    config_path.write_text(updated)
    success("Disabled formatter in opencode.jsonc")


def install_enforcement_script(claptrap_path: Path, workflow_dir: Path):
    src = claptrap_path / "bootstrap" / "lib" / "enforcement.py"
    dest = workflow_dir / "enforcement.py"
    shutil.copy(src, dest)
    dest.chmod(0o755)
    success("Installed enforcement.py -> .claptrap/")


def install_memory_files(claptrap_path: Path, workflow_dir: Path):
    templates_dir = claptrap_path / "bootstrap" / "templates"

    for name, filename in [
        ("memory_inbox.md", "memory_inbox_md.txt"),
        ("memories.md", "memories_md.txt"),
    ]:
        dest = workflow_dir / name
        if not dest.exists():
            shutil.copy(templates_dir / filename, dest)
            success(f"Created {name}")
        else:
            info(f"{name} already exists")


def install(env: str, target_dir: Path, claptrap_path: Path):
    workflow_dir = target_dir / ".claptrap"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    install_memory_files(claptrap_path, workflow_dir)
    install_enforcement_script(claptrap_path, workflow_dir)
    install_hooks(env, target_dir)
