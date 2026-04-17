# ct-complete-phase

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug` and `P##-slug`.
2. Resolve the milestone workspace root using the shared rules in `../SKILL.md`.
3. Update `<workspace-root>/.planning/milestones/M##-slug/phases/P##-slug/PHASE_SUMMARY.md` status to `complete`.
4. Update `<workspace-root>/.planning/ROADMAP.md`:
   - Set Current Position Status to `Phase complete`.
   - If more phases remain: advance Current Position to next phase (Phase `X+1 of Y (next-phase-slug)`, Status `Ready to plan`); recalculate Progress bar (filled blocks = floor(completed_phases / total_phases × 10), use `█` for filled and `░` for empty, append percent); update Last Activity.
   - If this was the last phase: set Status to `Milestone Complete`; set Progress to `[██████████] 100%`; update Last Activity.
5. Do not merge branches or remove the milestone worktree here. Final commit and squash merge happen at milestone completion.
6. Offer commit `docs: P##-slug complete` in the resolved milestone workspace.
7. Report any remaining phases in the milestone and remind the user to continue working in the same milestone workspace.
