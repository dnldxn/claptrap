# Agent Workflow

This folder contains provider-neutral agent definitions used by command-driven workflows in this repo. Commands spawn these agents as subagents with fresh context and bounded scope.

## Core Pipeline (Command-Driven)

1. **Propose** (`/claptrap-propose`)
   - Spawns: `alignment-reviewer.md`, `feasibility-reviewer.md`
   - Output: proposal.md, specs/**/spec.md, tasks.md, alignment + feasibility status
2. **Review** (`/claptrap-review`)
   - Spawns: `plan-reviewer.md`
   - Output: APPROVED or REVISE verdict with prioritized issues
3. **Implementation** (`/opsx:apply`)
   - Native OpenSpec command
   - May spawn: `code-reviewer.md`
   - Output: code changes, updated tasks, review findings

## Agent Spawning Map

- **`alignment-reviewer.md`** — Spawned by: `/claptrap-propose`
- **`feasibility-reviewer.md`** — Spawned by: `/claptrap-propose`
- **`plan-reviewer.md`** — Spawned by: `/claptrap-review`
- **`code-reviewer.md`** — Spawned by: `/opsx:apply` (native OpenSpec step)
- **`research.md`** — Spawned by: `/claptrap-brainstorm`, `/claptrap-propose` when external docs needed
- **`ui-designer.md`** — Spawned by: `/claptrap-brainstorm` when UI/UX artifacts are required

## Subagent Characteristics

- Fresh context: each subagent starts with no shared conversation state.
- Bounded scope: input is limited to the command-provided artifacts.
- Specific outputs: follow explicit output formats (e.g., `APPROVED` or `REVISE`).

