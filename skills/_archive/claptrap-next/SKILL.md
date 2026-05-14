---
name: claptrap-next
description: Use when you want to advance a claptrap workflow project and need to determine what step comes next based on the current ROADMAP state.
---

# claptrap-next

## Overview

Reads `.planning/ROADMAP.md` in the current checkout, determines the active milestone and phase state, presents 1-3 logical next actions, and points the user to the appropriate claptrap command.

## Algorithm

1. Read `.planning/ROADMAP.md` if it exists.
   - If the file is missing, check for local milestone branches matching `feature/M##-*`.
   - If one or more such branches exist, treat that as a likely branch-selection problem rather than `Not Started`: tell the user which branch or branches to inspect next.
   - Only treat the workflow as `Not Started` when `.planning/ROADMAP.md` is missing and no milestone feature branches exist.
2. Parse the **Current Position** block:
   - `Milestone:` -> extract `M##-slug`
   - `Phase:` -> extract phase number (`X of Y`) and `P##-slug`
   - `Status:` -> one of the values in the table below
3. If status is `In progress`, run `git status` to check for uncommitted changes. Record whether the workspace is **dirty** or **clean**.
4. Use the **Status -> Actions** table to build the option list (most recommended first).
5. Present options using the platform's option-selection tool when available; otherwise list the choices plainly.
6. Recommend the matching claptrap command from the **Command Dispatch** table and pass the parsed `M##-slug` / `P##-slug` as arguments.

## Status -> Actions

| ROADMAP Status | Option 1 (Recommended) | Option 2 | Option 3 |
|---|---|---|---|
| `Not Started` / missing | Brainstorm new milestone | -- | -- |
| `Ready to plan` | Plan current phase | Brainstorm new milestone | -- |
| `Planning` | Resume planning current phase | -- | -- |
| `Ready to execute` | Execute current phase | Re-plan current phase | -- |
| `In progress` (workspace clean) | Complete current phase | -- | -- |
| `In progress` (workspace dirty) | Resume execution | Complete phase anyway | -- |
| `Phase complete` (stale, phases remain) | Plan next phase | Complete milestone early | -- |
| `Phase complete` (stale, last phase) | Complete milestone | -- | -- |
| `Ready to complete milestone` | Complete milestone | -- | -- |
| `Milestone complete` | Brainstorm new milestone | -- | -- |

## Command Dispatch

| Action | Command to run |
|---|---|
| Brainstorm new milestone | `claptrap-brainstorm` |
| Plan current/next phase | `claptrap-plan M##-slug P##-slug` |
| Resume planning | `claptrap-plan M##-slug P##-slug` |
| Re-plan current phase | `claptrap-plan M##-slug P##-slug` |
| Execute current phase | `claptrap-execute-plan M##-slug P##-slug` |
| Resume execution | `claptrap-execute-plan M##-slug P##-slug` |
| Complete current phase | `claptrap-complete-phase M##-slug P##-slug` |
| Complete phase anyway | `claptrap-complete-phase M##-slug P##-slug` |
| Complete milestone / Complete milestone early | `claptrap-complete-milestone M##-slug` |

## Extracting the Next Phase

When a stale ROADMAP still shows `Phase complete`, treat it as a handoff state rather than a stable one: if phases remain, use the listed `Current Position -> Phase` value and continue with planning; if the milestone is on its last phase, continue with milestone completion.

## Common Mistakes

- **Forgetting to re-read after complete-phase:** For non-final phases, the ROADMAP advances the phase pointer automatically; always read the current value, never assume the next phase slug.
- **Passing stale slugs:** Extract `M##-slug` and `P##-slug` fresh from the ROADMAP each time this skill runs.
- **Skipping workspace status check:** Always check for dirty state before offering `complete phase` when status is `In progress`; a dirty workspace means execution is incomplete.
