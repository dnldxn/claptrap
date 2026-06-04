---
name: gh-grill-me
description: Design/spec workflow — start from an idea or existing GitHub Issue, run grill-me, then save as a new or updated GitHub Issue or local spec file.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

**REQUIRED SUB-SKILL:** Use `grill-me` (normal prose, no caveman).

**Input:** If the user provided an issue number/URL, fetch it as context: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`. Otherwise use the user's idea description.

**Interview:** Run `grill-me` seeded with the above context.

**Render:** Fill `assets/spec.template.md` into the final body (use `▼` between sections). Write to a temp file.

**Save:** Use `AskUserQuestion` to ask where to save:
1. Create new GitHub issue → `uv run <path-to-this-skill>/scripts/gh_spec_create.py --title "..." --body-file "$FILE"`
2. Overwrite existing issue *(only if input was an existing issue)* → `gh issue edit <number> --title "..." --body-file "$FILE"`
3. Save to file → write to `.planning/specs/YYYY-MM-DD-<slug>-spec.md`
4. Discard

Run from the target repo root. Use absolute path to `gh_spec_create.py`.

Proposal or Github Issue number/URL:
$ARGUMENTS
