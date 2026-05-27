---
name: gh-implement
description: Use when executing an implementation plan from a GitHub Project board, committing directly to main with Closes trailers.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

**REQUIRED SUB-SKILLS:** Use `subagent-driven-development`. On implementation, test, push, or status-update failure, use `systematic-debugging`. Before the final commit, use `requesting-code-review`.

Work from the target repository root so scripts and `gh` commands detect the correct GitHub repo. Use absolute paths to this skill when the target repo does not contain `skills/github-projects/gh-implement/`.

Safe script paths from the target repo root:
- Board state: `uv run <path-to-this-skill>/scripts/gh_state.py`
- Status updates: `uv run <path-to-this-skill>/scripts/gh_status_set.py --issue <number> --status "In progress"`

## Workflow

0. Check board state first with `uv run <path-to-this-skill>/scripts/gh_state.py`. Confirm selected plan(s) with the user before changing status or code. The user may give a spec number or a plan number.
1. Preflight direct-`main` safety before status or code changes: verify `git branch --show-current` is `main`, run `git status --short`, inspect `git diff`, and note any unrelated dirty files that must not be staged. If remote sync matters, run `git fetch` and verify `main` is not behind before committing.
2. Set status. If the parent spec is `Backlog` or `Up Next`, set the spec to `In progress` with `gh_status_set.py`. Set each selected plan to `In progress` before implementing it.
3. Read the plan issue body: `gh issue view <plan-number> --json body --jq .body`. Use `subagent-driven-development` step by step against the plan body.
4. Before the final commit, re-run `git status --short` and `git diff`, stage only files for the implemented plan, and leave unrelated user changes untouched.
5. Commit directly to `main`; do not create branches or PRs. Use this commit format:

   ```text
   <subject>

   <body>

   Closes #<plan>
   Refs #<spec>
   ```

6. After the commit pushes successfully, set the plan to `Done` with `gh_status_set.py`.
7. If all plans for the spec are complete, prompt before closing the spec issue and setting the spec to `Done`.
8. Dispatch modes:
   - Spec number: enumerate sub-issues with `gh api repos/{owner}/{repo}/issues/{spec}/sub_issues --jq '.[].number'`, sort by issue number, and implement all open plans in that order.
   - Plan number: implement that one plan only.
   - Continue: find open plans from board state and ask which to implement.
9. If a command reports missing project scopes, run `gh auth refresh -s project,read:project`, then retry.

## Guardrails

- Never mutate Project status before the user confirms the selected plan(s).
- Never commit unless on `main`, after checking status/diff, and after staging only intended files.
- Never mark a plan `Done` until the commit has pushed successfully.
- Never close the parent spec without explicit user approval.
- If any command fails, stop normal execution and use `systematic-debugging` before retrying.
