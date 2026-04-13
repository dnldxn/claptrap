# ct-plan

Invoke the `using-superpowers` and `writing-plans` skills after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Load `.planning/milestones/M##-slug/SUMMARY.md`, `.planning/milestones/M##-slug/DESIGN.md`, `.planning/milestones/M##-slug/RESEARCH.md`, and `.planning/milestones/M##-slug/phases/P##-slug/SUMMARY.md`.
- Write the plan to `.planning/milestones/M##-slug/phases/P##-slug/PLAN.md`.
- Do not create a branch or worktree during planning.
- Update the phase summary status to `planned`, update `.planning/ROADMAP.md`, and offer commit `plan: P##-slug`.
