---
name: "claptrap-review"
description: "Validate proposal/specs/tasks against the source design document before implementation."
model: claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# /claptrap-review

Validate all OpenSpec artifacts against the source design document. This is the explicit quality gate before `/opsx:apply`.

## Invocation

```
/claptrap-review <change-id>
/claptrap-review              # auto-detect most recent change
/claptrap-review --force      # proceed even if verdict is REVISE (writes accepted-risk memory)
```

## Workflow

1. **Resolve change-id**: Use argument if provided, else find most recent directory under `openspec/changes/` (exclude `archive/`).

2. **Load artifacts**:
   - Read `openspec/changes/<id>/.source` to get the design.md path (relative to the change directory)
   - Read the design.md
   - Read `proposal.md`, all `specs/**/spec.md` files, and `tasks.md`

3. **Spawn plan-reviewer**: Pass all artifacts to the `plan-reviewer` agent.

4. **Report verdict**: Output exactly `APPROVED:` or `REVISE:` (no other verdict words).

5. **STOP.**

**Arguments:** `$ARGUMENTS`
