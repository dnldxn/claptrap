# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A personal AI agent configuration toolkit ("claptrap") — a collection of skills, commands, and workflow templates that are installed as symlinks into AI coding assistants (Claude Code, Cursor, OpenCode).

## Installation

```bash
python bootstrap/install.py
```

The installer is stdlib-only and installs the OpenCode continuous-learning system from `opencode/claptrap-plugin/`. It creates guarded symlinks for the Claptrap instructions, plugin, agents, commands, and managed skills. It also sweeps stale symlinks that resolve into this repository and warns about the two manual `opencode.json` registrations.

Manual setup steps are documented in `README.md`, including the `skill-gardener` model entry.

## Repository Structure

- `bootstrap/install.py` — stdlib-only OpenCode installer
- `opencode/claptrap-plugin/` — Claptrap plugin (`plugin.ts`, `logic.ts`), instructions, `agents/`, `commands/`, `skills/`, and `tests/`
- `skills/ct-grill-me/` — design/spec workflow wrapper
- `skills/ct-writing-plans/` — implementation-plan workflow wrapper
- `skills/ct-implement/` — plan execution workflow wrapper
- `skills/ct-close-branch/` — branch verification, merge, and cleanup workflow wrapper
- `skills/claptrap-code-conventions/` — language-specific style guidelines (`python.md`, `snowflake.md`)
- `skills/snowflake/` — Snowflake SQL skill with reference docs
- `skills/dagu/` — Dagu workflow orchestration, DAG YAML, REST API, MCP, and run-debugging reference
- `skills/jupyter-notebooks/` — Jupyter notebook skill with helper scripts
- `skills/_archive/` — deprecated/retired skills kept for reference
- `docs/install/` — provider-specific installation notes (Cursor, Zed, OpenCode)

## Claptrap Workflow

Current workflow:

| Step | Skill | Writes |
| --- | --- | --- |
| Design | `ct-grill-me` | `.planning/specs/YYYY-MM-DD-<topic>-spec.md` |
| Plan | `ct-writing-plans` | `.planning/plans/YYYY-MM-DD-<spec-slug>-<order>-<plan-slug>.md` |
| Implement | `ct-implement` | Code/docs on a feature branch in the current workspace |
| Close | `ct-close-branch` | Verified squash merge, optional tag/delete/push |

## Skills vs Commands

- A **skill** (`skills/*/SKILL.md`) is loaded by the AI on demand via the `Skill` tool. It contains behavioral instructions.
- A **command** (`commands/*.md`) is a one-liner stub that invokes a skill with a specific operation and passes `$ARGUMENTS` through.
