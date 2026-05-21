---
name: ct-manage-state-file
description: Use when a Claptrap workflow needs to update or resync `.planning/state.html` after spec, plan, implementation, review, merge, or archive changes.
---

Update `.planning/state.html` through the bundled script. Never read or write it directly.

## Available scripts

- **`scripts/state_io.py`** — reads/writes structured state JSON embedded in the HTML file

## Workflow

1. Read current state:
   ```bash
   uv run scripts/state_io.py read
   ```

2. List filenames from disk (do not open files):
   ```bash
   ls .planning/specs/*.md .planning/plans/*.md \
      .planning/_archive/specs/*.md .planning/_archive/plans/*.md 2>/dev/null
   ```

3. Build a JSON patch combining workflow context and disk file lists (apply grouping rules below).
   Only open a spec or plan file if `state.html` has no existing summary for it yet.

4. Write the patch:
   ```bash
   uv run scripts/state_io.py write --json '<payload>'
   ```

The script handles HTML parsing, schema validation, and rendering.

## Fields

- `meta.state`: workflow phase (`design`, `planning`, `implementation`, `code review`, `done`, etc.)
- `meta.last_action`: 3-8 words; include plan/spec filename or branch when relevant
- `meta.last_updated`: `YYYY-mm-dd H:M:S`
- `meta.branch`: current git branch
- `summary`: 1-2 sentence status summary
- `open` / `archived`: grouped spec rows with ordered plan lists

## Grouping rules

- `.planning/state.html` is authoritative for spec → plan linkage.
- Resolve plan's parent spec: explicit workflow event → existing state mapping → inferred from filename slug.
- When link is inferred, mark it in the plan's `note` field (e.g. `"inferred link"`).
- Missing parent → group under `Unmapped / Missing Spec`.
- Sort plans by filename order (`01`, `02`, …) then lexicographically.
- Reuse existing summaries; only open a file to synthesize a summary when `state.html` has none for it.

## If invoked with no context

Only resync file lists, branch, and timestamp. Leave `meta.state`, `meta.last_action`, and `summary` unchanged.
