---
name: openspec
description: Work with OpenSpec change proposals (openspec/changes/*). Draft proposals, validate/show, apply tasks, and archive.
---

# OpenSpec

## What this skill does

This skill activates when working with OpenSpec change proposals and ensures agents follow the authoritative instructions.

## When to activate

- Creating a change proposal or spec
- Planning a new feature or breaking change
- Applying/implementing an OpenSpec change
- Archiving a completed change

## Required: Read the authoritative instructions

**Before any OpenSpec work, you MUST read `openspec/AGENTS.md`.**

If you cannot read `openspec/AGENTS.md`, STOP and ask the user for help. Do not proceed without it.

The `openspec/AGENTS.md` file contains the complete workflow, file formats, validation commands, and error resolution. Follow it exactly.

## Quick reference reminders

**Naming**: Use `kebab-case` for change IDs (e.g., `add-user-auth`, `fix-login-bug`).

**Date prefix**: Added automatically during archiving (e.g., `2026-01-17-add-user-auth`). New proposals use the base name only.

**Validation**: Run `openspec validate <change-id> --strict --no-interactive` before sharing proposals.

## Slash command shortcuts

If available, prefer these:
- `/openspec:proposal <description>` or `/openspec-proposal <description>`
- `/openspec:apply <change-id>` or `/openspec-apply <change-id>`
- `/openspec:archive <change-id>` or `/openspec-archive <change-id>`
