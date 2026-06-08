---
name: gh-writing-plans
description: Break a spec into one or more implementation plan files. Input can be a GitHub Issue ID/URL, a spec file path, or a text description. Saves plans to .planning/plans/. Use when the user wants to plan implementation of a spec or feature.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

**REQUIRED SUB-SKILL:** Invoke the `writing-plans` Skill to generate the plan or plans.

**Input:** Determine input mode:
- **GitHub Issue** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`
- **File path** — read the spec file directly
- **Text** — use as-is

**Scope:** Based on spec size and complexity, decide on one plan or multiple. Use multiple plans when work spans distinct subsystems or can be parallelized.

**Output:** Write the plan or plans to: `.planning/plans/YYYY-MM-DD-<order>-<spec-slug>-<plan-slug>.md`

Use a zero-padded order prefix (`01`, `02`, …) for multiple plans; omit it for a single plan. Create `.planning/plans/` if it doesn't exist.

**Log:** Only when you write a file or create/update a GitHub Issue, append one simple line to `.planning/log.md` (create if missing): `- <timestamp> — <action> — <file path or issue URL>`. Get the timestamp with `date '+%Y-%m-%d %H:%M'`. Example action: `Plan written`.

**Input Value:**
$ARGUMENTS
