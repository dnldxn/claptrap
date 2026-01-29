---
name: "claptrap-brainstorm"
description: "Turn ideas into fully formed designs through collaborative dialogue, memory context, and targeted research."
model: claude-opus-4.5
models:
  cursor: anthropic/claude-opus-4.5
  github-copilot: claude-opus-4.5
  claude: opus
  opencode: anthropic/claude-opus-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# /claptrap-brainstorm

Turn raw ideas into a validated design document through structured dialogue.

## Invocation

```
/claptrap-brainstorm "Add user authentication with OAuth support"
```

## Output

`.claptrap/designs/<feature-slug>/design.md`

## Rules

- Invoke the `claptrap-memory` skill to read and write memories as instructed.
- Invoke the `claptrap-brainstorming` skill and follow it exactly.
- After finalizing, tell the user to run `/claptrap-propose` to generate OpenSpec artifacts.

**User Brainstorm Idea/Prompt:** $ARGUMENTS
