# MCP Servers Setup

Instructions on how to install and configure various MCP Servers in various environments.  The current list of MCP Servers is:
- Serena
- Snowflake
- (Coming Soon) Context7

## MCP Server Types

- Local (stdio) servers - Run local processes (preferred)
- Remote (HTTP) servers - Connect to external services


## Instructions:
- Before installing any MCP Servers, use the environment-specific MCP CLI command below to check if they are already installed.
- Each MCP Server should be installed and configured system-wide (not per-project).
- Install as a local STDIO server.  Do not install using the Remote or Docker/container instructions.
- When finished, use the environment-specific MCP CLI command below to verify each MCP server is installed successfully.

## Environment Example Config Files

See the following template config files for each environment.

The `env`/`environment` key for each environment's config file below is optional.

### Cursor

https://cursor.com/docs/context/mcp#stdio-server-configuration

To check if a MCP Server is already installed, use the `agent mcp list` command.

To add a MCP Server, add the following to your `~/.cursor/mcp.json` file:
```json
{
  "mcpServers": {
    "my-local-mcp-server": {
      "command": "uvx",
      "args": ["-y", "my-mcp-command", <additional-args>],
      "env": {
        "API_KEY": "${env:API_KEY}"
      }
    }
  }
}
```

### Github Copilot

https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp#writing-a-json-configuration-for-mcp-servers

To check if a MCP Server is already installed, use the `cat ~/.copilot/mcp-config.json` command.

To add a MCP Server, add the following to your `~/.copilot/mcp-config.json` file:
```json
{
  "mcpServers": {
    "my-local-mcp-server": {
      "command": "uvx",
      "args": [ "-y", "my-mcp-command", <additional-args> ],
      "env": {
        "MY_ENV_VAR": "my_env_var_value"
      }
    }
  }
}
```

### OpenCode

https://opencode.ai/docs/mcp-servers/#local

To check if a MCP Server is already installed, use the `opencode mcp list` command.  After adding a MCP Server, use the `opencode mcp list --print-logs` command to verify it is installed successfully.

To add a MCP Server, add the following to your `~/.config/opencode/opencode.jsonc` file:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "my-local-mcp-server": {
      "type": "local",
      "command": [ "<command>", "<args>" ],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "my_env_var_value"
      }
    },
  },
}
```

### Claude Code

https://code.claude.com/docs/en/mcp#option-3%3A-add-a-local-stdio-server

To check if a MCP Server is already installed, use the `claude mcp list` command.

To add a MCP Server, use the following command:
```bash
claude mcp add --scope user --env VAR1=VALUE1 --env VAR2=VALUE2 -- <mcp-server-name> -- <command> <args>
```

### Codex

https://developers.openai.com/codex/mcp/#add-an-mcp-server

To check if a MCP Server is already installed, use the `codex mcp list` command.

To add a MCP Server, use the following command:
```bash
codex mcp add <mcp-server-name> --env VAR1=VALUE1 --env VAR2=VALUE2 -- <command> <args>
```

## MCP Server Setup

See the above instructions for adding an MCP Server to each environment.

### Serena MCP

A powerful coding agent toolkit providing semantic code retrieval and editing.  See [Serena documentation](https://oraios.github.io/serena) for more details.

The `context` arg can be one of the following:
- `ide` - Use this if not otherwise specified
- `codex` - Use this if your environment is Codex
- `claude-code` - Use this if your environment is Claude Code

Command: `uvx`
Args: `--from git+https://github.com/oraios/serena serena start-mcp-server --context <context> --project-from-cwd --open-web-dashboard false`

### context7 MCP

Context7 MCP pulls up-to-date, version-specific documentation and code examples straight from the source — and places them directly into your prompt.

https://github.com/upstash/context7

Command: `npx`
Args: `-y @upstash/context7-mcp --api-key <api-key>`

The API key is optional, but is recommended for higher rate limits.

### Snowflake MCP

This Snowflake MCP server provides tooling for Snowflake Cortex AI, object management, and SQL orchestration.  See [Snowflake documentation](https://github.com/Snowflake-Labs/mcp) for more details.

Command: `npx`
Args: `-y @snowflake-labs/mcp --service-config-file <service-config-file> --account <account> --user <user> --role <role> --warehouse <warehouse> --private-key-file <private-key-file> --private-key-file-pwd <private-key-file-pwd> --authenticator <authenticator>`
Environment Variables:
- PRIVATE_KEY_FILE_PWD
