import json
import shutil
from datetime import datetime
from pathlib import Path

from . import installer
from .output import info, success, warning


def generate_hooks_config(env: str):
    env_cfg = installer.CONFIG["environments"].get(env, {})
    hooks_cfg = env_cfg.get("hooks")

    if not hooks_cfg or hooks_cfg is False:
        return None

    events = hooks_cfg.get("events", {})
    if not events:
        return None

    common_hooks = installer.CONFIG.get("hooks", {})

    if env == "opencode":
        return None

    if env == "claude":
        hooks_output = {}
        for canonical_name, hook_def in common_hooks.items():
            event_name = events.get(canonical_name)
            if event_name:
                hooks_output[event_name] = [
                    {
                        "matcher": hook_def.get("matcher", "*"),
                        "hooks": [{"type": "command", "command": hook_def["command"]}],
                    }
                ]
        return {"hooks": hooks_output} if hooks_output else None

    hooks_output = {}
    for canonical_name, hook_def in common_hooks.items():
        event_name = events.get(canonical_name)
        if event_name:
            hooks_output[event_name] = [
                {
                    "matcher": hook_def.get("matcher", "*"),
                    "command": hook_def["command"],
                }
            ]
    return {"hooks": hooks_output} if hooks_output else None


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

    config = generate_hooks_config(env)
    if not config:
        if env == "opencode":
            info(
                "OpenCode uses plugin system for hooks - see docs/opencode.md for setup"
            )
        return

    root = Path(env_cfg["root"]).expanduser()
    config_path = root / hooks_cfg["file"]

    if config_path.exists():
        backup_path = backup_config(config_path)
        if backup_path:
            info(f"Backed up existing config -> {backup_path.name}")

    if config_path.exists():
        try:
            content = config_path.read_text()
            lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
            existing = json.loads("\n".join(lines))
            existing.setdefault("hooks", {}).update(config.get("hooks", {}))
            config = existing
        except json.JSONDecodeError:
            warning(
                f"Could not parse existing {config_path.name} - creating new config"
            )

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    success(f"Configured memory hooks -> {config_path}")


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
