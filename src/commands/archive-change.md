---
name: archive-change
description: "Archive a completed OpenSpec change, validate specs, and capture lessons learned."
---

# Archiving OpenSpec Changes

<!-- Model: Gemini 3 Flash or Claude Haiku 4.5 (via GitHub Copilot) -->

## Overview

Archive a completed OpenSpec change, update the living specs, and record lessons learned. This is a lightweight operation and MUST NOT spawn subagents.

Input:
- `change-id` referencing the completed proposal under `openspec/changes/<change-id>/`

Outputs:
- Archived change under `openspec/changes/archive/`
- Updated specs (unless `--skip-specs` is used)
- Lessons learned entry written to memory

## Task Completion

- Read `openspec/changes/<change-id>/tasks.md`.
- Mark any remaining tasks as complete.
- Manual verification tasks SHOULD already be verified by the user before archiving; do not re-verify here.

## Skills

Load the following skills:
- `memory`
- `openspec-change-proposal`

## Archive Execution

- Archive the OpenSpec change proposal.
- Pass `--skip-specs` for tooling-only changes.
- If the archive operation fails, report the error and STOP.

## Post-Archive Validation

- Run strict validation on the archived specs.
- If the response is "Nothing to validate", treat it as success.

## Design Status Update

- If `designs/<change-id>/design.md` exists for the change, update its Status to "Implemented".
- Add a link to the archived change in the design document.

## Workflow Steps

1. Read `tasks.md` and mark any open tasks complete.
2. Archive the OpenSpec change proposal (pass `--skip-specs` if provided).
3. Run post-archive validation.
4. Optionally write lessons learned to memory (be selective).
5. Update design doc status if applicable.
6. STOP.

## Flags

`--skip-specs`: Pass through when archiving tooling-only changes.

Example:
- `/openspec-archive add-linting --skip-specs`
