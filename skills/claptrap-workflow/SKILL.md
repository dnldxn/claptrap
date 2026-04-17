---
name: "claptrap-workflow"
description: Shared claptrap workflow skill for brainstorm, plan, execute, and completion operations.
---

# Claptrap Workflow

Use this skill as the shared entrypoint for claptrap workflow commands. Identify the requested operation from the invoking command, then load and follow the matching operation file before doing anything else.

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
| Worktree | `.worktrees/M##-slug/` |
| Tag | `milestone/M##-slug` |

### Slug Rules

- Derive the `slug` from the approved milestone title or phase title, not from a full sentence or the raw user prompt.
- Normalize the title to lowercase ASCII kebab-case: replace spaces and punctuation with hyphens, collapse repeated hyphens, and trim leading or trailing hyphens.
- Keep the slug short and descriptive, usually 2-5 words.
- Once created, treat milestone and phase slugs as stable identifiers and do not rename them casually.
- If a sibling milestone or phase would get the same slug, append a short numeric suffix such as `-2`.

Examples: `Build Search UI` -> `build-search-ui`, `Auth & Roles` -> `auth-roles`.

## Git Workspace Conventions

- During `ct-brainstorm`, offer the user a dedicated milestone branch and worktree before writing milestone documents.
- If accepted, create branch `feature/M##-slug` from the default branch and create worktree `.worktrees/M##-slug/`.
- When a dedicated worktree exists, all planning, execution, and completion work for that milestone happens inside that worktree until the milestone is complete.
- Resolve the milestone workspace root before reading or writing milestone files:
  - If `.worktrees/M##-slug/.planning/milestones/M##-slug/` exists, use `.worktrees/M##-slug/`.
  - Otherwise use the current repository root.
- Detect the default branch from `refs/remotes/origin/HEAD` when available. If that is unavailable, prefer `main`, then `master`.

## Template Loading

Only load a template when creating a new document of that type.

| Doc Type | Template |
|----------|----------|
| `ROADMAP.md` | [ROADMAP template](./assets/ROADMAP.md) |
| Milestone `MILESTONE_SUMMARY.md` | [MILESTONE-SUMMARY template](./assets/MILESTONE-SUMMARY.md) |
| Phase `M##-P##-slug-PLAN.md` | [PHASE-PLAN template](./assets/PHASE-PLAN.md) |
| `RESEARCH.md` | [RESEARCH template](./assets/RESEARCH.md) |

## First-Run Init

If `.planning/` does not exist:

```bash
mkdir -p .planning/milestones .planning/_archive
```

Then create `.planning/ROADMAP.md` from the [ROADMAP template](./assets/ROADMAP.md).

## ROADMAP Update Rules

**Every operation MUST update `.planning/ROADMAP.md` whenever the status changes.**

| After | What To Update |
|-------|----------------|
| brainstorm | Add milestone to Active Milestones; set Current Position Phase to `1 of Y (first-phase-slug)`, Status to `Ready to plan`; reset Progress to `[░░░░░░░░░░] 0%`; update Last Activity |
| plan (start) | Set Current Position Status to `Planning`; update Last Activity |
| plan (complete) | Set Current Position Status to `Ready to execute`; update Last Activity |
| execute | Set Current Position Status to `In progress`; update Last Activity |
| complete-phase | Set Status to `Phase complete`; if more phases remain: advance Current Position to next phase (Phase `X+1 of Y (next-phase-slug)`, Status `Ready to plan`), recalculate Progress bar (filled blocks = floor(completed_phases / total_phases × 10), use `█` for filled and `░` for empty, append percent); if last phase: set Status to `Milestone Complete`, set Progress to `[██████████] 100%`; update Last Activity |
| complete-milestone | Move the milestone to Completed; add archive date and tag; set Progress to `[██████████] 100%`; update Last Activity |
