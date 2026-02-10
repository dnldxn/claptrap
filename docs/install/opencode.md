# OpenCode Installation

## Configuration File

The configuration file is located at `~/.config/opencode/opencode.jsonc`.

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "formatter": false,
  "plugin": ["opencode-cursor-auth@latest"],
  "provider": {
    "cursor": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Cursor Agent (local)",
      "options": {"baseURL": "http://127.0.0.1:32123/v1"},
      "models": {
        "auto": {"name": "Auto"},
        "gpt-5.2-high": {"name": "GPT-5.2 High"},
        "gpt-5.3-codex-high": {"name": "GPT-5.3 Codex High"},
        "haiku-4.5-thinking": {"name": "Haiku 4.5 Thinking"},
        "sonnet-4.5-thinking": {"name": "Sonnet 4.5 Thinking"},
        "opus-4.6-thinking": {"name": "Opus 4.6 Thinking"},
        "gemini-3-pro": {"name": "Gemini 3 Pro"},
        "gemini-3-flash": {"name": "Gemini 3 Flash"}
      }
    }
  },
  "mcp": {
    "serena": {
      "type": "local",
      "command": ["uvx", "--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--open-web-dashboard", "false", "--context", "ide"],
      "enabled": true
    },
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp"],
      "enabled": true
    },
    "snowflake": {
      "type": "local",
      "command": ["uvx", "snowflake-labs-mcp", "--service-config-file", "/Users/ddixon/.snowflake/mcp_service_config.yaml", "--connection-name", "snowflake_mcp"],
      "enabled": true
    }
  }
}
```

## Test

To test which providers are successfully configured:
```bash
opencode run "hello" --model anthropic/claude-haiku-4-5  # Claude
opencode run "hello" --model cursor/gpt-5.3-codex-high  # Cursor
opencode run "hello" --model github-copilot/claude-haiku-4.5  # GitHub Copilot
opencode run "hello" --model openai/gpt-5.2 --variant=medium  # OpenAI Codex
opencode run "hello" --model google/gemini-3-flash-preview  # Gemini
opencode run "Hello" --model=google/antigravity-claude-sonnet-4-5-thinking --variant=max  # AntiGravity
```

## Cursor Plugin
https://github.com/POSO-PocketSolutions/opencode-cursor-auth

Remove any existing installation: `npm uninstall opencode-cursor-auth` and `rm -rf ~/.cache/opencode/node_modules/opencode-cursor-auth`

```bash
opencode auth login
# For Cursor:
# - Select provider: Other
# - Provider id: cursor
# - Method: Login via cursor-agent (opens browser)
```

## CodeNomad

```bash
npx @neuralnomads/codenomad --dangerously-skip-auth --host 127.0.0.1 --https false --http true
```