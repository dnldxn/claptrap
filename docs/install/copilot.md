# Github Copilot Installation

## Configuration File

The configuration file is located at `~/.copilot/mcp-config.json`.

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "ide", "--project-from-cwd", "--open-web-dashboard", "false"]
    }
  }
}
```

## Test

To test which MCP servers are successfully configured:
```bash
copilot mcp list
```
