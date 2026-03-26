---
name: jupyter-notebooks
description: "Token-efficient operations on Jupyter notebooks (.ipynb files). Use whenever the user references a .ipynb file or asks to read, edit, search, analyze, or create notebook cells. Also use when asked to clear outputs, inspect execution order, or prepare notebooks for git. Triggers: any mention of 'notebook', '.ipynb', 'jupyter', 'cell', or requests involving code that lives in notebook format. NEVER read .ipynb files directly — always use the bundled scripts to avoid consuming tokens on raw JSON, base64 outputs, and metadata."
---

# Jupyter Notebook Operations

.ipynb files are large JSON — raw cell source is ~2-5% of the file by token count. The rest is outputs (HTML tables, base64 images, ANSI tracebacks), metadata, and JSON scaffolding. **Always use the scripts below instead of reading/grepping the raw file.**

## Quick Reference

| Task | Command |
|------|---------|
| Overview | `python scripts/nb_summary.py <file>` |
| Read source | `python scripts/nb_read.py <file> [--cell N] [--type code\|markdown]` |
| Read with outputs | `python scripts/nb_read.py <file> --outputs [--max-output-lines 50]` |
| Search source | `python scripts/nb_search.py <file> <pattern> [-i]` |
| Search outputs too | `python scripts/nb_search.py <file> <pattern> --outputs` |
| Replace string | `python scripts/nb_edit.py replace <file> <cell> <old> <new> [--all]` |
| Insert cell | `python scripts/nb_edit.py insert <file> --at N [--type code] --source "..."` |
| Delete cell | `python scripts/nb_edit.py delete <file> <cell>` |
| Clear outputs | `python scripts/nb_edit.py clear-outputs <file> [--cell N]` |

All scripts use only Python stdlib — no pip install needed.

**Cell numbering:** Users see cells as 1-indexed. Scripts use 0-indexed. When the user says "cell 2", use `--cell 1` in the scripts. Always subtract 1.

## Workflow

1. **Start with `nb_summary.py`** to understand the notebook structure, cell count, and execution order
2. **Use `nb_read.py`** to read specific cells — never read the whole raw file
3. **Use `nb_search.py`** instead of grep (grep matches inside JSON arrays and base64, producing false positives)
4. **Use `nb_edit.py`** to modify cells — it handles source array splitting and resets `execution_count`

## Output Reading

`nb_read.py --outputs` performs smart MIME selection per output:

| Output type | What it shows | What it skips |
|-------------|--------------|---------------|
| `stream` (print) | Raw text | Nothing |
| `execute_result` | `text/plain` (ascii table) | `text/html` (bloated), `image/png` (base64) |
| `display_data` | `text/plain` fallback | Binary MIME types with size note |
| `error` | Clean traceback | ANSI escape codes |

MIME priority: `text/plain` > `text/markdown` > `text/html`. Binary outputs report format and size instead of dumping data.

## Execution Model

The JSON captures a *document*, not a running program. Kernel state (variables, imports, connections) exists only in memory.

- **`execution_count`** shows when each cell was last run. Cells are routinely executed out of order — this is normal, not a problem
- **`null` execution count** = never run in current session. Outputs may be from a previous session
- **Stale outputs are common** — source may have been edited after the last run. No indicator exists in the JSON
- **Read error outputs first** before suggesting fixes to cell source

## Editing Rules

- **Never re-run cells unless explicitly asked.** Cells frequently have side effects — API calls, DB writes, long computations
- **Preserve existing outputs** when editing source. Clear only if asked
- **Cell insertion**: reason about what's in scope at the insertion point (imports, variables defined above)
- **`nb_edit.py replace`** resets `execution_count` to `null` on edited cells — this signals the source no longer matches the outputs. Never fabricate counts
- **`nb_edit.py replace`** requires a unique match by default. Use `--all` for global replace, or provide more context for uniqueness

## IPython Syntax

Don't "fix" these as errors — they're valid in notebook cells:

- **Line magics**: `%matplotlib inline`, `%load_ext sql`, `%env VAR=value`, `%time expr`, `%pip install pkg`
- **Cell magics**: `%%sql`, `%%bash`, `%%writefile path`, `%%time`, `%%capture`
- **Shell commands**: `!ls`, `!pip install`, `!wget` — `!` prefix runs shell
- **Auto-display**: bare expression at end of cell auto-displays (no `print()` needed). `display()` shows multiple rich objects in one cell (this is why a single cell can have multiple `display_data` outputs)
- **`_` / `__`**: last / second-to-last cell output

## Structural Conventions

- **Cell 0 is usually imports** — add new imports there, not scattered
- **Config/constants cell** near the top; look for `"tags": ["parameters"]` in metadata (Papermill)
- **Markdown cells** serve as section headers — preserve the narrative flow
- **Scratch cells** at the bottom are often exploratory, not production code

## When to Suggest Leaving Notebooks

- Notebook is mostly function/class definitions with little interactivity — suggest extracting to a `.py` module and importing it
- Notebook exceeds ~50 cells — suggest splitting into multiple notebooks or moving shared code into modules
- Notebook is executed in production (Papermill, `nbconvert --execute`) — evaluate whether a plain script would be more maintainable
