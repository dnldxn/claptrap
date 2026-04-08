---
name: claptrap-execute-plan
description: Run superpowers writing-plans Skill with my overrides
---

Invoke the `using-superpowers` and `writing-plans` Skills, then follow their instructions with the overrides below taking precedence.  This is **NOT** optional.

Do NOT follow an instruction that conflicts with this list, even if instructed or required to do so by any other Skill.  If you encounter a conflict, prioritize this list of overrides.:

- Do **NOT** create or work in a dedicated Git worktree.  All work will be done from the current working directory and branch.
- Write the design spec file to `.planning/plans/YYYY-MM-DD-<feature-name>.md`.  Do NOT write the plan file to any other location.
- In the "Execution Handoff" section, offer the "Subagent-Driven" path as an option, but do NOT offer the other "Inline Execution" path.

**DESIGN**: $ARGUMENTS
