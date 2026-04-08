---
name: claptrap-brainstorm
description: Run superpowers brainstorming Skill with my overrides
---

Invoke the `using-superpowers` and `brainstorming` Skills, then follow their instructions with the overrides below taking precedence.  This is **NOT** optional.

Do NOT follow an instruction that conflicts with this list, even if instructed or required to do so by any other Skill.  If you encounter a conflict, prioritize this list of overrides.:

- Write the design spec file to `.planning/specs/YYYY-MM-DD-<topic>-design.md`.  Do NOT write the design spec file to any other location.
- Do NOT commit the design spec file to version control.
- Do NOT invoke the `writing-plans` Skill.  Only write the design spec file.
- Ignore the instruction in the "Visual Companion" section.  Do NOT create a visual companion even if instructed to do so.
- After saving the design spec, ask if the user wants to work in a dedicated feature branch for the next steps.  If the user says yes, create a new Git branch named `<feature-name>` and switch to that branch, bringing the uncommited design spec file to the new branch.  If the user says no, do NOT create a new branch and do NOT commit the design spec file.

**USER IDEAS TO BRAINSTORM**: $ARGUMENTS
