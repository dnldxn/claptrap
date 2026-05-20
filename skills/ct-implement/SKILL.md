---
name: ct-implement
description: Use when you have a written plan and are ready to execute it in the current workspace.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

## Overrides

- Create a new Git Branch to complete this work, but do **NOT** create a Git Worktree.  All work stays in the current workspace.
- After creating the branch, invoke `ct-manage-state-file` to record that the workflow is now in the implementation state and note the branch name.
- When implementation is complete and ready for review, invoke `ct-manage-state-file` to record that the workflow plan is now implemented and note which plan was finished.

Use the following Skills to implement the plan below. Announce newly loaded skills before starting. Then implement the plan step by step using `subagent-driven-development`. Invoke other skills (frontend-design, systematic-debugging, etc.) as needed. Continue until the plan is fully implemented.

**REQUIRED SUB-SKILLS:** Use `using-superpowers`, `context-management`, `token-efficiency`, `subagent-driven-development`, and `ct-manage-state-file`.

Plan:
$ARGUMENTS
