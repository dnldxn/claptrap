# ct-brainstorm

Invoke the `using-superpowers` and `brainstorming` skills after loading this file. Do not invoke `writing-plans` during this operation.

## Overrides

- Do not create a branch or worktree during brainstorming.
- Ignore any visual companion instructions.
- Read `.planning/ROADMAP.md` if it exists to determine the next `M##`; otherwise start at `M01`.
- Generate milestone and phase slugs using the shared slug rules in `../SKILL.md`.
- Write the design doc to `.planning/milestones/M##-slug/DESIGN.md`.
- After the design is approved, create `.planning/milestones/M##-slug/SUMMARY.md` from the [MILESTONE-SUMMARY template](../templates/MILESTONE-SUMMARY.md).
- Create phase summary files at `.planning/milestones/M##-slug/phases/P##-slug/SUMMARY.md` from the [PHASE-SUMMARY template](../templates/PHASE-SUMMARY.md).
- Spawn parallel research subagents for major topics, then synthesize the results into `.planning/milestones/M##-slug/RESEARCH.md` from the [RESEARCH template](../templates/RESEARCH.md).
- Update `.planning/ROADMAP.md` and offer commit `brainstorm: M##-slug`.
