---
name: "claptrap-workflow"
description: Use when running claptrap workflow commands or resuming a project that tracks milestone state in .planning/ROADMAP.md.
---

# Claptrap Workflow

Use this skill as the shared entrypoint for claptrap workflow commands. Identify the requested operation from the invoking command, then load and follow the matching operation file before doing anything else.

If resuming after an interruption or handoff, use `claptrap-next` to choose the next step instead of guessing from memory.

## Dispatch

| Operation | Load |
|-----------|------|
| ct-brainstorm | [ct-brainstorm](./references/ct-brainstorm.md) |
| ct-plan | [ct-plan](./references/ct-plan.md) |
| ct-execute | [ct-execute](./references/ct-execute.md) |
| ct-complete-phase | [ct-complete-phase](./references/ct-complete-phase.md) |
| ct-complete-milestone | [ct-complete-milestone](./references/ct-complete-milestone.md) |

## Naming Conventions

| Item | Format |
|------|--------|
| Milestone | `M##-slug` |
| Phase | `P##-slug` |
| Branch | `feature/M##-slug` |
| Tag | `milestone/M##-slug` |

### Slug Rules

- Derive the `slug` from the approved milestone title or phase title, not from a full sentence or the raw user prompt.
- Normalize the title to lowercase ASCII kebab-case: replace spaces and punctuation with hyphens, collapse repeated hyphens, and trim leading or trailing hyphens.
- Keep the slug short and descriptive, usually 2-5 words.
- Once created, treat milestone and phase slugs as stable identifiers and do not rename them casually.
- If a sibling milestone or phase would get the same slug, append a short numeric suffix such as `-2`.

Examples: `Build Search UI` -> `build-search-ui`, `Auth & Roles` -> `auth-roles`.

## Git Branch Conventions

- During `ct-brainstorm`, before writing milestone documents, offer the user the choice to create and checkout a feature branch `feature/M##-slug` or stay on the current branch.
- If a feature branch is created, all subsequent planning, execution, and completion work for the milestone happens on that branch at the project root.
- Detect the default branch from `refs/remotes/origin/HEAD` when available. If that is unavailable, prefer `main`, then `master`.
- All file paths are relative to the project root (e.g., `.planning/milestones/M##-slug/`). There is no workspace resolution step.

## Template Loading

Only load a template when creating a new document of that type.

| Doc Type | Template |
|----------|----------|
| `DESIGN.md` | No template. Draft directly during `ct-brainstorm`. |
| `ROADMAP.md` | [ROADMAP template](./assets/ROADMAP.md) |
| Milestone `MILESTONE_SUMMARY.md` | [MILESTONE-SUMMARY template](./assets/MILESTONE-SUMMARY.md) |
| Phase `M##-P##-slug-PLAN.md` | [PHASE-PLAN template](./assets/PHASE-PLAN.md) |
| `RESEARCH.md` | [RESEARCH template](./assets/RESEARCH.md) |

## First-Run Init

If `.planning/` does not exist, initialize it inside the checkout already chosen for the current milestone. During `ct-brainstorm`, make the branch decision first, then initialize `.planning/` there:

```bash
mkdir -p .planning/milestones .planning/_archive
```

Then create `.planning/ROADMAP.md` from the [ROADMAP template](./assets/ROADMAP.md).

## State Glossary

- `ROADMAP.md` tracks workflow state for the current milestone: `Not Started`, `Ready to plan`, `Planning`, `Ready to execute`, `In progress`, `Phase complete`, `Ready to complete milestone`, `Milestone complete`.
- The Current Position phase line stores the canonical phase ID first, then its ordinal: `P##-slug (X of Y)`.
- Each phase plan file tracks only that phase's local status in `## Context`: `proposed`, `planned`, `in-progress`, `complete`.
- `MILESTONE_SUMMARY.md` tracks milestone-level status such as `proposed` and `complete`.

## ROADMAP Update Rules

**Every operation MUST update `.planning/ROADMAP.md` whenever the status changes.**

| After | What To Update |
|-------|----------------|
| brainstorm | Add milestone to Active Milestones; set Current Position Phase to `P01-first-phase-slug (1 of Y)`, Status to `Ready to plan`; reset Progress to `[░░░░░░░░░░] 0%`; update Last Activity |
| plan (start) | Set Current Position Status to `Planning`; update Last Activity |
| plan (complete) | Set Current Position Status to `Ready to execute`; update Last Activity |
| execute | Set Current Position Status to `In progress`; update Last Activity |
| complete-phase | Set Status to `Phase complete`; if more phases remain: advance Current Position to next phase (Phase `P##-next-phase-slug (X+1 of Y)`, Status `Ready to plan`), recalculate Progress bar (filled blocks = floor(completed_phases / total_phases × 10), use `█` for filled and `░` for empty, append percent); if last phase: set Status to `Ready to complete milestone`, set Progress to `[██████████] 100%`; update Last Activity |
| complete-milestone | Move the milestone to Completed; add archive date and tag; set Progress to `[██████████] 100%`; if another active milestone remains, set Current Position from that row; otherwise keep the completed milestone in Current Position, set Phase to `-`, set Current Position Status to `Milestone complete`; update Last Activity |
