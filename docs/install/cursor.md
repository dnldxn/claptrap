# Cursor Config

## Models

Get current list of available models: `agent models`

Key models below.  Not the full list.
- auto - Auto
- composer-1.5 - Composer 1.5
- gpt-5.3-codex-high - GPT-5.3 Codex High
- gpt-5.2-high - GPT-5.2 High
- opus-4.6-thinking - Claude 4.6 Opus (Thinking)
- sonnet-4.6-thinking - Claude 4.6 Sonnet (Thinking)
- gemini-3-pro - Gemini 3 Pro
- gemini-3-flash - Gemini 3 Flash

## Agents

https://opencode.ai/docs/agents/#markdown

Example agent definition:
```markdown
---
name: security-auditor
description: Security specialist. Use when implementing auth, payments, or handling sensitive data.
model: gpt-5.3-codex-high
readonly: true
---
You are a security expert auditing code for vulnerabilities.  When invoked: ...
```

Explictly  invoke an agent in a session with: `/agent security-auditor`

### Configuration Fields

ALL fields are optional, even `name` and `description`.

- `name`:  Unique identifier for the agent. Used to invoke the agent in sessions.
- `description`:  When to use this subagent. Agent reads this to decide delegation.
- `model`:  Model to use: `fast`, `inherit`, or a specific model ID. Defaults to inherit.
- `readonly`:  If `true`, the subagent runs with restricted write permissions.
- `is_background`:  If `true`, the subagent runs in the background without waiting for completion.
