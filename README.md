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

### Test
To test which provider is successfully running in OpenCode:
```bash
opencode run "hello" --model anthropic/claude-haiku-4-5  # Claude
opencode run "hello" --model cursor/auto  # Cursor
opencode run "hello" --model github-copilot/claude-haiku-4.5  # GitHub Copilot
opencode run "hello" --model openai/gpt-5.2 --variant=medium  # OpenAI Codex
opencode run "hello" --model google/gemini-3-flash-preview  # Gemini
opencode run "Hello" --model=google/antigravity-claude-sonnet-4-5-thinking --variant=max  # AntiGravity
```

### Plugins

**OpenAI Codex Plugin**
https://github.com/numman-ali/opencode-openai-codex-auth

Paste the following into any LLM agent:
"""
Install the OpenAI Codex authentication plugin for OpenCode following the steps below.  If you run into issues, stop and ask for help.

1. Remove any existing installation: `npx -y opencode-openai-codex-auth@latest --uninstall --all`
2. Install the plugin: `npx -y opencode-openai-codex-auth@latest`
3. Read the Configuration page here for the steps below: `https://raw.githubusercontent.com/numman-ali/opencode-openai-codex-auth/main/docs/configuration.md`
4. Edit the OpenCode configuration file at `~/.config/opencode/opencode.jsonc`:
  - Update the `plugin` and `provider` sections as shown in the Configuration page.
  - Add the following model definitions under the `models:` section. Only install these models. For all use: `reasoningSummary: auto` and  `store: false`.
    - `GPT-5.2` (ReasoningEffort: `medium` and `xhigh` )
    - `GPT-5.2-Codex` (ReasoningEffort: `medium` and `xhigh`)
"""

**Cursor Plugin**
https://github.com/POSO-PocketSolutions/opencode-cursor-auth

Paste the following into any LLM agent:
```
Install the Cursor authentication plugin for OpenCode following the steps below.  If you run into issues, stop and ask for help.

1. Remove any existing installation: `npm uninstall opencode-cursor-auth` and `rm -rf ~/.cache/opencode/node_modules/opencode-cursor-auth`
2. Read the Installation page here for the steps below: `https://raw.githubusercontent.com/POSO-PocketSolutions/opencode-cursor-auth/main/README.md`
3. Follow the instructions to install and configure the Cursor plugin by editing `~/.config/opencode/opencode.jsonc`.
  - Use `@latest` for the plugin instead of the specified version in the instructions.
  - Assume the cursor-agent and bun are already installed.
4. Only install the Cursor models listed below.  Do not configure other models.
- "auto": { "name": "Cursor Auto" },
- "gpt-5.2-high": { "name": "Cursor GPT-5.2 High" },
- "gpt-5.2-codex-high": { "name": "Cursor GPT-5.2 Codex High" },
- "sonnet-4.5": { "name": "Cursor Sonnet 4.5" },
- "sonnet-4.5-thinking": { "name": "Cursor Sonnet 4.5 Thinking" },
- "opus-4.5": { "name": "Cursor Opus 4.5" },
- "opus-4.5-thinking": { "name": "Cursor Opus 4.5 Thinking" },
- "gemini-3-pro": { "name": "Cursor Gemini 3 Pro" },
- "gemini-3-flash": { "name": "Cursor Gemini 3 Flash" },
- "grok": { "name": "Cursor Grok" }
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

Paste the following into any LLM agent:
```markdown
Install the Gemini authentication plugin for OpenCode following the steps below.  If you run into issues, stop and ask for help.

1. Remove any existing installation: `rm -rf ~/.cache/opencode/node_modules/opencode-gemini-auth`
2. Read the Installation page here for the steps below: `https://raw.githubusercontent.com/jenslys/opencode-gemini-auth/main/README.md`
3. Follow the instructions to install and configure the Gemini plugin by editing `~/.config/opencode/opencode.jsonc`.
  - Use the environment variable $GOOGLE_CLOUD_PROJECT_ID as the Google Cloud Project ID.
  - Use `high` for the `thinkingLevel` and enable `includeThoughts`.
  - Only configure the Gemini models listed below.  Do not configure other models.
    - `gemini-3-flash-preview`
    - `gemini-3-pro-preview`
```

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

***AntiGravity Plugin**
https://github.com/NoeFabris/opencode-antigravity-auth

Pasthe the following into any LLM agent:
```
Install the opencode-antigravity-auth plugin and add the Antigravity model definitions to ~/.config/opencode/opencode.json by following: https://raw.githubusercontent.com/NoeFabris/opencode-antigravity-auth/dev/README.md
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
