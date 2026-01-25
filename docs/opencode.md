# OpenCode AI Development Environment

> Research date: January 2026
> Version: 1.1.34
> Sources: Official CLI output, https://opencode.ai/docs/

## Overview

OpenCode is an open-source, CLI-first AI development environment with a terminal TUI, web interface, and IDE support. It supports 75+ providers via [Models.dev](https://models.dev), MCP (Model Context Protocol) servers, custom agents/commands/skills, and a flexible plugin system.

Key features:
- **Multi-provider support**: Works with Anthropic, OpenAI, Google, GitHub Copilot, Cursor, and more
- **Multiple interfaces**: Terminal TUI (default), web UI, headless server, non-interactive CLI
- **Extensible**: Custom agents, commands, skills, tools, and MCP servers
- **Session management**: Persist, export, import, and share sessions

---

## 1. Directory Structure and Configuration

### Project-Level Structure

```
project-root/
├── .opencode/
│   ├── opencode.jsonc         # Project configuration
│   ├── AGENTS.md              # Project-wide agent instructions
│   ├── agents/                # Custom agent definitions
│   │   └── *.md
│   ├── commands/              # Custom slash commands
│   │   └── *.md
│   ├── skills/                # Reusable skill playbooks
│   │   └── */
│   │       └── SKILL.md
│   └── tools/                 # Custom tool definitions
│       └── *.md
```

### Global Paths

Run `opencode debug paths` to see your system's paths:

| Path | Default Location | Purpose |
|------|------------------|---------|
| `config` | `~/.config/opencode/` | Global configuration |
| `data` | `~/.local/share/opencode/` | Session data, logs |
| `cache` | `~/.cache/opencode/` | Cached data |
| `state` | `~/.local/state/opencode/` | Runtime state |
| `bin` | `~/.local/share/opencode/bin/` | Installed binaries |
| `log` | `~/.local/share/opencode/log/` | Log files |

### Configuration Precedence

Configuration merges from multiple sources (later overrides earlier):
1. Remote defaults (from Models.dev)
2. Global config (`~/.config/opencode/opencode.jsonc`)
3. Project config (`./.opencode/opencode.jsonc`)
4. Environment variables
5. CLI arguments

---

## 2. Available Providers and Models

> **Note:** Run `opencode models` from the terminal to get the current full list of available models.

### Model Specification Syntax

```
<provider>/<model-name>
```

In frontmatter:
```yaml
model: anthropic/claude-sonnet-4-5
```

In configuration:
```json
{
  "model": "anthropic/claude-sonnet-4-5"
}
```

### Providers and Models

**OpenCode Native:**
| Model | Description |
|-------|-------------|
| `opencode/big-pickle` | OpenCode native model |
| `opencode/gpt-5-nano` | Lightweight model |

**Anthropic:**
| Model | Notes |
|-------|-------|
| `anthropic/claude-opus-4-5` | Latest Opus |
| `anthropic/claude-opus-4-5-20251101` | Dated version |
| `anthropic/claude-opus-4-1` | |
| `anthropic/claude-opus-4-1-20250805` | |
| `anthropic/claude-opus-4-0` | |
| `anthropic/claude-opus-4-20250514` | |
| `anthropic/claude-sonnet-4-5` | Latest Sonnet |
| `anthropic/claude-sonnet-4-5-20250929` | |
| `anthropic/claude-sonnet-4-0` | |
| `anthropic/claude-sonnet-4-20250514` | |
| `anthropic/claude-haiku-4-5` | Latest Haiku |
| `anthropic/claude-haiku-4-5-20251001` | |
| `anthropic/claude-3-7-sonnet-latest` | Claude 3.7 |
| `anthropic/claude-3-7-sonnet-20250219` | |
| `anthropic/claude-3-5-sonnet-20241022` | Claude 3.5 |
| `anthropic/claude-3-5-sonnet-20240620` | |
| `anthropic/claude-3-5-haiku-latest` | |
| `anthropic/claude-3-5-haiku-20241022` | |
| `anthropic/claude-3-opus-20240229` | Claude 3 |
| `anthropic/claude-3-sonnet-20240229` | |
| `anthropic/claude-3-haiku-20240307` | |

**OpenAI:**
| Model | Notes |
|-------|-------|
| `openai/gpt-5.2` | Latest GPT-5 |
| `openai/gpt-5.2-codex` | Codex variant |
| `openai/gpt-5.1-codex-max` | High-capacity Codex |
| `openai/gpt-5.1-codex-mini` | Lightweight Codex |

**Cursor (via plugin):**
| Model | Notes |
|-------|-------|
| `cursor/auto` | Auto-select |
| `cursor/gpt-5` | GPT-5 via Cursor |
| `cursor/gpt-5.1` | |
| `cursor/gpt-5.1-codex` | |
| `cursor/gpt-5.2` | |
| `cursor/sonnet-4.5` | |
| `cursor/sonnet-4.5-thinking` | Extended thinking |

**GitHub Copilot:**
| Model | Notes |
|-------|-------|
| `github-copilot/claude-opus-4.5` | |
| `github-copilot/claude-opus-41` | |
| `github-copilot/claude-sonnet-4` | |
| `github-copilot/claude-sonnet-4.5` | |
| `github-copilot/claude-haiku-4.5` | |
| `github-copilot/gemini-2.5-pro` | |
| `github-copilot/gemini-3-flash-preview` | |
| `github-copilot/gemini-3-pro-preview` | |
| `github-copilot/gpt-4.1` | |
| `github-copilot/gpt-4o` | |
| `github-copilot/gpt-5` | |
| `github-copilot/gpt-5-mini` | |
| `github-copilot/gpt-5.1` | |
| `github-copilot/gpt-5.1-codex` | |
| `github-copilot/gpt-5.1-codex-max` | |
| `github-copilot/gpt-5.1-codex-mini` | |
| `github-copilot/gpt-5.2` | |
| `github-copilot/gpt-5.2-codex` | |
| `github-copilot/grok-code-fast-1` | |

---

## 3. Agent Files

Agents are defined as Markdown files with YAML frontmatter.

### Location

- Project: `.opencode/agents/*.md`
- Global: `~/.config/opencode/agents/*.md`

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to filename) |
| `description` | Yes | Brief description of the agent's purpose |
| `model` | No | Default model (format: `provider/model`) |
| `mode` | No | Agent mode: `primary`, `subagent`, or `all` |
| `tools` | No | Tool restrictions (object with tool:boolean) |

### Example Agent File

```markdown
---
description: "Review code for quality, security, and best practices"
model: anthropic/claude-sonnet-4-5
mode: subagent
tools:
  bash: false
  edit: false
---

You are a code reviewer. Focus on:
- Correctness and logic errors
- Security vulnerabilities
- Performance issues
- Code style and maintainability

Do not make changes directly. Provide actionable feedback.
```

### Agent Modes

| Mode | Description |
|------|-------------|
| `primary` | Main agent, full tool access |
| `subagent` | Spawned by other agents, restricted scope |
| `all` | Available in both contexts |

### Built-in Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `build` | primary | Main development agent |
| `plan` | primary | Planning mode with restricted editing |
| `explore` | subagent | Codebase exploration (read-only) |
| `general` | subagent | General-purpose subagent |
| `compaction` | primary | Session compaction |
| `summary` | primary | Generate summaries |
| `title` | primary | Generate session titles |

---

## 4. Slash Commands

Commands are invoked with `/command` in the TUI or via `--command` in CLI.

### Location

- Project: `.opencode/commands/*.md`
- Global: `~/.config/opencode/commands/*.md`

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | Yes | Brief description |
| `model` | No | Model to use for this command |
| `agent` | No | Agent to invoke |
| `template` | No | Prompt template (inline) |

### Example Command File

```markdown
---
description: "Run tests with coverage and show failures"
model: anthropic/claude-sonnet-4-5
---

Run the full test suite with coverage reporting. Show any failing tests
with their error messages and suggest fixes.
```

### JSON Configuration Alternative

Commands can also be defined in `opencode.jsonc`:

```json
{
  "command": {
    "test": {
      "description": "Run tests with coverage",
      "model": "anthropic/claude-sonnet-4-5",
      "template": "Run the test suite with coverage..."
    }
  }
}
```

---

## 5. Skills

Skills are reusable instruction sets that agents can load.

### Location

- Project: `.opencode/skills/<skill-name>/SKILL.md`
- Global: `~/.config/opencode/skills/<skill-name>/SKILL.md`

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier |
| `description` | Yes | What the skill does |
| `license` | No | License information |
| `compatibility` | No | Compatible environments |
| `metadata` | No | Additional metadata |

### Example SKILL.md

```markdown
---
name: memory
description: Read and write project memory for decisions, patterns, and lessons.
---

## What this skill does

Provides a lightweight memory system for recording and retrieving project decisions, patterns, and lessons learned.

## When to activate

- After making non-obvious decisions
- When patterns emerge that should be repeated
- When anti-patterns cause problems

## How to use

1. Read `.memories.md` for context
2. Add new entries at the top with proper format
3. Update existing entries when information changes
```

### Discovering Skills

```bash
opencode debug skill
```

---

## 6. Built-in Tools

OpenCode provides core tools that agents can use.

### Core Tools

| Tool | Permission | Description |
|------|------------|-------------|
| `read` | `read` | Read file contents |
| `edit` | `edit` | Edit file contents |
| `write` | `write` | Write/create files |
| `bash` | `bash` | Execute shell commands |
| `grep` | `grep` | Search file contents (ripgrep) |
| `glob` | `glob` | Find files by pattern |
| `list` | `list` | List directory contents |
| `webfetch` | `webfetch` | Fetch web content |
| `websearch` | `websearch` | Search the web |
| `codesearch` | `codesearch` | Search code repositories |
| `todoread` | `todoread` | Read todo list |
| `todowrite` | `todowrite` | Write todo list |
| `question` | `question` | Ask user questions |

### Permission System

Tools can be controlled via the `permission` field in config:

```json
{
  "permission": [
    { "permission": "read", "pattern": "*", "action": "allow" },
    { "permission": "read", "pattern": "*.env", "action": "ask" },
    { "permission": "edit", "pattern": "*", "action": "allow" },
    { "permission": "bash", "pattern": "*", "action": "ask" }
  ]
}
```

Actions:
- `allow`: Permit without asking
- `ask`: Prompt user for permission
- `deny`: Block the action

### Custom Tools

Custom tools can be added in:
- `.opencode/tools/*.md`
- `~/.config/opencode/tools/*.md`

---

## 7. MCP Servers

MCP (Model Context Protocol) servers extend OpenCode with additional tools and context.  See `bootstrap/mcp_setup.md` for instructions on how to install and configure various MCP Servers in each environment.

### Managing MCP Servers

```bash
opencode mcp list # List all configured MCP servers
opencode mcp add # Add a new MCP server
opencode mcp auth <name> # Authenticate with an OAuth-enabled server
opencode mcp logout <name> # Remove OAuth credentials
opencode mcp debug <name> # Debug an OAuth connection
```

---

## 8. CLI Reference

### Main Commands

| Command | Description |
|---------|-------------|
| `opencode` | Start TUI (default) |
| `opencode [project]` | Start TUI in specified project directory |
| `opencode run [message..]` | Run with a message (non-interactive) |
| `opencode serve` | Start headless server |
| `opencode web` | Start server with web interface |
| `opencode attach <url>` | Attach to running server |

### Session Management

| Command | Description |
|---------|-------------|
| `opencode session list` | List all sessions |
| `opencode export [sessionID]` | Export session as JSON |
| `opencode import <file>` | Import session from JSON or URL |

### Agent Management

| Command | Description |
|---------|-------------|
| `opencode agent list` | List available agents |
| `opencode agent create` | Create a new agent |

### Model Management

| Command | Description |
|---------|-------------|
| `opencode models [provider]` | List available models |

### Authentication

| Command | Description |
|---------|-------------|
| `opencode auth login [url]` | Log in to a provider |
| `opencode auth logout` | Log out from provider |
| `opencode auth list` | List configured providers |

### GitHub Integration

| Command | Description |
|---------|-------------|
| `opencode pr <number>` | Checkout PR branch and start OpenCode |
| `opencode github install` | Install GitHub agent |
| `opencode github run` | Run GitHub agent |

### Debugging

| Command | Description |
|---------|-------------|
| `opencode debug config` | Show resolved configuration |
| `opencode debug paths` | Show global paths |
| `opencode debug skill` | List available skills |
| `opencode debug agent <name>` | Show agent configuration |
| `opencode debug lsp` | LSP debugging utilities |
| `opencode debug rg` | ripgrep debugging utilities |
| `opencode debug file` | File system debugging |

### Other Commands

| Command | Description |
|---------|-------------|
| `opencode stats` | Show token usage and cost statistics |
| `opencode upgrade [target]` | Upgrade to latest or specific version |
| `opencode uninstall` | Uninstall OpenCode |
| `opencode completion` | Generate shell completion script |
| `opencode acp` | Start ACP (Agent Client Protocol) server |

### Global Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help |
| `-v, --version` | Show version |
| `-m, --model <provider/model>` | Specify model |
| `-c, --continue` | Continue last session |
| `-s, --session <id>` | Continue specific session |
| `--agent <name>` | Use specific agent |
| `--prompt <text>` | System prompt |
| `--print-logs` | Print logs to stderr |
| `--log-level <level>` | Log level (DEBUG, INFO, WARN, ERROR) |

### `opencode run` Options

| Option | Description |
|--------|-------------|
| `--command <name>` | Run a slash command |
| `--format <type>` | Output format: `default` or `json` |
| `-f, --file <path>` | Attach file(s) to message |
| `--title <text>` | Session title |
| `--share` | Share the session |
| `--attach <url>` | Attach to running server |
| `--port <number>` | Local server port |
| `--variant <level>` | Model variant/reasoning effort |

### `opencode stats` Options

| Option | Description |
|--------|-------------|
| `--days <n>` | Stats for last N days |
| `--tools <n>` | Number of tools to show |
| `--models` | Show model statistics |
| `--project <name>` | Filter by project |

### `opencode serve` / `opencode web` Options

| Option | Description |
|--------|-------------|
| `--port <number>` | Port to listen on (default: random) |
| `--hostname <host>` | Hostname (default: 127.0.0.1) |
| `--mdns` | Enable mDNS discovery |
| `--cors <domains>` | Additional CORS domains |

### `opencode upgrade` Options

| Option | Description |
|--------|-------------|
| `-m, --method <method>` | Installation method: curl, npm, pnpm, bun, brew, choco, scoop |

---

## 9. Configuration Reference

### Full opencode.jsonc Example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  
  "keybinds": {
    "leader": "ctrl+x"
  },

  "plugin": [
    "opencode-cursor-auth@1.0.16"
  ],

  "provider": {
    "custom-provider": {
      "name": "Custom Provider",
      "npm": "@ai-sdk/openai-compatible",
      "models": {
        "model-name": {
          "name": "Display Name",
          "limit": { "context": 128000, "output": 32000 },
          "modalities": { "input": ["text", "image"], "output": ["text"] }
        }
      },
      "options": {
        "baseURL": "https://api.example.com/v1"
      }
    }
  },

  "mcp": {
    "serena": {
      "type": "local",
      "command": [
        "uvx",
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server",
        "--context", "codex",
        "--project-from-cwd",
        "--open-web-dashboard", "false"
      ],
      "enabled": true,
      "timeout": 10000
    }
  },

  "permission": [
    { "permission": "read", "pattern": "*", "action": "allow" },
    { "permission": "edit", "pattern": "*", "action": "allow" },
    { "permission": "bash", "pattern": "*", "action": "ask" }
  ],

  "agent": {
    "Custom Agent": {
      "model": "anthropic/claude-opus-4-5",
      "description": "Custom agent description",
      "prompt": "You are a custom agent...",
      "permission": {}
    }
  },

  "command": {
    "custom-command": {
      "description": "Custom command description",
      "model": "anthropic/claude-sonnet-4-5",
      "template": "Command prompt template..."
    }
  }
}
```

### Provider Options

```json
{
  "provider": {
    "openai": {
      "options": {
        "reasoningEffort": "medium",
        "reasoningSummary": "auto",
        "textVerbosity": "medium",
        "store": false
      }
    }
  }
}
```

| Option | Values | Description |
|--------|--------|-------------|
| `reasoningEffort` | `low`, `medium`, `high`, `xhigh` | Reasoning depth |
| `reasoningSummary` | `auto`, `concise`, `detailed`, `off` | Summary style |
| `textVerbosity` | `low`, `medium`, `high` | Output verbosity |

---

## 10. Keyboard Shortcuts (TUI)

Default keybinds (customizable via `keybinds` config):

| Action | Default | Description |
|--------|---------|-------------|
| `leader` | `ctrl+x` | Leader key prefix |
| `app_exit` | `ctrl+c`, `ctrl+d`, `<leader>q` | Exit application |
| `model_list` | `<leader>m` | Open model selector |
| `agent_list` | `<leader>a` | Open agent selector |
| `command_list` | `ctrl+p` | Open command palette |
| `session_new` | `<leader>n` | New session |
| `session_list` | `<leader>l` | List sessions |
| `session_compact` | `<leader>c` | Compact session |
| `input_submit` | `return` | Submit message |
| `input_newline` | `shift+return`, `ctrl+j` | Insert newline |
| `input_clear` | `ctrl+c` | Clear input |
| `agent_cycle` | `tab` | Cycle agents |
| `model_cycle_recent` | `f2` | Cycle recent models |
| `variant_cycle` | `ctrl+t` | Cycle model variants |

---

## 11. Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENCODE_MODEL` | Default model |
| `OPENCODE_LOG_LEVEL` | Log level |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GOOGLE_API_KEY` | Google API key |

---

## 12. Comparison with Other Tools

### vs. Claude Code
- OpenCode is multi-provider; Claude Code is Anthropic-only
- Both support AGENTS.md conventions
- OpenCode has plugin ecosystem for provider flexibility

### vs. Cursor
- OpenCode is terminal-based; Cursor is IDE-based
- OpenCode uses API keys or OAuth plugins; Cursor uses subscription
- OpenCode has MCP server support

### vs. Codex CLI
- OpenCode supports multiple providers; Codex is OpenAI-only
- OpenCode has plugin/MCP ecosystem
- Both support non-interactive CLI modes

---

## References

- [OpenCode Documentation](https://opencode.ai/docs/)
- [CLI Reference](https://opencode.ai/docs/cli/)
- [Agents](https://opencode.ai/docs/agents/)
- [Skills](https://opencode.ai/docs/skills/)
- [Commands](https://opencode.ai/docs/commands/)
- [Tools](https://opencode.ai/docs/tools/)
- [MCP Servers](https://opencode.ai/docs/mcp-servers/)
- [Configuration](https://opencode.ai/docs/config/)
- [GitHub Repository](https://github.com/opencode-ai/opencode)
