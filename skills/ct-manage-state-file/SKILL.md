---
name: ct-manage-state-file
description: Use when a Claptrap workflow needs to update or resync `.planning/state.md` after spec, plan, implementation, review, merge, or archive changes.
---

Update .planning/state.md to reflect the current workflow state. Describe, in natural language, what just happened in the workflow. Infer the values for the template below from what just happened in the workflow. Use these guidelines:

- Which workflow state the project is now in.  Examples: `design`, `planning`, `implementation`, `code review`, `done`, etc.
- A short phrase describing what just happened, ideally with a filename or branch.  Examples: `wrote spec 2026-05-14-foo-spec.md`, `wrote plan 2026-05-14-foo-01-bar.md`, `started branch feature/foo`, `finished plan 2026-05-14-foo-01-bar.md`, `merged branch feature/foo`, etc.
- 1-2 sentence summary of the current situation.

If invoked manually with no context, only resync the file lists, branch, and timestamp; leave the existing state, last action, and summary unchanged.

## Update Procedure

1. If `.planning/state.md` is missing, create it from the template below. Ensure `.planning/state.md` is listed in the project root `.gitignore`.
2. Fill out the "State", "Last action", "Last updated", and "Branch" fields based on the most recent workflow event.
3. Rebuild file sections from disk:
   - Open specs: `.planning/specs/*.md`
   - Open plans: `.planning/plans/*.md`
   - Archived specs: `.planning/_archive/specs/*.md`
   - Archived plans: `.planning/_archive/plans/*.md`
4. For each listed file, use its title/header line (usually H1) plus first paragraph to write one sentence. If no H1 title, use the filename slug. Drop references to missing files; do not add deleted markers.

## state.md Template

```markdown

- **State:** <design | planning | implementation | code review | done | etc>
- **Last action:** <3-8 words; include filename or branch where relevant>
- **Last updated:** <ISO 8601 timestamp>
- **Branch:** <current git branch>

## Summary

<1-2 sentences describing the current situation.>

## Open

### Specs
- `<filename>` — <one-sentence summary>

### Plans
- `<filename>` — <one-sentence summary>

## Archived

### Specs
- `<filename>` — <one-sentence summary>

### Plans
- `<filename>` — <one-sentence summary>
```
