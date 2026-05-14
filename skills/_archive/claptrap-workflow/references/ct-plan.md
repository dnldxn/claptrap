# ct-plan

Invoke the `using-superpowers` and `writing-plans` skills after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Load `.planning/milestones/M##-slug/MILESTONE_SUMMARY.md`, `.planning/milestones/M##-slug/DESIGN.md`, `.planning/milestones/M##-slug/RESEARCH.md`, and `.planning/milestones/M##-slug/M##-P##-slug-PLAN.md`.
- The phase plan file already contains summary sections (Context through Definition of Done) written during brainstorming. Preserve these sections exactly as they are.
- After loading the planning documents, if anything about the scope, approach, or requirements feels ambiguous or underspecified, consider asking the user for clarification before writing the plan.
- When writing the plan, append the plan content below the `---` separator in the phase plan file, replacing the placeholder comment. The summary sections remain at the top, followed by the separator, followed by the full plan produced by the `writing-plans` skill.
- Before writing the plan, update `.planning/ROADMAP.md` Current Position Status to `Planning`.
- After the plan is written, update the phase plan file's Context status to `planned`, update `.planning/ROADMAP.md` Current Position Status to `Ready to execute`, and offer commit `plan: P##-slug`.
