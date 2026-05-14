# ct-complete-phase

This operation is standalone. Do not invoke additional Superpowers workflow skills, except for the final-phase handoff to `ct-complete-milestone` described below.

## Steps

1. Parse arguments into `M##-slug` and `P##-slug`.
2. Ask the user whether to close this phase. If they decline, stop.
3. Update `.planning/milestones/M##-slug/M##-P##-slug-PLAN.md` Context status to `complete`.
4. Update `.planning/ROADMAP.md`:
   - Set Current Position Status to `Phase complete`.
   - If more phases remain: advance Current Position to next phase (Phase `P##-next-phase-slug (X+1 of Y)`, Status `Ready to plan`); recalculate Progress bar (filled blocks = floor(completed_phases / total_phases × 10), use `█` for filled and `░` for empty, append percent); update Last Activity.
   - If this was the last phase: set Status to `Ready to complete milestone`; set Progress to `[██████████] 100%`; update Last Activity.
5. Offer commit `docs: P##-slug complete`.
6. If this was the last phase and the phase-close commit is created, automatically invoke `ct-complete-milestone` (pass `M##-slug`).
7. If this was the last phase and the phase-close commit is not created, remind the user to run `claptrap-complete-milestone M##-slug` after committing the phase-close changes.
8. If more phases remain, report the remaining phases and remind the user to re-read the updated `ROADMAP.md` and then run `claptrap-plan M##-slug P##-next-phase-slug` for the next phase.
