---
name: openspec-change-proposal
description: Work with OpenSpec change proposals (openspec/changes/*). Draft proposals, validate/show, apply tasks, and archive.
---

# OpenSpec Change Proposals

## What this skill does

This skill identifies when to use OpenSpec and ensures you follow the authoritative instructions in `openspec/AGENTS.md`.

**This skill is a trigger, not a replacement for AGENTS.md.**

## When to activate

Activate this skill when the user wants to:
- Create a change proposal or spec
- Plan a new feature or breaking change
- Apply/implement an OpenSpec change
- Archive a completed change

Trigger phrases (examples):
- "Create a change proposal for..."
- "Help me plan a change"
- "Apply the openspec change"
- "Archive the change"

## Required steps (always follow in order)

### 1. Confirm OpenSpec is initialized
- Check that `openspec/` directory exists
- If not, tell the user to run `openspec init`

### 2. Read the authoritative instructions
**Read `openspec/AGENTS.md` before creating or modifying any OpenSpec files.**

This file contains:
- Exact file formats (proposal.md, tasks.md, spec deltas)
- Scenario syntax (`#### Scenario:` with `- **WHEN**` / `- **THEN**`)
- Requirement wording (SHALL/MUST)
- Change ID naming conventions
- Validation commands and flags
- Common errors and how to fix them

### 3. Follow the AGENTS.md workflow
The AGENTS.md defines a three-stage workflow:
1. **Creating Changes** - Draft proposal, tasks, and spec deltas
2. **Implementing Changes** - Apply tasks sequentially
3. **Archiving Changes** - Move to archive after deployment

Follow those instructions exactly. Do not improvise formats.

## Slash command shortcuts

Some tools expose OpenSpec slash commands. If available, prefer them:
- `/openspec:proposal <description>` or `/openspec-proposal <description>`
- `/openspec:apply <change-id>` or `/openspec-apply <change-id>`
- `/openspec:archive <change-id>` or `/openspec-archive <change-id>`

If slash commands are unavailable, follow the manual steps in `openspec/AGENTS.md`.

## Output behavior

When performing an OpenSpec action:
1. State which operation you're performing (proposal, apply, archive)
2. Reference the specific `<change-id>`
3. If using CLI commands, show them explicitly
4. Run `openspec validate <change-id> --strict --no-interactive` before sharing proposals
5. After archiving, run `openspec validate --all --strict --no-interactive` without asking; do not prompt with a fallback suggestion if the initial validation returns "Nothing to validate."