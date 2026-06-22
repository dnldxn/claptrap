---
name: gh-writing-plans
description: Break a spec into one or more implementation plans. Input can be a GitHub Issue ID/URL, a spec file path, or a text description. Offers to save plans as GitHub sub-issues, as files in .planning/plans/, or implement them directly. Use when planning implementation of a spec or feature.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

**REQUIRED SUB-SKILL:** Invoke the `writing-plans` Skill to generate the plan or plans.

Run scripts from the target repo root so they detect the correct GitHub repo. Use an absolute path to this skill's scripts when the target repo lacks `skills/github-projects/gh-writing-plans/`.

**Input:** Determine input mode:
- **GitHub Issue** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`
- **File path** — read the spec file directly
- **Text** — use as-is

**Scope:** Based on spec size and complexity, decide on one plan or multiple. Use multiple plans when work spans distinct subsystems or can be parallelized.

**Write:** Use `writing-plans` to break the spec into bite-sized plans. Render each plan into `assets/plan.template.md` (objective, tasks, verification) and save to a temp file.

**Save:** Use `AskUserQuestion` to ask where to save the plan or plans:

1. **GitHub sub-issues** — requires a parent spec issue: use the input issue, otherwise ask for its number. Show the board first with `uv run <path-to-this-skill>/scripts/gh_state.py`. Create each sub-issue sequentially to preserve order:
   `uv run <path-to-this-skill>/scripts/gh_plan_create.py --title "..." --body-file "$FILE" --parent <spec>`
   Report each `issue_number=` and `issue_url=`. Only if meaningful new constraints or decisions belong in the spec, update its body with `uv run <path-to-this-skill>/scripts/gh_issue_body.py --issue <spec> --body-file "$FILE"`. Then show the board again with `gh_state.py`.

2. **Files** — write each plan to `.planning/plans/YYYY-MM-DD-<spec-slug>-<order>-<plan-slug>.md`. Use a zero-padded order prefix (`01`, `02`, …) for multiple plans; omit it for a single plan. Create `.planning/plans/` if it doesn't exist.

3. **Implement directly** — invoke the `gh-implement` Skill with the plan or plans in the current workspace (no file or issue saved).

**Input Value:**
$ARGUMENTS
