# ct-complete-phase

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug` and `P##-slug`.
2. Squash-merge `feature/M##-slug-P##-slug` into `main`; stop and report if conflicts occur.
3. Run `git worktree remove .worktrees/M##-slug/P##-slug/ --force`.
4. Update `.planning/milestones/M##-slug/phases/P##-slug/SUMMARY.md` status to `complete`.
5. Update `.planning/ROADMAP.md` to advance Current Position to the next pending phase, or `Milestone Complete` if this was the last phase.
6. Run `git add .planning/ && git commit -m "docs: P##-slug complete"`.
7. Report any remaining phases in the milestone.
