# ct-plan

Invoke the `using-superpowers` and `writing-plans` skills after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Load `.planning/milestones/M##-slug/MILESTONE_SUMMARY.md`, `.planning/milestones/M##-slug/DESIGN.md`, `.planning/milestones/M##-slug/RESEARCH.md`, and `.planning/milestones/M##-slug/phases/P##-slug/PHASE_SUMMARY.md`.
- Write the plan to `.planning/milestones/M##-slug/phases/P##-slug/PLAN.md`.
- Do not create a branch or worktree during planning.
- Before writing the plan, update `.planning/ROADMAP.md` Current Position Status to `Planning`.
- After the plan is written, update the phase summary status to `planned`, update `.planning/ROADMAP.md` Current Position Status to `Ready to execute`, and offer commit `plan: P##-slug`.
