import json
import re
from pathlib import Path

from . import installer
from .common import parse_json_with_comments, run_cmd
from .memory import backup_config
from .output import info, success, warning

MCP_SERVERS = list(installer.CONFIG.get("mcp_servers", {}).keys())
CLI_CHECK_ORDER = ["opencode", "claude", "agent", "codex", "gemini"]


def _server_def(server_name: str) -> dict | None:
    return installer.CONFIG.get("mcp_servers", {}).get(server_name)


def requires_user_config(server_name: str) -> bool:
    # Servers with params or env that need prompting cannot be installed headlessly.
    server = _server_def(server_name)
    if not server: return False
    return bool(server.get("params") or server.get("env"))


def get_server_config(server_name: str, env: str) -> dict | None:
    server = _server_def(server_name)
    if not server: return None

    command = server.get("command")
    if not command: return None

    args = list(server.get("args", []))
    context_map = server.get("context", {})
    if context_map:
        context_value = context_map.get(env, context_map.get("default"))
        if context_value: args += ["--context", context_value]

    return {"command": command, "args": args, "env": {}}


def build_server_entry(server_name: str, server_config: dict, config_format: str) -> dict:
    command = server_config["command"]
    args = server_config.get("args", [])
    env_vars = server_config.get("env", {})

    if config_format == "opencode":
        entry = {"type": "local", "command": [command, *args], "enabled": True}
        if env_vars: entry["environment"] = env_vars
        return entry

    entry = {"command": command, "args": args}
    if env_vars: entry["env"] = env_vars
    return entry


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
    # Returns True if configured, False if not configured, None if file not found or unparseable.
    if not config_path.exists(): return None

    content = parse_json_with_comments(config_path.read_text())
    if content is None: return None

    if "mcpServers" in content:
        servers = content["mcpServers"]
    elif "mcp" in content:
        servers = content["mcp"]
    else:
        return False

    return server_name.lower() in [s.lower() for s in servers.keys()]


def check_mcp_server(server_name: str, cli: str | None = None) -> bool | None:
    # Legacy function for backward compatibility - checks any available CLI.
    for cmd_cli in CLI_CHECK_ORDER:
        result = check_mcp_server_cli(server_name, cmd_cli)
        if result is not None:
            return result
    return None


def _config_format(config_path: Path, content: dict | None) -> str:
    if content and "mcp" in content: return "opencode"
    if config_path.name == "opencode.jsonc": return "opencode"
    return "mcpServers"


def _build_cli_command(cli: str, server_name: str, server_config: dict) -> list[str]:
    env_vars = server_config.get("env", {})
    cmd = [cli, "mcp", "add"]

    if cli == "claude":
        cmd += ["--scope", "user"]
        for key, value in sorted(env_vars.items()):
            cmd += ["--env", f"{key}={value}"]
        cmd += [server_name]
    else:
        cmd += [server_name]
        for key, value in sorted(env_vars.items()):
            cmd += ["--env", f"{key}={value}"]

    cmd += ["--", server_config["command"], *server_config.get("args", [])]
    return cmd


def install_via_cli(server_name: str, env: str) -> bool:
    env_cfg = installer.CONFIG["environments"].get(env, {})
    cli = env_cfg.get("cli")
    if not cli:
        warning(f"{env}: MCP CLI not configured")
        return False

    server_config = get_server_config(server_name, env)
    if not server_config:
        warning(f"{server_name}: MCP server definition missing")
        return False

    cmd = _build_cli_command(cli, server_name, server_config)
    info(f"  Running: {' '.join(cmd)}")
    result = run_cmd(cmd)
    if result.returncode == 0:
        success(f"  {server_name} MCP installed via {cli}")
        return True

    warning(f"  {server_name} MCP install failed (exit {result.returncode})")
    if result.stderr.strip():
        for line in result.stderr.strip().splitlines()[:5]:
            warning(f"    {line}")
    elif result.stdout.strip():
        for line in result.stdout.strip().splitlines()[:5]:
            warning(f"    {line}")
    return False


def _insert_into_jsonc(text: str, key: str, server_name: str, entry_json: str) -> str | None:
    # Insert a server entry into a JSONC file by text manipulation, preserving comments/formatting.
    # Returns the updated text, or None if the key block can't be found.
    pattern = rf'("{key}"\s*:\s*\{{)'
    match = re.search(pattern, text)
    if not match:
        return None

    insert_pos = match.end()
    entry_text = f'\n    "{server_name}": {entry_json},'
    return text[:insert_pos] + entry_text + text[insert_pos:]


def install_via_config(server_name: str, env: str) -> bool:
    env_cfg = installer.CONFIG["environments"].get(env, {})
    config_file = env_cfg.get("mcp_install")
    root = Path(env_cfg.get("root", "")).expanduser()
    if not config_file or not root:
        warning(f"  {server_name}: MCP config path not configured for {env}")
        return False

    config_path = root / config_file
    server_config = get_server_config(server_name, env)
    if not server_config:
        warning(f"  {server_name}: MCP server definition missing")
        return False

    is_jsonc = config_path.suffix == ".jsonc"

    if config_path.exists():
        raw_text = config_path.read_text()
        content = parse_json_with_comments(raw_text)
    else:
        raw_text = None
        content = None

    # Check if server already present (works for both JSON and JSONC).
    if content is not None:
        format_type = _config_format(config_path, content)
        key = "mcp" if format_type == "opencode" else "mcpServers"
        servers = content.get(key, {})
        if server_name in servers:
            info(f"  {server_name} MCP already in {config_path.name}")
            return False

    # Backup before any write.
    backup_path = backup_config(config_path)
    if backup_path:
        info(f"  Backed up {config_path.name} -> {backup_path.name}")

    format_type = _config_format(config_path, content)
    entry = build_server_entry(server_name, server_config, format_type)
    key = "mcp" if format_type == "opencode" else "mcpServers"
    entry_json = json.dumps(entry, indent=6)

    # JSONC files: targeted text insertion to preserve comments and formatting.
    if is_jsonc and raw_text:
        updated = _insert_into_jsonc(raw_text, key, server_name, entry_json)
        if updated:
            config_path.write_text(updated)
            success(f"  {server_name} MCP added to {config_path}")
            return True
        warning(f"  {server_name}: could not find \"{key}\" block in {config_path.name}")
        return False

    # Plain JSON: standard parse-modify-serialize.
    if content is None:
        if raw_text is not None:
            warning(f"  {server_name}: could not parse {config_path.name}, writing fresh config")
        content = {}

    content.setdefault(key, {})
    content[key][server_name] = entry
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(content, indent=2))
    success(f"  {server_name} MCP added to {config_path}")
    return True


def install_server(server_name: str, env: str) -> bool:
    env_cfg = installer.CONFIG["environments"].get(env, {})
    mcp_install = env_cfg.get("mcp_install")

    if not mcp_install:
        info(f"  {server_name}: MCP not supported for {env}")
        return False

    if requires_user_config(server_name):
        server = _server_def(server_name)
        params = [p["prompt"] for p in server.get("params", []) if p.get("prompt")]
        info(f"  {server_name}: requires manual config ({', '.join(params)}); skipping")
        return False

    if mcp_install == "cli":
        status = check_mcp_server_cli(server_name, env_cfg.get("cli", ""))
        if status is True:
            info(f"  {server_name} MCP already configured")
            return False
        if status is None:
            warning(f"  {server_name}: {env} CLI not found, cannot check status")
            return False
        return install_via_cli(server_name, env)

    config_path = Path(env_cfg.get("root", "")).expanduser() / mcp_install
    status = check_mcp_server_config(server_name, config_path)
    if status is True:
        info(f"  {server_name} MCP already configured")
        return False
    return install_via_config(server_name, env)


def install_all(envs: list[str]) -> None:
    for env in envs:
        info(f"{env}:")
        for server in MCP_SERVERS:
            install_server(server, env)


def check_all(envs: list[str]) -> None:
    for env in envs:
        env_cfg = installer.CONFIG["environments"].get(env, {})
        mcp_type = env_cfg.get("mcp")
        cli = env_cfg.get("cli")
        root = Path(env_cfg.get("root", "")).expanduser()

        if not mcp_type:
            info(f"{env}: MCP not supported")
            continue

        info(f"{env}:")
        for server in MCP_SERVERS:
            if mcp_type == "cli":
                status = check_mcp_server_cli(server, cli)
            else:
                config_path = root / mcp_type
                status = check_mcp_server_config(server, config_path)

            if status is True:
                success(f"  {server} MCP is configured")
            elif status is False:
                warning(f"  {server} MCP not configured")
            else:
                info(f"  Could not check {server} MCP status")
