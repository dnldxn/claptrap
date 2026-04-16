# ct-complete-phase

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug` and `P##-slug`.
2. Squash-merge `feature/M##-slug-P##-slug` into `main`; stop and report if conflicts occur.
3. Run `git worktree remove .worktrees/M##-slug/P##-slug/ --force`.
4. Update `.planning/milestones/M##-slug/phases/P##-slug/PHASE_SUMMARY.md` status to `complete`.
5. Update `.planning/ROADMAP.md`:
   - Set Current Position Status to `Phase complete`.
   - If more phases remain: advance Current Position to next phase (Phase `X+1 of Y (next-phase-slug)`, Status `Ready to plan`); recalculate Progress bar (filled blocks = floor(completed_phases / total_phases × 10), use `█` for filled and `░` for empty, append percent); update Last Activity.
   - If this was the last phase: set Status to `Milestone Complete`; set Progress to `[██████████] 100%`; update Last Activity.
6. Run `git add .planning/ && git commit -m "docs: P##-slug complete"`.
7. Report any remaining phases in the milestone.
