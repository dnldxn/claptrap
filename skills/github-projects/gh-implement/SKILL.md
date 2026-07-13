---
name: gh-implement
description: Use when you have a written plan and are ready to execute it in the current workspace.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

Do **NOT** create a new Git branch or worktree. All work stays in the current branch and workspace.

**Input:** Resolve `$ARGUMENTS` into plan text:
- **Issue number or GitHub URL** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`. Note the number for the completion step.
- **File path** — read the file directly.
- **Anything else** — use as-is.

**Clarify:** Before writing code, resolve every ambiguity, gap, or undecided detail in the plan by asking the user — keep asking until the work is fully clear. Guessing here compounds into wrong code.

**Implement:** Execute the plan by invoking the `subagent-driven-development` skill. Invoke other skills (frontend-design, systematic-debugging, etc.) as needed. Continue until the plan is fully implemented.

**Review:** Spawn a sub-agent to quickly review the implemented changes, passing it the plan text and the diff (`git diff` / `git status`). Its only goal: confirm the changes match the plan — the plan already contains the code snippets, so it just scans for missing, incomplete, or divergent work. Weigh each finding, then decide per item whether to fix.

**Completion:** Use the `question`, `AskUserQuestion`, `clarify`, `request_user_input`, or equivalent tool to ask:

1. Commit and push? / Commit only? / Skip?
   - Commit: `git add -A && git commit -m "<inferred or confirmed message>"` (then `git push` if pushing).
2. If the input was a GitHub Issue: _"Close issue #N as complete?"_ — if yes, `gh issue close <number>`.

**Input Value:**
$ARGUMENTS
