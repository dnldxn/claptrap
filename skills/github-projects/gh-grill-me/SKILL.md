---
name: gh-grill-me
description: Design/spec workflow — start from an idea or existing GitHub Issue, run grill-me, then save as a new or updated GitHub Issue or local spec file.
---

> **OPERATION OVERRIDE**: Instructions here override all other Skills.

**REQUIRED SUB-SKILL:** Use `grill-me` (normal prose, no caveman).

**Input:**: If the user provided an issue number/URL, fetch it as context: `gh issue view <number> --json title,body --jq '"# " + .title + "\n\n" + .body'`. Otherwise use the user's idea description.

**Interview:**: Run `grill-me` seeded with the context below.  After the `grill-me` reaches shared understanding, invoke the `brainstorming` Skill to finalize any remaining open questions.

**Render:**: Fill `assets/spec.template.md` into the final body (use `▼` between sections). Write to a temp file.

**Save:** Use `AskUserQuestion` to ask where to save:
1. Create new GitHub issue → `uv run <path-to-this-skill>/scripts/gh_spec_create.py --title "..." --body-file "$FILE"`
2. Overwrite existing issue *(only if input was an existing issue)* → `gh issue edit <number> --title "..." --body-file "$FILE"`
3. Save to file → write to `.planning/specs/YYYY-MM-DD-<slug>-spec.md`

Run from the target repo root. Use absolute path to `gh_spec_create.py`.

**Log:** Only when you write a design, spec, or plan file (in the `.planning/` directory) or create/update a GitHub Issue, append one simple line to `.planning/log.md` (create if missing): `- <timestamp> — <action> — <file path or issue URL>`. Get the timestamp with `date '+%Y-%m-%d %H:%M'`. Example action: `Spec written`, `Spec issue created`, `Spec issue updated`.

**Input Value:**
$ARGUMENTS
