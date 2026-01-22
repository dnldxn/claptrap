# Agent Workflow

This folder contains provider-neutral agent definitions used by command-driven workflows in this repo. Commands spawn these agents as subagents with fresh context and bounded scope.

## Core Pipeline (Command-Driven)

1. **Propose** (`/propose`)
   - Spawns: `alignment-reviewer.md`, `feasibility-reviewer.md`
   - Output: change proposal(s), task checklist(s), spec deltas, alignment + feasibility status
2. **Apply + Review** (`/implement-change`)
   - Spawns: `code-reviewer.md`, `refactor.md` (for refactor-only changes)
   - Output: code changes, updated tasks, review findings, and fixes
3. **Archive** (`/archive-change`)
   - No agent; completes the OpenSpec archive step

## Agent Spawning Map

- **`alignment-reviewer.md`** — Spawned by: `/propose`, `/brainstorm` (via `design-to-proposal`)
- **`feasibility-reviewer.md`** — Spawned by: `/propose`, `/brainstorm` (via `design-to-proposal`)
- **`plan-reviewer.md`** — Spawned by: `/propose` for plan validation
- **`code-reviewer.md`** — Spawned by: `/implement-change`
- **`research.md`** — Spawned by: `/brainstorm`, `/propose`, `/implement-change`
- **`ui-designer.md`** — Spawned by: `/brainstorm` when UI/UX artifacts are required
- **`refactor.md`** — Spawned by: `/implement-change` for refactor-only changes

## Subagent Characteristics

- Fresh context: each subagent starts with no shared conversation state.
- Bounded scope: input is limited to the command-provided artifacts.
- Specific outputs: follow explicit output formats (e.g., `APPROVED` or `REVISE`).

