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

See [bootstrap/README.md](bootstrap/README.md) for detailed installation options.

## MCP Servers

```bash
claude --model sonnet --allow-dangerously-skip-permissions -p "Install Serena and context7 MCP servers for Github CoPilot using the instructions here: @~/projects/claptrap/bootstrap/mcp_setup.md"

codex --model gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox exec "Install Serena and context7 MCP servers for Claude using the instructions here: @~/projects/claptrap/bootstrap/mcp_setup.md"
```

See [bootstrap/mcp_setup.md](bootstrap/mcp_setup.md) for for more information.

## OpenCode Setup

To test which provider is successfully running in OpenCode:
```bash
opencode run --model auto "hello"
opencode run --model anthropic/claude-haiku-4-5 "hello"  # Claude
opencode run --model cursor/opus-4.5-thinking "hello"  # Cursor
opencode run --model github-copilot/claude-haiku-4.5 "hello"  # GitHub Copilot
opencode run --model openai/gpt-5.1-codex-mini "hello"  # Codex
opencode run --model google/gemini-3-flash-preview "hello"  # Gemini
```

Opencode does not automatically update plugins. To update to the latest version, you must clear the cached plugin:

```bash
# Clear the specific plugin cache
rm -rf ~/.cache/opencode/node_modules/opencode-gemini-auth
rm -rf ~/.cache/opencode/node_modules/opencode-cursor-auth

# Run Opencode to trigger a fresh install
opencode
```

**Codex Plugin**
https://github.com/numman-ali/opencode-openai-codex-auth

```bash
npx -y opencode-openai-codex-auth@latest
```

**Cursor Plugin**
https://github.com/POSO-PocketSolutions/opencode-cursor-auth

```bash
npm install opencode-cursor-auth@latest
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
```

**Gemini Plugin**
https://github.com/jenslys/opencode-gemini-auth

Add `opencode-gemini-auth@latest` to the plugins array in `~/.config/opencode/opencode.jsonc`.
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-gemini-auth@latest"],
  "provider": {
    "google": {
      "models": {
        "gemini-3-flash-preview": {
          "options": {
            "thinkingConfig": {
              "thinkingLevel": "high",
              "includeThoughts": true
            }
          }
        },
        "gemini-3-pro-preview": {
          "options": {
            "thinkingConfig": {
              "thinkingLevel": "high",
              "includeThoughts": true
            }
          }
        }
      }
    }
  }
}
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
