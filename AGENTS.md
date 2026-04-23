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
- `skills/claptrap-workflow/assets/` — Markdown templates for planning documents (`ROADMAP.md`, `MILESTONE-SUMMARY.md`, `PHASE-PLAN.md`, etc.)
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

Milestone/phase IDs use zero-padded numbers (`M01`, `P02`) with a kebab-case slug derived from the title. When a dedicated git branch is created during brainstorming, branches are named `feature/M##-slug`.

### Git Branch Lifecycle

Branches and commits are scoped to the **milestone**, never to individual phases. The lifecycle spans the five workflow steps:

| Step | Branch | Commit Offered |
| --- | --- | --- |
| `ct-brainstorm` | Asks the user whether to create a feature branch. If yes: create and checkout `feature/M##-slug` from the default branch. If no: stay on the current branch. | `brainstorm: M##-slug` |
| `ct-plan` | No new branch. Planning happens on the current branch. | `plan: P##-slug` |
| `ct-execute` | No new branch. Code and doc changes happen on the current branch. Execution commits are made by the `subagent-driven-development` skill as the plan progresses. | (per plan task) |
| `ct-complete-phase` | Auto-invoked by `ct-execute` after work is done. If this was the last phase and the phase-close commit is created, auto-invokes `ct-complete-milestone`. | `docs: P##-slug complete` |
| `ct-complete-milestone` | If on a feature branch, offers a **squash merge** of `feature/M##-slug` into the default branch, then tags the result `milestone/M##-slug`, then offers to delete `feature/M##-slug`. If on the default branch, tags the current commit in place. | milestone completion commit + squash merge commit |

All file paths are relative to the project root. There is no workspace resolution step.

### `claptrap-next` skill

The **`claptrap-next`** skill is a router for target projects that use `.planning/ROADMAP.md`. Invoke it when you need to **determine the next claptrap step** from the current ROADMAP (including after idle time or handoff), instead of guessing which of brainstorm / plan / execute / complete-phase / complete-milestone applies.

**Behavior (summary):**

1. Read `.planning/ROADMAP.md` if it exists. If the file is missing, check for local milestone branches matching `feature/M##-*`; only treat the workflow as **not started** when neither the ROADMAP nor milestone feature branches exist.
2. Parse **Current Position**: `Milestone:` (`M##-slug`), `Phase:` (`P##-slug (X of Y)`), `Status:`.
3. If `Status` is **In progress**, run `git status` to distinguish **dirty** (keep executing) vs **clean** (ready to complete the phase).
4. Offer **1–3** next actions ordered by recommendation; after selection, direct the user to the matching claptrap command with **fresh** slugs from the ROADMAP.

**Command dispatch:**

| Situation | Run |
| --- | --- |
| New milestone | `claptrap-brainstorm` |
| Early completion path | `claptrap-complete-milestone M##-slug` |
| Plan or resume planning a phase | `claptrap-plan M##-slug P##-slug` |
| Execute or resume execution | `claptrap-execute-plan M##-slug P##-slug` |
| Complete current phase | `claptrap-complete-phase M##-slug P##-slug` |
| Complete milestone or archive | `claptrap-complete-milestone M##-slug` |

**Important:** After `ct-complete-phase`, re-read the ROADMAP. For non-final phases, the **Phase** field advances automatically; for the last phase, the status moves to milestone completion instead. Do not assume the next `P##-slug` without reading it.

## Skills vs Commands

- A **skill** (`skills/*/SKILL.md`) is loaded by the AI on demand via the `Skill` tool. It contains behavioral instructions.
- A **command** (`commands/*.md`) is a one-liner stub that invokes a skill with a specific operation and passes `$ARGUMENTS` through.
- The `claptrap-workflow` skill is the single dispatcher; each command tells it which operation to run.
