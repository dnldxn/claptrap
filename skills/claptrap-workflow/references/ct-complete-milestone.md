# ct-complete-milestone

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug`.
2. Resolve the milestone workspace root using the shared rules in `../SKILL.md`.
3. Read `<workspace-root>/.planning/milestones/M##-slug/MILESTONE_SUMMARY.md` and inspect all phase plan files (`M##-P##-slug-PLAN.md`) in the milestone directory for their Context status.
4. Determine whether the milestone is running in a dedicated worktree by checking whether `<workspace-root>` is `.worktrees/M##-slug/`.
5. Detect the default branch using the shared rules in `../SKILL.md`.
6. If any phase is not `complete`, list the incomplete phases and ask the user whether to archive anyway. Stop if they decline.
7. Update the milestone summary status to `complete` and add the completion date.
8. Run `git mv <workspace-root>/.planning/milestones/M##-slug <workspace-root>/.planning/_archive/YYYY-MM-DD-M##-slug`.
9. Update `<workspace-root>/.planning/ROADMAP.md` to move the milestone to Completed and include the archive date. Leave the git tag field ready to fill once the final tagged commit is known.
10. If the workspace has uncommitted changes, offer to commit all changes in the milestone workspace before any merge step. Recommend `Commit all milestone changes` first.
11. If the user accepts, run `git add .` in the milestone workspace and commit with a milestone completion message.
12. If the milestone uses a dedicated worktree, offer to squash merge branch `feature/M##-slug` back into the default branch (`main` or `master`). Recommend this option.
13. If the user accepts the squash merge:
    - Switch to the default branch outside the milestone worktree.
    - Run a non-interactive squash merge of `feature/M##-slug`.
    - Create the merge commit on the default branch.
    - Tag the merged result `milestone/M##-slug`.
    - Update the ROADMAP completed-milestone entry with git tag `milestone/M##-slug`.
    - Offer to remove `.worktrees/M##-slug/` and delete branch `feature/M##-slug` after the merge succeeds.
14. If the user declines the squash merge, tag the current completion commit `milestone/M##-slug`, update the ROADMAP completed-milestone entry with that git tag, and report that the milestone is complete in the milestone workspace while the branch remains open.
15. If the milestone does not use a dedicated worktree, tag the current completion commit `milestone/M##-slug` and update the ROADMAP completed-milestone entry with that git tag.
16. Report the final archive path and, if applicable, the merge branch, default branch, retained worktree, and git tag.
