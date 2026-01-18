---
name: propose-change
description: "Create OpenSpec change proposals from designs or user input, validate them, and route through Plan Review."
model: github-copilot/claude-opus-4.5
---

## Overview

Turn a validated design or direct user request into a formal OpenSpec change proposal. The command reads required context, creates `openspec/changes/<change-id>/` with `proposal.md`, `tasks.md`, and spec deltas, then validates the proposal and submits it to Plan Review.

**Inputs:**
- `design-slug`: $ARGUMENTS (design doc location: `.workflow/designs/<design-slug>/design.md`)

If you are unable to find the design doc, ask for help and STOP.  Acknowledge that you have read it before proceeding.

## Skills

Load the following skills:
- `memory`
- `openspec-change-proposal`
- `spawn-subagent`

## Plan Review

Plan Review ALWAYS runs after a proposal is created and validated.

Review criteria:
- Spec alignment
- Feasibility and sequencing
- Completeness and testability
- Risks and edge cases

Outputs MUST be:
- `APPROVED` when ready
- `REVISE` with prioritized feedback when changes are required

**Plan Review subagent prompt template:**
- **Goal**: Review the proposal for alignment, feasibility, completeness, and risks.
- **Inputs**: `proposal.md`, `tasks.md`, spec deltas in `openspec/changes/<change-id>/specs/`
- **Model**: Claude Sonnet 4.5 (via GitHub Copilot)
- **Constraints**: Be critical but pragmatic; avoid nitpicks; propose alternatives only when materially better.
- **Output**: `APPROVED` or `REVISE` with prioritized feedback and suggested fixes.

## Iteration Bounds

- After the initial proposal, perform 2 review cycles.
- A review cycle = Plan Review → respond to findings (apply changes or justify why not).
- Stop after 2 cycles; finalize and note the limit.

## Optional Subagents

Spawn optional subagents when needed:

- **Research**: Use when external documentation is required for a correct proposal.
- **Explore**: Use when codebase context or existing patterns are required.

## Workflow Steps

1. Read memory for project context, decisions, and anti-patterns.
2. Read the input design doc. This is **required**.
3. Read `openspec/AGENTS.md` to follow the exact proposal format.
4. If any instruction is unclear, ask for help and STOP.
5. Create `openspec/changes/<change-id>/` with `proposal.md`, `tasks.md`, and spec deltas.
6. Validate with `openspec validate <change-id> --strict --no-interactive`.
7. Plan Review Pass 1 of 2:
   - Run Plan Review.
   - For each finding, triage: ACCEPT (fix), DEFER (note why), or REJECT (brief rationale + citation).
   - If any ACCEPT items, apply changes and keep `tasks.md` consistent.
8. Plan Review Pass 2 of 2:
   - Repeat Plan Review Pass 1.
   - Stop after this pass; finalize and note the 2-pass limit (even if REVISE persists).
9. Optionally write significant decisions to memory (be selective).
10. STOP. The user triggers `/implement-change` separately.

## Key Principles

- Never guess the OpenSpec format; always read `openspec/AGENTS.md`.
- Validate before Plan Review and re-validate after changes.
- Use bounded iteration to prevent infinite loops.
- End with a clean handoff for implementation.
