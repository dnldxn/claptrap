---
name: gh-grill-me
description: Use when starting a new design/spec that should be saved as a GitHub Issue on the Project board after user approval.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

**REQUIRED SUB-SKILL:** Use `grill-me` (normal prose, no caveman).

After the `grill-me` interview reaches shared understanding:
1. Render `assets/spec.template.md` into a body (use `▼` between sections).
2. Ask the user whether to save. If they decline, stop. If they approve, write the rendered Markdown to a secure temporary file and run from the target repo root:
   `uv run <path-to-this-skill>/scripts/gh_spec_create.py --title "..." --body-file "$SPEC_BODY_FILE"`
3. Report created issue number and URL.

Keep the current working directory at the target repository root so the script can detect the correct GitHub repo. Use the absolute path to this skill's `scripts/gh_spec_create.py` when the repo does not contain `skills/github-projects/gh-grill-me/`.

If gh_spec_create.py reports missing gh auth scopes, tell user:
`gh auth refresh -s project,read:project`
Then retry.

To see current board state at any time:
`uv run <path-to-this-skill>/scripts/gh_state.py`
