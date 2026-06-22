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

1. Use `AskUserQuestion` to ask: _"Commit all changes and push?"_ — if yes, run `git add -A && git commit -m "<inferred or confirmed message>"` then `git push`.

2. If the input was a GitHub Issue, use `AskUserQuestion` to ask: _"Close issue #N as complete?"_ — if yes, run `gh issue close <number>`. Then check for a parent via `gh issue view <number> --json parent`. If the issue has a parent, list the parent's sub-issue states with `gh issue view <parent_number> --json subIssuesSummary --jq '.subIssuesSummary'` — if all sub-issues are closed (percent == 100), use `AskUserQuestion` to ask: _"All sub-issues of #{parent} are closed. Close parent #{parent} too?"_ — if yes, run `gh issue close <parent_number>`.  If the user answered no to closing, check for a parent anyway (skip the close, still offer to close the parent if all its sub-issues are closed).
