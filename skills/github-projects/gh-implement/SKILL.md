---
name: gh-implement
description: Use when you have a written plan and are ready to execute it in the current workspace.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

Do **NOT** create a new Git Branch or Git Worktree to complete this work. All work stays in the current branch and workspace.

Implement the plan step by step using `subagent-driven-development`. Invoke other skills (frontend-design, systematic-debugging, etc.) as needed. Continue until the plan is fully implemented.


**Input:** Resolve `$ARGUMENTS` into plan text:
- **Issue number or GitHub URL** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`. Note the issue number for the completion step.
- **File path** — read the file directly.
- **Anything else** — use as-is.

**Plan:**
_(resolved from input above)_

---

**Completion:** After the plan is fully implemented:

1. If the input was a GitHub Issue, use `AskUserQuestion` to ask: _"Close issue #N as complete?"_ — if yes, run `gh issue close <number>`.
2. Use `AskUserQuestion` to ask: _"Commit all changes and push?"_ — if yes, run `git add -A && git commit -m "<inferred or confirmed message>"` then `git push`.
