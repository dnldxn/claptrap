---
name: gh-implement
description: Use when you have a written plan and are ready to execute it in the current workspace.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

Do **NOT** create a new Git Branch or Git Worktree to complete this work. All work stays in the current branch and workspace.

Implement the plan step by step using `subagent-driven-development`. Invoke other skills (frontend-design, systematic-debugging, etc.) as needed. Continue until the plan is fully implemented.

**Log:** Only when you write a file or create/update a GitHub Issue, append one simple line to `.planning/log.md` (create if missing): `- <timestamp> — <action> — <file path or issue URL>`. Get the timestamp with `date '+%Y-%m-%d %H:%M'`. Example action: `File written`, `Issue updated`.

Plan:
$ARGUMENTS
