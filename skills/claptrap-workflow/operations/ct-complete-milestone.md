# ct-complete-milestone

This operation is standalone. Do not invoke additional Superpowers workflow skills.

## Steps

1. Parse arguments into `M##-slug`.
2. Read `.planning/milestones/M##-slug/SUMMARY.md` and inspect all phase statuses.
3. If any phase is not `complete`, list the incomplete phases and ask the user whether to archive anyway. Stop if they decline.
4. Update the milestone summary status to `complete` and add the completion date.
5. Update `.planning/ROADMAP.md` to move the milestone to Completed.
6. Run `git add .planning/ && git commit -m "docs: M##-slug complete"`.
7. Run `git mv .planning/milestones/M##-slug .planning/_archive/YYYY-MM-DD-M##-slug`.
8. Run `git tag milestone/M##-slug`.
9. Update `.planning/ROADMAP.md` with the archive date and git tag, then run `git add .planning/ && git commit -m "archive: M##-slug"`.
10. Report `Milestone M##-slug archived to .planning/_archive/YYYY-MM-DD-M##-slug. Tagged milestone/M##-slug.`
