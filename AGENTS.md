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
- `skills/ct-grill-me/` — design/spec workflow wrapper
- `skills/ct-writing-plans/` — implementation-plan workflow wrapper
- `skills/ct-implement/` — plan execution workflow wrapper
- `skills/ct-close-branch/` — branch verification, merge, and cleanup workflow wrapper
- `skills/claptrap-code-conventions/` — language-specific style guidelines (`python.md`, `snowflake.md`)
- `skills/snowflake/` — Snowflake SQL skill with reference docs
- `skills/jupyter-notebooks/` — Jupyter notebook skill with helper scripts
- `skills/_archive/` — deprecated/retired skills kept for reference
- `docs/install/` — provider-specific installation notes (Cursor, Zed, OpenCode)

## Claptrap Workflow

Current workflow:

| Step | Skill | Writes |
| --- | --- | --- |
| Design | `ct-grill-me` | `.planning/specs/YYYY-MM-DD-<topic>-design.md` |
| Plan | `ct-writing-plans` | `.planning/plans/YYYY-MM-DD-<topic>-plan.md` |
| Implement | `ct-implement` | Code/docs on a feature branch in the current workspace |
| Close | `ct-close-branch` | Verified squash merge, optional tag/delete/push |

Branch rules:

- `ct-implement` creates or reuses `feature/<topic>` in the current workspace. It does not create worktrees.
- If the plan specifies `M##-slug`, the branch is `feature/M##-slug`.
- `ct-close-branch` runs verification, asks before squash merge, asks before deleting the branch, and asks before pushing.
- If the branch is `feature/M##-slug`, closeout creates tag `milestone/M##-slug` after approval.

## Skills vs Commands

- A **skill** (`skills/*/SKILL.md`) is loaded by the AI on demand via the `Skill` tool. It contains behavioral instructions.
- A **command** (`commands/*.md`) is a one-liner stub that invokes a skill with a specific operation and passes `$ARGUMENTS` through.
