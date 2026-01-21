---
name: implement-change
description: "Implement an approved OpenSpec change with bounded review iteration."
model: openai/gpt-5.2-codex
---

## Overview

Implement an approved OpenSpec change using `tasks.md` as the source of truth. Deliver minimal, correct code changes that follow existing patterns, then run a bounded Code Review cycle to validate correctness, safety, and plan alignment.

**Inputs:**
- `change-id`: $ARGUMENTS (the approved proposal under `openspec/changes/<change-id>/`)

**Outputs:**
- Code changes implementing the proposal
- Updated `openspec/changes/<change-id>/tasks.md` checkboxes

## Skills

Load the following skills:
- `memory`
- `openspec`
- `spawn-subagent`

## Required Reading

- Read the approved proposal under `openspec/changes/<change-id>/`. This is **required**.
- Read the implementation checklist under `openspec/changes/<change-id>/tasks.md`. This is **required**.
- Read the spec deltas in `openspec/changes/<change-id>/specs/` for requirements and scenarios.

## Core Principles

- **Task-by-task delivery**: complete one task at a time.
- **Minimal change**: avoid refactors unless required to meet the task.
- **External-boundary errors only**: handle failures at I/O or user-input boundaries.
- **Clarity over cleverness**: keep code simple and readable.
- **Consistency**: mirror existing patterns for naming, structure, and flow.

## Rules

- Follow the project code conventions for the language you edit.
- Do not expand scope or fix unrelated issues.
- Ask brief clarifying questions when requirements are unclear.
- Avoid new dependencies unless required to meet the task.
- Prefer existing helpers and patterns before introducing new abstractions.
- If a task reveals a gap in requirements, pause and ask for clarification.
- Keep edits small, focused, and easy to review.

## Task Implementation

- Implement tasks sequentially, in the exact order listed.
- Check off tasks in `tasks.md` as they are completed.
- Skip manual verification tasks (leave unchecked).
- Keep diffs focused and reviewable; avoid unrelated refactors.

## Code Review

Code Review ALWAYS runs after implementation.

Review criteria:
- Correctness
- Safety
- Maintainability
- Alignment with the proposal and tasks

Outputs MUST be:
- `APPROVED` when ready
- `REVISE` with prioritized findings when changes are required

**Code Review subagent prompt template:**
- **Goal**: Review the implementation for correctness, safety, maintainability, and plan alignment.
- **Inputs**: Code changes, `proposal.md`, `tasks.md`, spec deltas in `openspec/changes/<change-id>/specs/`
- **Model**: Claude Sonnet 4.5 (via GitHub Copilot)
- **Constraints**: Focus on meaningful risks; avoid nitpicks; propose fixes when needed.
- **Output**: `APPROVED` or `REVISE` with prioritized findings and suggested fixes.

## Iteration Bounds

- After the initial implementation, perform 2 review cycles.
- A review cycle = Code Review → respond to findings (apply changes or justify why not).
- Stop after 2 cycles; finalize and note the limit.

## Optional Subagents

Spawn optional subagents when needed:

- **Research**: Use when external documentation or best practices are required.
- **Explore**: Use when codebase context or existing patterns are required.

## Workflow Steps

1. Read `proposal.md`, `design.md` (if exists), `tasks.md`, and spec deltas.
2. Read memory for relevant context.
3. Investigate the relevant code and confirm intent before editing.
4. Implement tasks sequentially, checking off completed items.
5. Spawn Code Review with changes and proposal context.
6. Code Review Pass 1 of 2:
   - Run Code Review.
   - For each finding, triage: ACCEPT (fix), DEFER (note why), or REJECT (brief rationale + citation).
   - If any ACCEPT items, apply changes and keep `tasks.md` consistent.
7. Code Review Pass 2 of 2:
   - Repeat Code Review Pass 1.
   - Stop after this pass; finalize and note the 2-pass limit (even if REVISE persists).
8. Mark all automated tasks complete (skip manual verification tasks).
9. Optionally write lessons to memory (be selective).  Ask yourself:
   - Did we make a non-obvious decision that should be documented?
   - Did we encounter a tricky edge case that should be remembered for future development?
   - Did something unexpected happen that should be noted for future reference?
   - Did we learn anything that could improve future development?
10. STOP. The user triggers `/archive-change` separately.

## Key Principles

- Follow `tasks.md` order exactly.
- Keep changes focused on the approved scope.
- Bounded iteration prevents infinite review loops.
- Clean handoff: implementation stops before archiving.
