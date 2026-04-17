# ct-plan

Invoke the `using-superpowers` and `writing-plans` skills after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Resolve the milestone workspace root using the shared rules in `../SKILL.md` before loading any files.
- Load `<workspace-root>/.planning/milestones/M##-slug/MILESTONE_SUMMARY.md`, `<workspace-root>/.planning/milestones/M##-slug/DESIGN.md`, `<workspace-root>/.planning/milestones/M##-slug/RESEARCH.md`, and `<workspace-root>/.planning/milestones/M##-slug/M##-P##-slug-PLAN.md`.
- The phase plan file already contains summary sections (Context through Definition of Done) written during brainstorming. Preserve these sections exactly as they are.
- When writing the plan, append the plan content below the `---` separator in the phase plan file, replacing the placeholder comment. The summary sections remain at the top, followed by the separator, followed by the full plan produced by the `writing-plans` skill.
- Do not create another branch or worktree during planning. Continue in the resolved milestone workspace.
- Before writing the plan, update `<workspace-root>/.planning/ROADMAP.md` Current Position Status to `Planning`.
- After the plan is written, update the phase plan file's Context status to `planned`, update `<workspace-root>/.planning/ROADMAP.md` Current Position Status to `Ready to execute`, and offer commit `plan: P##-slug` in the resolved workspace.
