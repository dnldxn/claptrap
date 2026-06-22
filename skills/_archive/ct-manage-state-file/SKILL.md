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
   Only open a spec or plan file to synthesize a summary when the current state JSON has none for it.

4. Write the patch:
   ```bash
   uv run scripts/state_io.py write --json '<payload>'
   ```

The script handles HTML parsing, schema validation, and rendering.

## JSON structure

```json
{
  "meta": {
    "state": "design | planning | implementation | code review | done | ...",
    "last_action": "3-8 words; include plan/spec filename or branch",
    "last_updated": "YYYY-mm-dd H:M:S",
    "branch": "current git branch"
  },
  "summary": "1-2 sentence status summary",
  "open": [
    {
      "spec": "spec-filename.md",
      "summary": "1-2 sentence spec summary",
      "plans": [
        { "file": "plan-filename.md", "summary": "one sentence", "note": "optional" }
      ]
    }
  ],
  "archived": []
}
```

`archived` uses the same structure as `open`. Partial patches supported — only include fields that changed.

## Grouping rules

- The `state_io.py read` output is authoritative for existing spec → plan linkage. Preserve these mappings unless a workflow event provides an explicit override.
- Resolve plan's parent spec: explicit workflow event → existing mapping from `state_io.py read` output → inferred from filename slug.
- When link is inferred, set `"note": "inferred link"` on that plan entry in the JSON patch.
- Missing parent → group under `Unmapped / Missing Spec`.
- Sort plans by filename order (`01`, `02`, …) then lexicographically.
- Reuse existing summaries from `state_io.py read` output; only open a spec or plan file to synthesize a summary when the current state has none for it.

## If invoked with no context

Only resync file lists, branch, and timestamp. Preserve any existing plan or spec file summaries. Leave `meta.state`, `meta.last_action`, and `summary` unchanged.
