# Bootstrap Directory

Installs claptrap agents, commands, skills, and memory system to target projects across multiple AI environments.

## Entry Point

- **`install.py`** - Main installer script. Run from target project: `python bootstrap/install.py [--env ENV] [--verify]`
- **`install.py mcp`** - MCP installer. Run from target project: `python bootstrap/install.py mcp [--env ENV]`

## Configuration

- **`claptrap.yaml`** - Single source of truth for all environments, model aliases, hooks, and feature defaults

## Library (`lib/`)

| File | Purpose |
|------|---------|
| `installer.py` | Core installation logic: staging, symlinks, model transforms, debate agent generation |
| `memory.py` | Memory system: hooks config, enforcement script, OpenCode plugin, formatter config |
| `verify.py` | Verification: checks staged files, symlinks, hooks, gitignore, MCP servers, global skills |
| `common.py` | Shared utilities: `run_cmd()`, `parse_json_with_comments()`, environment detection |
| `mcp.py` | MCP server installation and verification: server definitions, CLI/config install, status checks |
| `output.py` | Terminal output: `success()`, `warning()`, `info()`, `header()`, `step()` with ANSI colors |
| `enforcement.py` | Standalone script copied to target projects for memory capture enforcement |

## Templates (`templates/`)

| File | Creates |
|------|---------|
| `memory_inbox_md.txt` | `.claptrap/memory_inbox.md` |
| `memories_md.txt` | `.claptrap/memories.md` |
| `agents_md.txt` | (unused) |

## Documentation

| File | Purpose |
|------|---------|
| `README.md` | User-facing install instructions |
| `mcp_setup.md` | MCP server configuration guide |
| `environments/opencode.md` | OpenCode-specific setup notes |

## Key Functions

**Finding installation targets:**
```python
# lib/common.py
detect_environments()  # Finds installed CLI tools
select_environment()   # Interactive env selection
```

**Installing features:**
```python
# lib/installer.py
install_feature(src_dir, staging_dir, feature_dir, suffix, env, is_skill)
generate_debate_agents(claptrap_path, agents_dir, env)
transform_model(content, env)  # Replaces model aliases per environment
```

**Memory system:**
```python
# lib/memory.py
install(env, target_dir, claptrap_path)  # Main entry for memory setup
install_hooks(env, target_dir)           # JSON hooks or OpenCode plugin
configure_opencode_formatter(root)       # Disables formatter in opencode.jsonc
```

**Verification:**
```python
# lib/verify.py
verify_all(envs, claptrap_path, target_dir)  # Full verification suite
```

**MCP servers:**
```python
# lib/mcp.py
install_all(envs)                    # Install MCP servers to environments
install_server(server_name, env)     # Install single server
get_server_config(server_name, env)  # Resolve server command/args
```

## Data Flow

```
claptrap.yaml
    ↓
install.py (orchestrator)
    ├── installer.py → staging/ + symlinks to env dirs
    ├── memory.py → .claptrap/ files + hooks config
    ├── mcp.py → MCP server install + status checks
    └── common.py → environment detection, utilities
```

## Environment Config Structure (claptrap.yaml)

```yaml
environments:
  <env>:
    root: ~/.config/<env>     # Where env config lives
    cli: <command>            # CLI tool name for detection
    agents: {dir, suffix}     # Or `false` if unsupported
    commands: {dir, suffix}
    skills: {dir}
    hooks: {file, events}     # Or `false` if unsupported
```
