---
name: gh-writing-plans
description: Break a spec into one or more implementation plans. Use when planning implementation of a spec or feature.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

Run scripts from the target repo root so they detect the correct GitHub repo. Use an absolute path to this skill's scripts when the target repo lacks `skills/github-projects/gh-writing-plans/`.

**Input:** Determine input mode:
- **GitHub Issue** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`
- **File path** — read the spec file directly
- **Text** — use as-is

**Scope:** Based on spec size and complexity, decide on one plan or multiple. Use multiple plans when work spans distinct subsystems or can be parallelized.

**Write:** Spawn one sub-agent per plan, in parallel. Give each sub-agent the full spec, the overall design, and the slice of scope it owns — enough context that it can write its plan standalone, without needing to come back for clarification. Each sub-agent invokes the `writing-plans` skill, renders the result into `assets/plan.template.md` (objective, tasks, verification), and saves it to its own temp file. Each sub-agent should ensure its plan is under 65,536 characters (it can be shorter if needed). Wait for every sub-agent to finish, then read each plan file and check it's complete, correctly scoped, and consistent with the others — send any that fall short back for a fix before moving on.

**Save:** Use the `question`, `AskUserQuestion`, `clarify`, `request_user_input`, or equivalent tool to ask where to save the plan or plans:

1. **GitHub sub-issues** — requires a parent spec issue: use the input issue, otherwise ask for its number. Show the board first with `uv run <path-to-this-skill>/scripts/gh_state.py`. Create each sub-issue sequentially to preserve order:
   `uv run <path-to-this-skill>/scripts/gh_plan_create.py --title "..." --body-file "$FILE" --parent <spec>`
   Report each `issue_number=` and `issue_url=`. Only if meaningful new constraints or decisions belong in the spec, update its body with `uv run <path-to-this-skill>/scripts/gh_issue_body.py --issue <spec> --body-file "$FILE"`. Then show the board again with `gh_state.py`.

2. **Files** — write each plan to `.planning/plans/YYYY-MM-DD-<spec-slug>-<order>-<plan-slug>.md`. Use a zero-padded order prefix (`01`, `02`, …) for multiple plans; omit it for a single plan. Create `.planning/plans/` if it doesn't exist.

3. **Implement directly** — invoke the `gh-implement` skill with the plan or plans in the current workspace (no file or issue saved).

**Input Value:**
$ARGUMENTS
