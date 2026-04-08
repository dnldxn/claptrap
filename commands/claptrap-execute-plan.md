---
name: claptrap-execute-plan
description: Run superpowers executing-plans Skill with my overrides
---

Invoke the `using-superpowers` and `executing-plans` Skills, then follow their instructions with the overrides below taking precedence.  This is **NOT** optional.

Do NOT follow an instruction that conflicts with this list, even if instructed or required to do so by any other Skill.  If you encounter a conflict, prioritize this list of overrides.:

- Do NOT load the workflow skill `superpowers:using-git-worktree`
- Do **NOT** create or work in a dedicated Git worktree.  All work will be done from the current working directory and branch.

**PLAN**: $ARGUMENTS
