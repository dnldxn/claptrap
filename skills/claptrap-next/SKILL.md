---
name: claptrap-next
description: Use when you want to advance a claptrap workflow project and need to determine what step comes next based on the current ROADMAP state.
---

# claptrap-next

## Overview

Reads `.planning/ROADMAP.md` in the current project, determines the active milestone and phase state, presents 1–3 logical next actions, and triggers the appropriate claptrap sub-skill.

## Algorithm

1. Check whether `.planning/ROADMAP.md` exists. If not, treat status as `Not Started`.
2. Parse the **Current Position** block:
   - `Milestone:` → extract `M##-slug`
   - `Phase:` → extract phase number (`X of Y`) and `P##-slug`
   - `Status:` → one of the values in the table below
3. If status is `In progress`, inspect `.worktrees/M##-slug/P##-slug/` to check for unmerged local changes (run `git status` inside the worktree directory). Record whether it is **dirty** or **clean**.
4. Use the **Status → Actions** table to build the option list (most recommended first).
5. Present options to the user with the `question` tool (single-select).
6. Load the matching sub-skill from the **Skill Dispatch** table and pass the parsed `M##-slug` / `P##-slug` as context.

## Status → Actions

| ROADMAP Status | Option 1 (Recommended) | Option 2 | Option 3 |
|---|---|---|---|
| `Not Started` / missing | Brainstorm new milestone | — | — |
| `Ready to plan` | Plan current phase | Brainstorm new milestone | — |
| `Planning` | Resume planning current phase | — | — |
| `Ready to execute` | Execute current phase | Re-plan current phase | — |
| `In progress` (worktree clean) | Complete current phase | — | — |
| `In progress` (worktree dirty) | Resume execution | Complete phase anyway | — |
| `Phase complete` (phases remain) | Plan next phase | Complete milestone early | — |
| `Phase complete` (last phase) | Complete milestone | — | — |
| `Milestone Complete` | Archive milestone | Brainstorm new milestone | — |

## Skill Dispatch

| Action | Sub-skill to load |
|---|---|
| Brainstorm new milestone | `claptrap-brainstorm` |
| Plan current/next phase | `claptrap-plan` (pass `M##-slug P##-slug`) |
| Resume planning | `claptrap-plan` (pass `M##-slug P##-slug`) |
| Execute current phase | `claptrap-execute` (pass `M##-slug P##-slug`) |
| Resume execution | `claptrap-execute` (pass `M##-slug P##-slug`) |
| Complete current phase | `claptrap-complete-phase` (pass `M##-slug P##-slug`) |
| Complete phase anyway | `claptrap-complete-phase` (pass `M##-slug P##-slug`) |
| Complete milestone / Archive milestone | `claptrap-complete-milestone` (pass `M##-slug`) |

## Extracting the Next Phase

When status is `Phase complete` and phases remain, read the `Current Position → Phase` field — the ROADMAP update rules advance it automatically after `ct-complete-phase`. Use whichever phase slug is now listed.

## Common Mistakes

- **Forgetting to re-read after complete-phase:** The ROADMAP advances the phase pointer automatically; always read the current value, never assume the next phase slug.
- **Passing stale slugs:** Extract `M##-slug` and `P##-slug` fresh from the ROADMAP each time this skill runs.
- **Skipping worktree check:** Always check for dirty state before offering `complete phase` when status is `In progress`; a dirty worktree means execution is incomplete.
