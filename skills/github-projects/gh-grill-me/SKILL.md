---
name: gh-grill-me
description: Design/spec workflow — start from an idea or existing GitHub Issue, run grill-me, then save as a new or updated GitHub Issue or local spec file.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

**Input:**: If the user provided an issue number/URL, fetch it as context: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`. Otherwise use the user's idea description.

**Interview:**: Invoke the `grill-me` and `brainstorming` skills seeded with the context below.  Use the `question`, `AskUserQuestion`, `clarify`, `request_user_input`, or equivalent tool to interview the user, one question at a time (pause in between each question). After the `grill-me` and `brainstorming` skills reach shared understanding and are satisfied the requirements are clear, proceed to generate the design/spec.

**Render:**: Fill `assets/spec.template.md` into the final body (use `▼` between sections). Write to a temp file.

**Save:** Use the same question tool discovered above to ask where to save:
1. Create new GitHub issue → `uv run <path-to-this-skill>/scripts/gh_spec_create.py --title "..." --body-file "$FILE"`
2. Overwrite existing issue *(only if input was an existing issue)* → `gh issue edit <number> --title "..." --body-file "$FILE"`
3. Save to file → write to `.planning/specs/YYYY-MM-DD-<slug>-spec.md`

Run from the target repo root. Use absolute path to `gh_spec_create.py`.


**Input Value:**
$ARGUMENTS
