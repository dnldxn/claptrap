# Provider configuration for all supported AI coding environments
from pathlib import Path

DEFAULT_PROVIDER = {
    "agents_dir": "agents",
    "commands_dir": "commands",
    "skills_dir": "skills",
    "agent_suffix": ".md",
    "command_suffix": ".md",
}

PROVIDERS = {
    "cursor": {
        "name": "Cursor",
        "dir": ".cursor",
        "global_dir": Path.home() / ".cursor",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "mcp_cmd": ["agent", "mcp", "list"],
        "hooks_config_path": "hooks.json",
        "hooks_events": {"session_end": "stop", "post_tool": "postToolUse"},
    },
    "github-copilot": {
        "name": "GitHub Copilot",
        "dir": ".github",
        "commands_dir": "prompts",
        "agent_suffix": ".agent.md",
        "command_suffix": ".prompt.md",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "hooks_config_path": "copilot-hooks.json",
        "hooks_events": {"session_end": "sessionEnd", "post_tool": "postToolUse"},
    },
    "opencode": {
        "name": "OpenCode",
        "dir": ".opencode",
        "global_dir": Path.home() / ".config" / "opencode",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "mcp_cmd": ["opencode", "mcp", "list"],
        "hooks_config_path": "opencode.jsonc",
        "hooks_events": {
            "session_end": "session.idle",
            "post_tool": "tool.execute.after",
        },
    },
    "claude": {
        "name": "Claude",
        "dir": ".claude",
        "global_dir": Path.home() / ".claude",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "mcp_cmd": ["claude", "mcp", "list"],
        "hooks_config_path": "settings.json",
        "hooks_events": {"session_end": "Stop", "post_tool": "PostToolUse"},
    },
    "codex": {
        "name": "Codex",
        "dir": ".codex",
        "global_dir": Path.home() / ".codex",
        "has_agents": False,
        "has_commands": True,
        "commands_dir": "prompts",
        "has_skills": True,
        "mcp_cmd": ["codex", "mcp", "list"],
        "hooks_config_path": None,
        "hooks_events": None,
    },
    "gemini": {
        "name": "Gemini",
        "dir": ".gemini",
        "global_dir": Path.home() / ".gemini",
        "has_agents": False,
        "has_commands": True,
        "has_skills": False,
        "commands_format": "toml",
        "mcp_cmd": ["gemini", "mcp", "list"],
        "hooks_config_path": "settings.json",
        "hooks_events": {"session_end": "SessionEnd", "post_tool": "AfterTool"},
    },
}

PROVIDER_ORDER = ["opencode", "cursor", "github-copilot", "claude", "codex", "gemini"]


def get(key):
    return {**DEFAULT_PROVIDER, **PROVIDERS[key]}


def get_display_dir(cfg):
    return str(cfg["global_dir"]) if cfg.get("global_dir") else cfg["dir"]


def get_root_dir(provider_key, target_dir):
    cfg = get(provider_key)
    return cfg["global_dir"] if cfg.get("global_dir") else target_dir / cfg["dir"]


def get_install_dir(provider_key, feature, target_dir):
    return get_root_dir(provider_key, target_dir) / get(provider_key)[f"{feature}_dir"]


def can_install_feature(cfg, feature):
    if not cfg.get(f"has_{feature}"):
        return False, "not supported"
    if feature == "commands" and cfg.get("commands_format") == "toml":
        return False, "requires TOML format (manual setup)"
    return True, None
