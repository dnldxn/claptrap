# ct-execute

> **OPERATION OVERRIDE**: The instructions in this file take precedence over any conflicting instructions from `using-superpowers` or `subagent-driven-development`. Follow this file exactly where it differs.

Invoke `using-superpowers` and `subagent-driven-development` after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Resolve the milestone workspace root using the shared rules in `../SKILL.md` before loading any files or making code changes.
- Load `<workspace-root>/.planning/milestones/M##-slug/M##-P##-slug-PLAN.md` and `<workspace-root>/.planning/milestones/M##-slug/RESEARCH.md`.
- Execute the phase inside the resolved milestone workspace. If `.worktrees/M##-slug/` exists for the milestone, all code and document changes happen there.
- Do not create a per-phase branch or worktree during execution.
- Update the phase plan file's Context status to `in-progress` and update `<workspace-root>/.planning/ROADMAP.md` Current Position Status to `In progress`.
