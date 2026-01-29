---
name: "claptrap-propose"
description: "Generate OpenSpec artifacts (proposal, specs, tasks) from an approved design.md, with alignment + feasibility review."
model: claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# /claptrap-propose

Generate OpenSpec artifacts from a design document. This command does NOT implement code.

## Invocation

```
/claptrap-propose .claptrap/designs/<slug>/design.md
/claptrap-propose                                      # auto-detect most recent design
/claptrap-propose --regenerate proposal|specs|tasks|all --change <change-id>
```

## Outputs

- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/specs/**/spec.md`
- `openspec/changes/<change-id>/tasks.md`
- `openspec/changes/<change-id>/.source` (link to source design.md)

## Rules

- Invoke the `claptrap-memory` skill to read and write memories as instructed.
- Invoke the `claptrap-propose` skill and follow it exactly.

**Arguments:** `$ARGUMENTS`
