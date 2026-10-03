---
name: dd-writing-plans
description: Break a spec into one or more implementation plans. Use when planning implementation of a spec or feature.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

Run scripts from the target repo root so they detect the correct GitHub repo. Use an absolute path to this skill's scripts when the target repo lacks `skills/github-projects/gh-writing-plans/`.

**Input:** Determine input mode:
- **GitHub Issue** — fetch: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`
- **File path** — read the spec file directly
- **Text** — use as-is

**Clarify:** Before scoping, resolve every ambiguity, gap, or undecided detail in the spec by asking the user — keep asking until the work is fully clear and well-defined. Guessing here compounds into flawed plans.

**Scope:** Default to one plan; split only when separate plans materially improve execution. Before delegating, the main agent must review the breakdown for a simpler way to meet all spec goals, merging unnecessary splits.

**Write:** Spawn one sub-agent per plan, in parallel. Give each sub-agent the full spec, the overall design, and the slice of scope it owns — enough context that it can write its plan standalone, without needing to come back for clarification. Each sub-agent invokes the `writing-plans` skill, renders the result into `assets/plan.template.md` (objective, tasks, verification), and saves it to its own temp file. Before returning, each planner must remove over-engineering and simplify wordy or complex language while preserving required work and verification. Keep plans under 65,536 characters; this is a ceiling, not a target. Wait for every sub-agent to finish, then read each plan file and check it's complete, correctly scoped, simple, concise, and consistent with the others — send any that fall short back for a fix before moving on.

**Save:** Use the `question`, `AskUserQuestion`, `clarify`, `request_user_input`, or equivalent tool to ask where to save the plan or plans:

1. **GitHub sub-issues** — requires a parent spec issue: use the input issue, otherwise ask for its number. Create each sub-issue sequentially to preserve order:
   `uv run <path-to-this-skill>/scripts/gh_plan_create.py --title "..." --body-file "$FILE" --parent <spec>`
   Report each `issue_number=` and `issue_url=`. Only if meaningful new constraints or decisions belong in the spec, update its body with `uv run <path-to-this-skill>/scripts/gh_issue_body.py --issue <spec> --body-file "$FILE"`.

2. **Files** — write each plan to `.planning/plans/YYYY-MM-DD-<spec-slug>-<order>-<plan-slug>.md`. Use a zero-padded order prefix (`01`, `02`, …) for multiple plans; omit it for a single plan. Create `.planning/plans/` if it doesn't exist.

3. **Implement directly** — invoke the `gh-implement` skill with the plan or plans in the current workspace (no file or issue saved).

**Input Value:**
$ARGUMENTS
