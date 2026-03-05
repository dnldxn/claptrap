# OpenCode Config

## Models

Get current list of available models: `opencode models`

Key models below.  Not the full list.

- opencode/kimi-k2.5-free
- anthropic/claude-haiku-4-5
- anthropic/claude-opus-4-6
- anthropic/claude-sonnet-4-5
- cursor/auto
- cursor/gemini-3-flash
- cursor/gemini-3-pro
- cursor/gpt-5.2-high
- cursor/gpt-5.3-codex-high
- cursor/haiku-4.5-thinking
- cursor/opus-4.6-thinking
- cursor/sonnet-4.5-thinking
- github-copilot/claude-haiku-4.5
- github-copilot/claude-opus-4.5
- github-copilot/claude-opus-4.6
- github-copilot/claude-sonnet-4.5
- github-copilot/gemini-3-flash-preview
- github-copilot/gemini-3-pro-preview
- github-copilot/gpt-5.2
- github-copilot/grok-code-fast-1
- openai/gpt-5.2
- openai/gpt-5.3-codex

## Agents

https://opencode.ai/docs/agents/#markdown

Example agent definition:

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
tools:
  write: false
  edit: false
  bash: false
---

You are in code review mode. Focus on ...
```

### Configuration Fields

| Field           | Required? | Description                                                                    |
|-----------------|-----------|--------------------------------------------------------------------------------|
| `name`          | Yes       | Unique identifier for the agent. Used to invoke the agent in sessions.         |
| `description`   | Yes       | When to use this subagent. Agent reads this to decide delegation.              |
| `model`         | No        | Model to use: `fast`, `inherit`, or a specific model ID. Defaults to inherit.  |
| `mode`          | No        | `primary`, `subagent`, or `all` (default)                                      |
| `tools`         | No        | Tool permissions for the agent: `write`, `edit`, `bash`                        |
| `hidden`        | No        | If `true`, hide a subagent from the @ autocomplete menu. Useful for subagents. |
| `steps`         | No        | Max number of iterations an agent can perform before being forced to respond   |

## Plugins

- https://github.com/Nomadcxx/opencode-cursor



## opencode.jsonc

```json
{
  "$schema": "https://opencode.ai/config.json",
  "theme": "opencode",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "formatter": false,
  "plugin": ["cursor-acp"],
  "provider": {
    "cursor-acp": {
      "name": "Cursor",
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://127.0.0.1:32124/v1" },
      "models": {
        "auto": { "name": "Auto" },
        "composer-1": { "name": "Composer 1" },
        "gpt-5.2": { "name": "GPT-5.2" },
        "gpt-5.2-high": { "name": "GPT-5.2 High" },
        "gpt-5.2-codex": { "name": "GPT-5.2 Codex" },
        "gpt-5.2-codex-low": { "name": "GPT-5.2 Codex Low" },
        "gpt-5.2-codex-high": { "name": "GPT-5.2 Codex High" },
        "gpt-5.2-codex-xhigh": { "name": "GPT-5.2 Codex Extra High" },
        "gpt-5.2-codex-fast": { "name": "GPT-5.2 Codex Fast" },
        "gpt-5.2-codex-low-fast": { "name": "GPT-5.2 Codex Low Fast" },
        "gpt-5.2-codex-high-fast": { "name": "GPT-5.2 Codex High Fast" },
        "gpt-5.2-codex-xhigh-fast": { "name": "GPT-5.2 Codex Extra High Fast" },
        "gpt-5.1-high": { "name": "GPT-5.1 High" },
        "gpt-5.1-codex-max": { "name": "GPT-5.1 Codex Max" },
        "gpt-5.1-codex-max-high": { "name": "GPT-5.1 Codex Max High" },
        "opus-4.6-thinking": { "name": "Claude 4.6 Opus (Thinking)" },
        "opus-4.6": { "name": "Claude 4.6 Opus" },
        "opus-4.5": { "name": "Claude 4.5 Opus" },
        "opus-4.5-thinking": { "name": "Claude 4.5 Opus (Thinking)" },
        "sonnet-4.5": { "name": "Claude 4.5 Sonnet" },
        "sonnet-4.5-thinking": { "name": "Claude 4.5 Sonnet (Thinking)" },
        "gemini-3-pro": { "name": "Gemini 3 Pro" },
        "gemini-3-flash": { "name": "Gemini 3 Flash" },
        "grok": { "name": "Grok" }
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
    }
  }
}
```
