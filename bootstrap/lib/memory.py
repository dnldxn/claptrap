# Memory system installation - hooks configuration and enforcement
import json
import shutil
from datetime import datetime
from pathlib import Path

from . import providers
from .output import success, warning, info


def generate_hooks_config(provider_key):
    """Generate hooks configuration for a provider."""
    cfg = providers.get(provider_key)
    events = cfg.get("hooks_events")
    if not events: return None

    enforcement_cmd = "python3 .claptrap/enforcement.py"

    # OpenCode uses plugin system, not hooks config - skip hook generation
    if provider_key == "opencode":
        return None

    # Claude uses nested structure with matcher and hooks array
    if provider_key == "claude":
        return {
            "hooks": {
                events["session_end"]: [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"{enforcement_cmd} --event session-end",
                            }
                        ],
                    }
                ],
                events["post_tool"]: [
                    {
                        "matcher": "Write|Edit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": f"{enforcement_cmd} --event post-tool",
                            }
                        ],
                    }
                ],
            }
        }

    # Cursor and others use simpler structure
    return {
        "hooks": {
            events["session_end"]: [
                {"matcher": "*", "command": f"{enforcement_cmd} --event session-end"}
            ],
            events["post_tool"]: [
                {
                    "matcher": "Edit|Write" if provider_key == "cursor" else "*",
                    "command": f"{enforcement_cmd} --event post-tool",
                }
            ],
        }
    }


def backup_config(config_path):
    """Create a timestamped backup of the config file."""
    if not config_path.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = config_path.with_suffix(f".{timestamp}.backup")
    shutil.copy2(config_path, backup_path)
    return backup_path


def install_hooks(provider_key, target_dir):
    """Install hooks configuration for memory enforcement."""
    cfg = providers.get(provider_key)

    if not cfg.get("hooks_config_path"):
        warning(f"{cfg['name']} doesn't support hooks (soft enforcement only)")
        return

    config = generate_hooks_config(provider_key)
    if not config:
        if provider_key == "opencode":
            info("OpenCode uses plugin system for hooks - see docs/opencode.md for setup")
        return

    config_path = (providers.get_root_dir(provider_key, target_dir) / cfg["hooks_config_path"])

    # Backup existing config before any modifications
    if config_path.exists():
        backup_path = backup_config(config_path)
        if backup_path:
            info(f"Backed up existing config → {backup_path.name}")

    # Merge with existing config if present
    if config_path.exists():
        try:
            content = config_path.read_text()
            lines = [l for l in content.split("\n") if not l.strip().startswith("//")]  # Strip JSONC comments
            existing = json.loads("\n".join(lines))
            existing.setdefault("hooks", {}).update(config.get("hooks", {}))
            config = existing
        except json.JSONDecodeError:
            warning(f"Could not parse existing {config_path.name} - creating new config")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    success(f"Configured memory hooks → {config_path}")


def install_enforcement_script(claptrap_path, workflow_dir):
    """Copy enforcement script to .claptrap/"""
    src = claptrap_path / "bootstrap" / "lib" / "enforcement.py"
    dest = workflow_dir / "enforcement.py"
    shutil.copy(src, dest)
    dest.chmod(0o755)
    success("Installed enforcement.py → .claptrap/")


def install_memory_files(claptrap_path, workflow_dir):
    """Initialize memory inbox and memories files."""
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


def install(provider_key, target_dir, claptrap_path):
    """Install complete memory system for a provider."""
    workflow_dir = target_dir / ".claptrap"
    workflow_dir.mkdir(parents=True, exist_ok=True)

    install_memory_files(claptrap_path, workflow_dir)
    install_enforcement_script(claptrap_path, workflow_dir)
    install_hooks(provider_key, target_dir)
