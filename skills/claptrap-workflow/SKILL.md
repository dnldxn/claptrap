---
name: "claptrap-workflow"
description: Shared claptrap workflow skill for brainstorm, plan, execute, and completion operations.
---

# Claptrap Workflow

Use this skill as the shared entrypoint for claptrap workflow commands. Identify the requested operation from the invoking command, then load and follow the matching operation file before doing anything else.

## Dispatch

| Operation | Load |
|-----------|------|
| ct-brainstorm | [ct-brainstorm](./operations/ct-brainstorm.md) |
| ct-plan | [ct-plan](./operations/ct-plan.md) |
| ct-execute | [ct-execute](./operations/ct-execute.md) |
| ct-complete-phase | [ct-complete-phase](./operations/ct-complete-phase.md) |
| ct-complete-milestone | [ct-complete-milestone](./operations/ct-complete-milestone.md) |

## Naming Conventions

| Item | Format |
|------|--------|
| Milestone | `M##-slug` |
| Phase | `P##-slug` |
| Branch | `feature/M##-slug-P##-slug` |
| Worktree | `.worktrees/M##-slug/P##-slug/` |
| Tag | `milestone/M##-slug` |

### Slug Rules

- Derive the `slug` from the approved milestone title or phase title, not from a full sentence or the raw user prompt.
- Normalize the title to lowercase ASCII kebab-case: replace spaces and punctuation with hyphens, collapse repeated hyphens, and trim leading or trailing hyphens.
- Keep the slug short and descriptive, usually 2-5 words.
- Once created, treat milestone and phase slugs as stable identifiers and do not rename them casually.
- If a sibling milestone or phase would get the same slug, append a short numeric suffix such as `-2`.

Examples: `Build Search UI` -> `build-search-ui`, `Auth & Roles` -> `auth-roles`.

## Template Loading

Only load a template when creating a new document of that type.

| Doc Type | Template |
|----------|----------|
| `ROADMAP.md` | [ROADMAP template](./templates/ROADMAP.md) |
| Milestone `SUMMARY.md` | [MILESTONE-SUMMARY template](./templates/MILESTONE-SUMMARY.md) |
| Phase `SUMMARY.md` | [PHASE-SUMMARY template](./templates/PHASE-SUMMARY.md) |
| `RESEARCH.md` | [RESEARCH template](./templates/RESEARCH.md) |

## First-Run Init

If `.planning/` does not exist:

```bash
mkdir -p .planning/milestones .planning/_archive
```

Then create `.planning/ROADMAP.md` from the [ROADMAP template](./templates/ROADMAP.md).

## ROADMAP Update Rules

Every operation updates `.planning/ROADMAP.md` before finishing.

| After | What To Update |
|-------|----------------|
| brainstorm | Add milestone to Active Milestones and set Current Position |
| plan | Set Current Position status to `Planning` |
| execute | Set Current Position status to `In Progress` |
| complete-phase | Mark the phase complete and advance Current Position |
| complete-milestone | Move the milestone to Completed and add archive date plus tag |
