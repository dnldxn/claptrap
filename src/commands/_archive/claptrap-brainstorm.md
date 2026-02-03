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

# Brainstorming Ideas Into Designs

Turn raw ideas into a validated design document through structured dialogue.

## Invocation

```
/claptrap-brainstorm "<User Idea/Prompt>"
```

## Output

`.claptrap/designs/<YYYY-MM-DD><feature-slug>/design.md` (e.g. `.claptrap/designs/2024-01-15-new-auth-system/design.md`)

## Rules

- Invoke the `claptrap-brainstorming` skill and follow it exactly.
- After finalizing, tell the user to run `/claptrap-propose` to generate OpenSpec artifacts.

**User Brainstorm Idea/Prompt:** $ARGUMENTS
