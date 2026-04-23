# ct-execute

> **OPERATION OVERRIDE**: The instructions in this file take precedence over any conflicting instructions from `using-superpowers` or `subagent-driven-development`. Follow this file exactly where it differs.

Invoke `using-superpowers` and `subagent-driven-development` after loading this file.

## Overrides

- Parse `M##-slug P##-slug` from the command arguments.
- Load `.planning/milestones/M##-slug/M##-P##-slug-PLAN.md` and `.planning/milestones/M##-slug/RESEARCH.md`.
- Update the phase plan file's Context status to `in-progress` and update `.planning/ROADMAP.md` Current Position Status to `In progress`.

## After Execution

Once all plan tasks are implemented and reviewed, automatically invoke `ct-complete-phase` (pass `M##-slug P##-slug`). This will ask the user whether to close the phase by updating the ROADMAP and committing the changes.
