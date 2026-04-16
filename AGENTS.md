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
- `skills/claptrap-workflow/assets/` — Markdown templates for planning documents (`ROADMAP.md`, `MILESTONE_SUMMARY.md`, `PHASE_SUMMARY.md`, etc.)
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
      phases/
        P##-slug/
          PHASE_SUMMARY.md
          PLAN.md
  _archive/
```

Milestone/phase IDs use zero-padded numbers (`M01`, `P02`) with a kebab-case slug derived from the title. Branches are named `feature/M##-slug-P##-slug`; worktrees go to `.worktrees/M##-slug/P##-slug/`.

## Skills vs Commands

- A **skill** (`skills/*/SKILL.md`) is loaded by the AI on demand via the `Skill` tool. It contains behavioral instructions.
- A **command** (`commands/*.md`) is a one-liner stub that invokes a skill with a specific operation and passes `$ARGUMENTS` through.
- The `claptrap-workflow` skill is the single dispatcher; each command tells it which operation to run.
