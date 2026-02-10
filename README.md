# claptrap

Custom AI agents to use with Github Copilot, Claude, Codex, Gemini, etc.

This repository contains a set of custom AI agents designed to work with various large language models (LLMs). These agents assist with software development tasks by following structured workflows and principles.

See the **[Workflow Guide](docs/workflow.md)** for complete documentation.

## Installation

Run the bootstrap installer from your target project directory:

```bash
python3 ~/projects/claptrap/bootstrap/install.py
python3 ~/projects/claptrap/bootstrap/install.py mcp --env opencode # cursor, codex, claude, gemini, github-copilot
python3 ~/projects/claptrap/bootstrap/install.py verify
```

See [bootstrap/README.md](bootstrap/README.md) for detailed installation options.

## MCP Servers

```bash
claude --model sonnet --allow-dangerously-skip-permissions -p "Install Serena and context7 MCP servers for Github CoPilot using the instructions here: @~/projects/claptrap/bootstrap/mcp_setup.md"

codex --model gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox exec "Install Serena and context7 MCP servers for Claude using the instructions here: @~/projects/claptrap/bootstrap/mcp_setup.md"
```

See [bootstrap/mcp_setup.md](bootstrap/mcp_setup.md) for for more information.

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
