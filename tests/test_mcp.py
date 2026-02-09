def test_get_server_config_returns_serena_with_context():
    from bootstrap.lib.mcp import get_server_config

    config = get_server_config("serena", "codex")
    assert config is not None
    assert config["command"] == "uvx"
    assert "--context" in config["args"]
    assert "codex" in config["args"]


def test_get_server_config_returns_serena_default_context():
    from bootstrap.lib.mcp import get_server_config

    config = get_server_config("serena", "cursor")
    assert config is not None
    assert "--context" in config["args"]
    idx = config["args"].index("--context")
    assert config["args"][idx + 1] == "ide"


def test_get_server_config_returns_context7():
    from bootstrap.lib.mcp import get_server_config

    config = get_server_config("context7", "codex")
    assert config is not None
    assert config["command"] == "npx"
    assert "@upstash/context7-mcp" in config["args"]


def test_get_server_config_excludes_params():
    # Servers with params should still return a base config (no param args).
    from bootstrap.lib.mcp import get_server_config

    config = get_server_config("snowflake", "codex")
    assert config is not None
    assert config["command"] == "npx"
    assert "--service-config-file" not in config["args"]


def test_requires_user_config_true_for_snowflake():
    from bootstrap.lib.mcp import requires_user_config

    assert requires_user_config("snowflake") is True


def test_requires_user_config_false_for_serena():
    from bootstrap.lib.mcp import requires_user_config

    assert requires_user_config("serena") is False


def test_build_server_entry_cursor_format():
    from bootstrap.lib.mcp import build_server_entry

    server_config = {
        "command": "npx",
        "args": ["-y", "test-server"],
        "env": {"API_KEY": "abc123"},
    }
    entry = build_server_entry("context7", server_config, "mcpServers")
    assert entry["command"] == "npx"
    assert entry["args"] == ["-y", "test-server"]
    assert entry["env"]["API_KEY"] == "abc123"


def test_build_server_entry_opencode_format():
    from bootstrap.lib.mcp import build_server_entry

    server_config = {
        "command": "uvx",
        "args": ["-y", "serena"],
        "env": {"TOKEN": "xyz"},
    }
    entry = build_server_entry("serena", server_config, "opencode")
    assert entry["type"] == "local"
    assert entry["command"] == ["uvx", "-y", "serena"]
    assert entry["enabled"] is True
    assert entry["environment"]["TOKEN"] == "xyz"


def test_install_via_cli_calls_correct_command(monkeypatch):
    from bootstrap.lib import mcp

    calls = {}

    def fake_run_cmd(cmd):
        calls["cmd"] = cmd
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(mcp, "run_cmd", fake_run_cmd)
    assert mcp.install_via_cli("serena", "codex") is True
    assert calls["cmd"][:3] == ["codex", "mcp", "add"]
    assert "serena" in calls["cmd"]


def test_install_via_cli_shows_stderr_on_failure(monkeypatch, capsys):
    from bootstrap.lib import mcp

    def fake_run_cmd(cmd):
        return type("Result", (), {"returncode": 1, "stdout": "", "stderr": "bad args"})()

    monkeypatch.setattr(mcp, "run_cmd", fake_run_cmd)
    assert mcp.install_via_cli("serena", "codex") is False
    out = capsys.readouterr().out
    assert "exit 1" in out
    assert "bad args" in out


def _with_env(monkeypatch, tmp_path, env_name, config_file):
    # Helper: temporarily redirect an env's root and mcp_install to tmp_path.
    from bootstrap.lib import installer

    env_cfg = installer.CONFIG["environments"][env_name]
    saved = {k: env_cfg.get(k) for k in ("root", "mcp_install")}
    env_cfg["root"] = str(tmp_path)
    env_cfg["mcp_install"] = config_file
    return env_cfg, saved


def _restore_env(env_cfg, saved):
    for k, v in saved.items():
        env_cfg[k] = v


def test_install_via_config_merges_existing(monkeypatch, tmp_path):
    from bootstrap.lib import mcp

    env_cfg, saved = _with_env(monkeypatch, tmp_path, "cursor", "mcp.json")

    config_path = tmp_path / "mcp.json"
    config_path.write_text(
        '{"mcpServers":{"existing":{"command":"npx","args":["-y","x"]}}}'
    )

    try:
        assert mcp.install_via_config("context7", "cursor") is True
        updated = config_path.read_text()
        assert "existing" in updated
        assert "context7" in updated
    finally:
        _restore_env(env_cfg, saved)


def test_install_via_config_creates_backup(monkeypatch, tmp_path):
    from bootstrap.lib import mcp

    env_cfg, saved = _with_env(monkeypatch, tmp_path, "cursor", "mcp.json")

    config_path = tmp_path / "mcp.json"
    config_path.write_text('{"mcpServers":{}}')

    try:
        mcp.install_via_config("context7", "cursor")
        backups = list(tmp_path.glob("*.backup"))
        assert len(backups) == 1
        assert backups[0].read_text() == '{"mcpServers":{}}'
    finally:
        _restore_env(env_cfg, saved)


def test_install_via_config_preserves_jsonc_comments(monkeypatch, tmp_path):
    from bootstrap.lib import mcp

    env_cfg, saved = _with_env(monkeypatch, tmp_path, "opencode", "opencode.jsonc")

    original = """{
  // This is a user comment
  "$schema": "https://opencode.ai/config.json",
  "formatter": false,
  "mcp": {
    "existing-server": {
      "type": "local",
      "command": ["npx", "-y", "existing"],
      "enabled": true
    }
  }
}"""
    config_path = tmp_path / "opencode.jsonc"
    config_path.write_text(original)

    try:
        assert mcp.install_via_config("context7", "opencode") is True
        updated = config_path.read_text()
        assert "// This is a user comment" in updated
        assert '"$schema"' in updated
        assert '"formatter": false' in updated
        assert "existing-server" in updated
        assert "context7" in updated
    finally:
        _restore_env(env_cfg, saved)


def test_install_via_config_jsonc_skips_duplicate(monkeypatch, tmp_path):
    from bootstrap.lib import mcp

    env_cfg, saved = _with_env(monkeypatch, tmp_path, "opencode", "opencode.jsonc")

    original = """{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp"],
      "enabled": true
    }
  }
}"""
    config_path = tmp_path / "opencode.jsonc"
    config_path.write_text(original)

    try:
        assert mcp.install_via_config("context7", "opencode") is False
    finally:
        _restore_env(env_cfg, saved)


def test_check_mcp_server_config_returns_false_for_empty_json(tmp_path):
    from bootstrap.lib.mcp import check_mcp_server_config

    config_path = tmp_path / "mcp.json"
    config_path.write_text("{}")
    assert check_mcp_server_config("serena", config_path) is False


def test_check_mcp_server_config_returns_none_for_missing_file(tmp_path):
    from bootstrap.lib.mcp import check_mcp_server_config

    config_path = tmp_path / "nonexistent.json"
    assert check_mcp_server_config("serena", config_path) is None


def test_check_mcp_server_config_returns_none_for_unparseable(tmp_path):
    from bootstrap.lib.mcp import check_mcp_server_config

    config_path = tmp_path / "bad.json"
    config_path.write_text("not valid json {{{")
    assert check_mcp_server_config("serena", config_path) is None


def test_check_mcp_server_config_finds_server_in_mcp_key(tmp_path):
    from bootstrap.lib.mcp import check_mcp_server_config

    config_path = tmp_path / "opencode.jsonc"
    config_path.write_text('{"mcp": {"serena": {"type": "local"}}}')
    assert check_mcp_server_config("serena", config_path) is True
    assert check_mcp_server_config("context7", config_path) is False


def test_install_server_skips_if_already_installed(monkeypatch):
    from bootstrap.lib import mcp

    monkeypatch.setattr(mcp, "check_mcp_server_cli", lambda *_args: True)
    monkeypatch.setattr(mcp, "install_via_cli", lambda *_args: False)
    assert mcp.install_server("serena", "codex") is False


def test_install_server_skips_servers_requiring_user_config():
    from bootstrap.lib import mcp

    assert mcp.install_server("snowflake", "codex") is False


def test_mcp_servers_from_config():
    from bootstrap.lib import installer, mcp

    assert set(mcp.MCP_SERVERS) == set(installer.CONFIG.get("mcp_servers", {}).keys())
