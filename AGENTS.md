# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A personal AI agent configuration toolkit ("claptrap") — a collection of skills, commands, and workflow templates that are installed as symlinks into AI coding assistants (Claude Code, Cursor, OpenCode).

## Installation

```bash
python bootstrap/install.py
```

This script reads `bootstrap/config.yml`, detects which AI providers are installed (`claude`, `opencode`, `agent`), then creates symlinks from each provider's config directory (e.g., `~/.claude/skills/`) into this repo's `skills/` and `commands/` directories. Skills/commands managed externally are referenced as `external/` paths in the config.

Manual setup steps (not handled by the installer) are documented in `README.md`, including symlinking individual workflow commands and updating `~/.claude/CLAUDE.md`.

## Repository Structure

- `bootstrap/` — installer (`install.py`) and `config.yml` mapping features to provider directories
- `commands/` — slash command stubs that delegate to skills via the `claptrap-workflow` skill
- `skills/claptrap-workflow/` — the core workflow skill; all commands dispatch through here
- `skills/claptrap-workflow/references/` — one file per workflow step (`ct-brainstorm`, `ct-plan`, `ct-execute`, `ct-complete-phase`, `ct-complete-milestone`)
- `skills/claptrap-workflow/assets/` — Markdown templates for planning documents (`ROADMAP.md`, `MILESTONE_SUMMARY.md`, `PHASE-PLAN.md`, etc.)
- `skills/claptrap-code-conventions/` — language-specific style guidelines (`python.md`, `snowflake.md`)
- `skills/snowflake/` — Snowflake SQL skill with reference docs
- `skills/jupyter-notebooks/` — Jupyter notebook skill with helper scripts
- `skills/_archive/` — deprecated/retired skills kept for reference
- `docs/install/` — provider-specific installation notes (Cursor, Zed, OpenCode)

## Claptrap Workflow

The five workflow steps run in order: **brainstorm → plan → execute → complete-phase → complete-milestone**.

Planning state lives under `.planning/` in the *target project* (not this repo):

```
.planning/
  ROADMAP.md
  milestones/
    M##-slug/
      DESIGN.md
      RESEARCH.md
      MILESTONE_SUMMARY.md
      M##-P##-slug-PLAN.md
      ...
  _archive/
```

Milestone/phase IDs use zero-padded numbers (`M01`, `P02`) with a kebab-case slug derived from the title. When a dedicated git workspace is created during brainstorming, branches are named `feature/M##-slug` and worktrees go to `.worktrees/M##-slug/`.

### Git Workspace Lifecycle

Branches, worktrees, and commits are scoped to the **milestone**, never to individual phases. The lifecycle spans the five workflow steps:

| Step | Branch / Worktree | Commit Offered |
| --- | --- | --- |
| `ct-brainstorm` | Asks the user whether to create a dedicated workspace. If yes: create branch `feature/M##-slug` from the default branch + worktree `.worktrees/M##-slug/`. If no: stay in the current checkout. | `brainstorm: M##-slug` |
| `ct-plan` | No new branch or worktree. Planning happens in the resolved milestone workspace. | `plan: P##-slug` |
| `ct-execute` | No new per-phase branch. Code and doc changes happen in the milestone workspace. Execution commits are made by the `subagent-driven-development` skill as the plan progresses. | (per plan task) |
| `ct-complete-phase` | No merging. Branch and worktree stay open until the milestone completes. | `docs: P##-slug complete` |
| `ct-complete-milestone` | 1. Offer to commit any uncommitted changes in the milestone workspace. 2. If a dedicated worktree is in use, offer a **squash merge** of `feature/M##-slug` into the default branch, then tag the result `milestone/M##-slug`, then offer to remove `.worktrees/M##-slug/` and delete `feature/M##-slug`. 3. If no dedicated worktree, tag the current commit `milestone/M##-slug` in place. | milestone completion commit + squash merge commit |

**Workspace resolution:** Before any read/write during plan, execute, complete-phase, or complete-milestone, resolve the milestone workspace root: if `.worktrees/M##-slug/.planning/milestones/M##-slug/` exists, use that worktree; otherwise use the current repo root. All work for the milestone stays in that single workspace until the milestone is complete.

### `claptrap-next` skill

The **`claptrap-next`** skill is a router for target projects that use `.planning/ROADMAP.md`. Invoke it when you need to **determine the next claptrap step** from the current ROADMAP (including after idle time or handoff), instead of guessing which of brainstorm / plan / execute / complete-phase / complete-milestone applies.

**Behavior (summary):**

1. Read `.planning/ROADMAP.md` if it exists; if the file is missing, treat the workflow as **not started**.
2. Parse **Current Position**: `Milestone:` (`M##-slug`), `Phase:` (`P##-slug`, phase “X of Y”), `Status:`.
3. If `Status` is **In progress**, run `git status` in the active milestone workspace to distinguish **dirty** (keep executing) vs **clean** (ready to complete the phase). The workspace may be the current checkout or `.worktrees/M##-slug/`.
4. Offer **1–3** next actions ordered by recommendation; after selection, load the matching sub-skill with **fresh** slugs from the ROADMAP.

**Sub-skill dispatch:**

| Situation | Load |
| --- | --- |
| New milestone / early completion paths | `claptrap-brainstorm` |
| Plan or resume planning a phase | `claptrap-plan` (pass `M##-slug` and `P##-slug`) |
| Execute or resume execution | `claptrap-execute` (pass `M##-slug` and `P##-slug`) |
| Complete current phase (including forcing completion when the milestone workspace is dirty) | `claptrap-complete-phase` (pass `M##-slug` and `P##-slug`) |
| Complete milestone or archive | `claptrap-complete-milestone` (pass `M##-slug`) |

**Important:** After `ct-complete-phase`, re-read the ROADMAP—the **Phase** field advances automatically. Do not assume the next `P##-slug` without reading it.

## Skills vs Commands

- A **skill** (`skills/*/SKILL.md`) is loaded by the AI on demand via the `Skill` tool. It contains behavioral instructions.
- A **command** (`commands/*.md`) is a one-liner stub that invokes a skill with a specific operation and passes `$ARGUMENTS` through.
- The `claptrap-workflow` skill is the single dispatcher; each command tells it which operation to run.
