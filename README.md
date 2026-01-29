# claptrap

Custom AI agents to use with Github Copilot, Claude, Codex, Gemini, etc.

This repository contains a set of custom AI agents designed to work with various large language models (LLMs). These agents assist with software development tasks by following structured workflows and principles.

## Quick Start

```bash
# Install into your project
cd /path/to/your/project
python3 /path/to/claptrap/bootstrap/install.py

# Start the workflow
/claptrap-brainstorm "Add user authentication"
/claptrap-propose
/claptrap-review
/opsx:apply
```

See the **[Workflow Guide](docs/workflow.md)** for complete documentation.

## Agents Overview

The repository includes the following AI agents in `src/agents/`:

| Agent | Purpose |
|-------|---------|
| `ui-designer` | Designs user interfaces based on project requirements |
| `plan-reviewer` | Validates proposals and tasks against requirements |
| `alignment-reviewer` | Validates that proposals align with project goals |
| `feasibility-reviewer` | Assesses technical feasibility and risks |
| `code-reviewer` | Reviews code changes for correctness and maintainability |
| `refactor` | Refactors code for simplicity and readability |
| `research` | Researches docs and writes concise developer references |

For how agents fit into the workflow, see [docs/workflow.md](docs/workflow.md).

## Installation

Run the bootstrap installer from your target project directory:

```bash
python3 /path/to/claptrap/bootstrap/install.py
```

Or create a shell alias for convenience:

```bash
alias claptrap-install='python3 "$HOME/projects/claptrap/bootstrap/install.py"'
```

See [bootstrap/README.md](bootstrap/README.md) for detailed installation options.

## MCP Servers

See [bootstrap/mcp_setup.md](bootstrap/mcp_setup.md) for instructions on how to install and configure various MCP Servers in each environment.

## OpenCode Setup

### Claude Code Plugin for OpenCode
```bash
opencode auth login

# Test
opencode run --model anthropic/claude-haiku-4-5 "hello"
```

### Github Copilot
```bash
opencode run --model github-copilot/claude-haiku-4.5 "hello"
```

```bash

### Codex Plugin for OpenCode
```bash
# OpenAI Codex adapter for OpenCode
# https://github.com/numman-ali/opencode-openai-codex-auth
npx -y opencode-openai-codex-auth@latest

# Test
opencode run --model openai/gpt-5.1-codex-mini "hello"
```

### Cursor Plugin for OpenCode

https://github.com/POSO-PocketSolutions/opencode-cursor-auth

```bash
curl -fsS https://cursor.com/install | bash  # Install Cursor CLI
npm install opencode-cursor-auth  # Install Cursor plugin for OpenCode
```

Add to ~/.config/opencode/opencode.jsonc:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-cursor-auth@1.0.16"],
  "provider": {
    "cursor": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Cursor Agent (local)",
      "options": {
        "baseURL": "http://127.0.0.1:32123/v1"
      },
      "models": {
        "auto": { "name": "Cursor Auto" },
        "gpt-5.2-high": { "name": "Cursor GPT-5.2 High" },
        "gpt-5.2-codex-high": { "name": "Cursor GPT-5.2 Codex High" },
        "sonnet-4.5": { "name": "Cursor Sonnet 4.5" },
        "sonnet-4.5-thinking": { "name": "Cursor Sonnet 4.5 Thinking" },
        "opus-4.5": { "name": "Cursor Opus 4.5" },
        "opus-4.5-thinking": { "name": "Cursor Opus 4.5 Thinking" },
        "gemini-3-pro": { "name": "Cursor Gemini 3 Pro" },
        "gemini-3-flash": { "name": "Cursor Gemini 3 Flash" },
        "grok": { "name": "Cursor Grok" }
      }
    }
  }
}
```

```bash
opencode auth login
# For Cursor:
# - Select provider: Other
# - Provider id: cursor
# - Method: Login via cursor-agent (opens browser)

# Test
opencode run --model cursor/opus-4.5-thinking "hello"
```

### Gemini Plugin for OpenCode

Add `opencode-gemini-auth@latest` to the plugins array in `~/.config/opencode/opencode.jsonc`.
```bash
opencode auth login

# Test
opencode run --model google/gemini-3-flash-preview "hello"
```

## Zed IDE

Click the "+ Add Agent" -> "Add Custom Agent", then add this to the "agent_servers" section:
```json
    "Cursor": {
      "type": "custom",
      "command": "npx",
      "args": ["@blowmage/cursor-agent-acp"],
      "env": {},
    },
    "Copilot": {
      "type": "custom",
      "command": "copilot",
      "args": ["--acp"],
      "env": {},
    },
```
