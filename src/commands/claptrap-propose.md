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

# Claptrap Propose

Generate OpenSpec artifacts from a design document. This command does NOT implement code.

## Invocation

```bash
/claptrap-propose .claptrap/designs/<YYYY-MM-DD><feature-slug>/design.md # e.g. /claptrap-propose .claptrap/designs/2024-01-15-new-auth-system/design.md
/claptrap-propose                                      # auto-detect most recent design
/claptrap-propose --regenerate proposal|specs|tasks|all --change <change-id>
```

## Outputs

- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/specs/**/spec.md`
- `openspec/changes/<change-id>/tasks.md`

## Rules

- Invoke the `claptrap-propose` skill and follow it exactly.

**Arguments:** `$ARGUMENTS`
