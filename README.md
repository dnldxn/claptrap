# claptrap
Custom AI agents to use with Github Copilot, Claude, Codex, Gemini, etc

This repository contains a set of custom AI agents designed to work with various large language models (LLMs) such as Github Copilot, Claude, Codex, Gemini, and others. These agents are tailored to assist with software development tasks by following specific workflows and principles.

## Agents Overview
The repository includes the following AI agents in `src/agents/`, each with a distinct role in the software development lifecycle:

1. **UI Designer** (`ui-designer.md`): Designs user interfaces based on project requirements.
2. **Plan Reviewer** (`plan-reviewer.md`): Validates proposals and tasks against requirements.
3. **Alignment Reviewer** (`alignment-reviewer.md`): Validates that proposals align with project goals.
4. **Feasibility Reviewer** (`feasibility-reviewer.md`): Assesses technical feasibility and risks.
5. **Code Reviewer** (`code-reviewer.md`): Reviews code changes for correctness and maintainability.
6. **Refactor** (`refactor.md`): Refactors code for simplicity and readability while preserving behavior.
7. **Research** (`research.md`): Researches docs and writes concise developer references.

For the full workflow and how agents fit together, see `src/agents/AGENTS.md`.


## Installation

Run the bootstrap installer from your target project directory:

```bash
python3 /path/to/claptrap/bootstrap/install.py
```

Or create a shell alias for convenience:

```bash
alias claptrap-install='python3 "$HOME/projects/claptrap/bootstrap/install.py"'
```

See `bootstrap/README.md` for detailed installation options and environment-specific setup.

## MCP Servers

See `bootstrap/mcp_setup.md` for instructions on how to install and configure various MCP Servers in each environment.

## OpenCode Setup

### Claude Code Plugin for OpenCode
```bash
opencode auth login

# Test
opencode run --model anthropic/claude-haiku-4-5 "hello"
```

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
  "plugin": [
    "opencode-cursor-auth@1.0.16"
  ],
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

## Usage

```bash
/brainstorm
/propose <design-path>
/implement-change <change-name>
/archive-change <change-name>
/finish-openspec-change
```

## Designs

Design exploration documents live in `src/designs/`. Use `src/designs/TEMPLATE.md` and
store new designs at `src/designs/<feature-slug>/design.md` (kebab-case feature slug).

## OpenSpec Commands

```bash
openspec list                      # List changes
openspec create <name>             # Create change
openspec validate <name>           # Validate change
openspec show <name>               # Show details
openspec archive <name> --yes      # Archive completed change
openspec update                    # Update integration
```

## Memory System

The repository includes a lightweight memory system to capture and retain project decisions, patterns, anti-patterns, and lessons learned. See `src/skills/memory/SKILL.md` for usage details.

## Old / Deprecated / Reference

```bash
cd $PROJECT_PATH

# Set your agent CLI command
export AGENT_CLI="claude -p"  # Claude Code
export AGENT_CLI="copilot --prompt"  # GitHub Copilot CLI
export AGENT_CLI="codex exec"  # OpenAI Codex CLI
export AGENT_CLI="agent --model 'gpt-5.2-high' -p"  # Cursor CLI
```
