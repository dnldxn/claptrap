# OpenCode AI Development Environment

> Research date: January 2026
> Sources: Local project files, oh-my-opencode-slim documentation, opencode-openai-codex-auth plugin

## Overview

OpenCode is a CLI-based AI development environment that supports multi-provider model access, plugin-based extensions, MCP (Model Context Protocol) servers, and customizable agents/commands/skills. It is designed for terminal-based AI-assisted development workflows.

---

## 1. Custom Subagents, Slash Commands, and Skills

### Support
OpenCode supports custom agents, slash commands, and skills via configuration files and markdown-based definitions.

### Directory Structure

```
project-root/
├── .opencode/
│   ├── opencode.jsonc         # Main project configuration
│   ├── AGENTS.md              # Project-wide agent instructions
│   ├── agents/                # Custom agent definitions
│   │   └── *.md
│   ├── commands/              # Custom slash commands
│   │   └── *.md
│   └── skills/                # Reusable skill playbooks
│       └── */
│           └── SKILL.md
```

**Global Configuration Locations:**
- User global config: `~/.config/opencode/opencode.json`
- Plugin config: `~/.opencode/openai-codex-auth-config.json`
- Project local config: `./.opencode/opencode.jsonc`

### Agent/Command Locations
Plugins and extensions (like oh-my-opencode) can add agents/commands via:
- `~/.config/opencode/oh-my-opencode-slim.json` (user global)
- `./.opencode/oh-my-opencode-slim.json` (project local)

---

## 2. Frontmatter Syntax for .md Files

### Agent Files

```yaml
---
name: Code Reviewer
description: "Review an OpenSpec change proposal for correctness, safety, and spec alignment."
model: claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.1-codex
---
```

### Slash Command Files

```yaml
---
name: brainstorm
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior."
model: claude-opus-4.5
models:
  cursor: anthropic/claude-opus-4.5
  github-copilot: claude-opus-4.5
  claude: opus
  opencode: anthropic/claude-opus-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---
```

### Skill Files (SKILL.md)

```yaml
---
name: memory
description: Read and write project memory files for decisions, patterns, and lessons.
---
```

### Frontmatter Fields Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the agent/command/skill |
| `description` | Yes | Brief description of purpose |
| `model` | No | Default model identifier |
| `models` | No | Provider-specific model mappings |

---

## 3. Available Models

### Model Specification Syntax

In frontmatter:
```yaml
model: anthropic/claude-sonnet-4-5
```

In configuration (opencode.jsonc):
```json
{
  "model": "anthropic/claude-sonnet-4-5"
}
```

### Model Format
```
<provider>/<model-name>
```

### Available Providers and Models

**Anthropic:**
- `anthropic/claude-opus-4-5` (alias: `claude-opus-4-5-20251101`)
- `anthropic/claude-sonnet-4-5`

**OpenAI (via plugin):**
- `openai/gpt-5.2-low`, `openai/gpt-5.2-medium`, `openai/gpt-5.2-high`, `openai/gpt-5.2-xhigh`
- `openai/gpt-5.1-codex-low`, `openai/gpt-5.1-codex-medium`, `openai/gpt-5.1-codex-high`
- `openai/gpt-5.1-codex-max-low`, `openai/gpt-5.1-codex-max-medium`, `openai/gpt-5.1-codex-max-high`, `openai/gpt-5.1-codex-max-xhigh`
- `openai/gpt-5.1-codex-mini-medium`, `openai/gpt-5.1-codex-mini-high`
- `openai/gpt-5.1-low`, `openai/gpt-5.1-medium`, `openai/gpt-5.1-high`

**Google:**
- `google/gemini-3-flash`
- `google/gemini-3-flash-preview`
- `google/claude-opus-4-5-thinking` (via Antigravity routing)

**Cerebras:**
- `cerebras/zai-glm-4.6` (via Antigravity routing)

### Per-Agent Model Configuration

In `opencode.jsonc`:
```json
{
  "agent": {
    "commit": {
      "model": "openai/gpt-5.1-codex-low",
      "prompt": "Generate concise commit messages"
    },
    "review": {
      "model": "openai/gpt-5.1-codex-high",
      "prompt": "Thorough code review"
    }
  }
}
```

---

## 4. Triggering Subagents from Agent Files

### Spawn Subagent Pattern

In an agent `.md` file, reference skills that handle spawning:

```markdown
# Skills

Load the following skills:
- `memory`
- `spawn-subagent`

# Subagent Spawning

- Subagents spawn in a fresh context; include all necessary background and constraints.
- Spawn Research when external documentation would improve accuracy.
- Spawn Explore when codebase context is required.

**Research subagent prompt template:**
- **Query**: [Specific question to answer]
- **Context**: [Project details, current idea, why research is needed]
- **Constraints**: [Scope, do not modify code, cite sources if available]
```

### Subagent Interface Definition

```markdown
# Subagent Interface

- Input: code changes plus proposal context (`proposal.md`, `tasks.md`, and spec deltas).
- Context: assume fresh context; do not rely on prior conversation state.
- Expected paths:
  - `openspec/changes/<change-id>/proposal.md`
  - `openspec/changes/<change-id>/tasks.md`
```

---

## 5. Triggering Agents from Slash Commands

### In Command Files

Reference agents by name and describe when they're spawned:

```markdown
## Agent Spawning Map

- **`alignment-reviewer.md`** -- Spawned by: `/propose`
- **`feasibility-reviewer.md`** -- Spawned by: `/propose`
- **`developer.md`** -- Spawned by: `/implement-change`
- **`code-reviewer.md`** -- Spawned by: `/implement-change`
- **`research.md`** -- Spawned by: `/brainstorm`, `/propose`, `/implement-change`
```

### Spawned By Declaration (in Agent Files)

```markdown
# Spawned By
- `brainstorm`
- `propose`
- `implement-change`
```

---

## 6. Available Tools

### Core Built-in Tools

| Tool | Syntax | Description |
|------|--------|-------------|
| `grep` | `grep` | Fast content search using ripgrep |
| `glob` | `glob` | File pattern matching |
| `read` | `read` | Read file contents |
| `write` | `write` | Write file contents |
| `edit` | `edit` | Edit file contents |
| `bash` | `bash` | Execute shell commands |

### oh-my-opencode Extended Tools

**Background Tasks:**
| Tool | Description |
|------|-------------|
| `background_task` | Launch agents in new sessions (sync or async) |
| `background_output` | Fetch results by task ID |
| `background_cancel` | Abort running tasks |

**LSP Integration:**
| Tool | Description |
|------|-------------|
| `lsp_goto_definition` | Jump to symbol definition |
| `lsp_find_references` | Find all usages across workspace |
| `lsp_diagnostics` | Get errors/warnings from language server |
| `lsp_rename` | Rename symbols across all files |

**Code Search:**
| Tool | Description |
|------|-------------|
| `ast_grep_search` | AST-aware pattern matching (25 languages) |
| `ast_grep_replace` | AST-aware refactoring with dry-run support |

### MCP Servers (Built-in with oh-my-opencode)

| MCP | Purpose | URL |
|-----|---------|-----|
| `websearch` | Real-time web search via Exa AI | `https://mcp.exa.ai/mcp` |
| `context7` | Official library documentation | `https://mcp.context7.com/mcp` |
| `grep_app` | GitHub code search via grep.app | `https://mcp.grep.app` |

### Tool Configuration in opencode.jsonc

```json
{
  "mcp": {
    "serena": {
      "type": "local",
      "command": [
        "uvx",
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server",
        "--context", "ide",
        "--project", "."
      ],
      "enabled": true,
      "timeout": 10000
    }
  }
}
```

---

## 7. Non-Interactive CLI Syntax

### Basic CLI Usage

```bash
# Run with a task prompt
opencode run "your task description"

# Specify model
opencode run "task" --model=openai/gpt-5.1-codex-high

# With provider prefix
opencode run "task" --model=anthropic/claude-sonnet-4-5
```

### CLI Arguments

| Argument | Description |
|----------|-------------|
| `run "<prompt>"` | Execute a task with the given prompt |
| `--model=<provider>/<model>` | Specify the model to use |
| `--verbose` | Enable verbose output |
| `--json` | Output in JSON format |

### Debug Flags

```bash
# Enable plugin debugging
DEBUG_CODEX_PLUGIN=1 opencode run "test" --model=openai/your-model

# Enable request logging
ENABLE_PLUGIN_REQUEST_LOGGING=1 opencode run "test"

# Disable Codex mode temporarily
CODEX_MODE=0 opencode run "task"
```

### Specifying Agents/Instructions

Agents and instructions are loaded automatically from:
1. `.opencode/AGENTS.md` - Project-wide instructions
2. `.opencode/agents/*.md` - Agent definitions
3. `.opencode/commands/*.md` - Slash commands

Custom instructions can be loaded via plugins or configuration files.

---

## 8. Additional Features

### Plugin System

```json
{
  "plugin": [
    "opencode-antigravity-auth@1.3.0",
    "opencode-openai-codex-auth"
  ]
}
```

### Model Options (per-provider)

```json
{
  "provider": {
    "openai": {
      "options": {
        "reasoningEffort": "medium",      // low, medium, high, xhigh
        "reasoningSummary": "auto",       // auto, concise, detailed, off
        "textVerbosity": "medium",        // low, medium, high
        "store": false                    // Required for Codex API
      }
    }
  }
}
```

### Model Variants

```json
{
  "models": {
    "gpt-5.1-codex-low": {
      "name": "GPT 5.1 Codex Low (OAuth)",
      "limit": {
        "context": 272000,
        "output": 128000
      },
      "modalities": {
        "input": ["text", "image"],
        "output": ["text"]
      },
      "options": {
        "reasoningEffort": "low"
      }
    }
  }
}
```

### Keybinds

```json
{
  "keybinds": {
    "leader": "alt+x"
  }
}
```

### Theme

```json
{
  "theme": "opencode"
}
```

### Formatter

```json
{
  "formatter": false
}
```

---

## Configuration File Reference

### Full opencode.jsonc Example

```json
{
  "$schema": "https://opencode.ai/config.json",
  "formatter": false,
  "theme": "opencode",
  "keybinds": {
    "leader": "alt+x"
  },
  "model": "anthropic/claude-sonnet-4-5",
  "mcp": {
    "serena": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide", "--project", "."],
      "enabled": true,
      "timeout": 10000
    }
  },
  "plugin": [
    "opencode-antigravity-auth@1.3.0",
    "opencode-openai-codex-auth"
  ],
  "provider": {
    "openai": {
      "options": {
        "reasoningEffort": "medium",
        "reasoningSummary": "auto",
        "textVerbosity": "medium",
        "include": ["reasoning.encrypted_content"],
        "store": false
      },
      "models": {
        "gpt-5.1-codex-medium": {
          "name": "GPT 5.1 Codex Medium (OAuth)",
          "limit": { "context": 272000, "output": 128000 },
          "modalities": { "input": ["text", "image"], "output": ["text"] },
          "options": { "reasoningEffort": "medium" }
        }
      }
    }
  }
}
```

---

## Comparison Notes

### vs. Claude Code
- OpenCode is CLI-first; Claude Code has richer IDE integration
- OpenCode has a plugin ecosystem for provider flexibility
- Both support AGENTS.md conventions

### vs. Cursor
- OpenCode is terminal-based; Cursor is IDE-based
- OpenCode uses API keys or OAuth plugins; Cursor uses subscription
- OpenCode has MCP server support; Cursor has built-in AI features

### vs. Codex CLI
- OpenCode supports multiple providers; Codex is OpenAI-only
- OpenCode has plugin/MCP ecosystem; Codex is simpler
- Both support non-interactive CLI modes
