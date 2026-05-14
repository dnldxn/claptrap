# ct-complete-milestone

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug`.
2. Read `.planning/milestones/M##-slug/MILESTONE_SUMMARY.md` and inspect all phase plan files (`M##-P##-slug-PLAN.md`) in the milestone directory for their Context status.
3. Detect the default branch using the shared rules in `../SKILL.md`.
4. If any phase is not `complete`, list the incomplete phases and ask the user whether to finalize anyway. Stop if they decline.
5. Ask the user whether to complete this milestone. If they decline, stop.
6. If the current checkout has uncommitted milestone work outside the completion-doc updates, offer to commit those milestone changes first. Default to milestone-related changes only. Include unrelated changes only if the user explicitly asks. If the user declines, stop.
7. If the current branch is `feature/M##-slug`, ask whether to squash merge now. If the user declines, stop and leave the milestone ready to complete later. If unrelated changes would keep the working tree dirty after any milestone-work commit, stop and ask the user to clean or stash them before finalizing.
8. Update the milestone summary status to `complete` and add the completion date.
9. Run `git mv .planning/milestones/M##-slug .planning/_archive/YYYY-MM-DD-M##-slug`.
10. Update `.planning/ROADMAP.md` to move the milestone to Completed, include the archive date, and record the planned git tag name `milestone/M##-slug`. If another active milestone remains, set Current Position from the most recently updated remaining active-milestone row; otherwise keep the completed milestone in Current Position, set Phase to `-`, and set Current Position Status to `Milestone complete`.
11. Stage only the workflow completion changes (`.planning/ROADMAP.md` and `.planning/_archive/YYYY-MM-DD-M##-slug/`) and commit `docs: M##-slug complete`.
12. Determine if the current branch is a feature branch (`feature/M##-slug`):
    - **If on a feature branch**: switch to the default branch, run a non-interactive squash merge, create the merge commit, tag the result `milestone/M##-slug`, then offer to delete branch `feature/M##-slug`.
    - **If on the default branch**: tag the current milestone completion commit `milestone/M##-slug`.
13. Report the final archive path, the git tag, and (if applicable) the merge details.
