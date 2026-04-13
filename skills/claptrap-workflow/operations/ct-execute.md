# ct-execute

> **OPERATION OVERRIDE**: The instructions in this file take precedence over any conflicting instructions from `using-superpowers`, `subagent-driven-development`, or `using-git-worktrees`. Follow this file exactly where it differs.

Invoke `using-superpowers`, `subagent-driven-development`, and `using-git-worktrees` after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Load `.planning/milestones/M##-slug/phases/P##-slug/PLAN.md` and `.planning/milestones/M##-slug/RESEARCH.md`.
- Create worktree `.worktrees/M##-slug/P##-slug/` on branch `feature/M##-slug-P##-slug`.
- In Step 3, present `Squash and Merge into main` as option `1` and mark it recommended.
- Update the phase summary status to `in-progress` and update `.planning/ROADMAP.md`.
