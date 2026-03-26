#!/usr/bin/env python3
"""Read notebook cell source and/or outputs with smart MIME selection and truncation."""
import argparse
import json
import re
import sys

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def join_source(src):
    return "".join(src) if isinstance(src, list) else src


def format_output(output, max_lines):
    otype = output.get("output_type", "")
    lines = []

    if otype == "stream":
        text = join_source(output.get("text", ""))
        lines.append(f"  [{output.get('name', 'stdout')}]")
        lines.extend(f"  {l}" for l in text.splitlines())
    elif otype == "error":
        raw = "\n".join(output.get("traceback", []))
        clean = ANSI_RE.sub("", raw)
        lines.append(f"  [error: {output.get('ename', '?')}: {output.get('evalue', '')}]")
        lines.extend(f"  {l}" for l in clean.splitlines())
    elif otype in ("execute_result", "display_data"):
        data = output.get("data", {})
        for mime in ("text/plain", "text/markdown", "text/html"):
            if mime in data:
                text = join_source(data[mime])
                label = mime.split("/")[1]
                lines.append(f"  [{label}]")
                lines.extend(f"  {l}" for l in text.splitlines())
                break
        else:
            mimes = list(data.keys())
            skipped = [m for m in mimes if "/" in m]
            if skipped:
                sizes = []
                for m in skipped:
                    raw = join_source(data[m])
                    sizes.append(f"{m} ({len(raw)} chars)")
                lines.append(f"  [binary output omitted: {', '.join(sizes)}]")

    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines] + [f"  ... truncated ({len(lines) - max_lines} more lines)"]
    return lines


def read_notebook(path, cell_idx=None, show_outputs=False, max_lines=50, cell_type=None):
    with open(path) as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    if cell_idx is not None:
        if cell_idx < 0 or cell_idx >= len(cells):
            print(f"Error: cell {cell_idx} out of range (0-{len(cells)-1})", file=sys.stderr)
            sys.exit(1)
        targets = [(cell_idx, cells[cell_idx])]
    else:
        targets = list(enumerate(cells))

    for i, cell in targets:
        ct = cell.get("cell_type", "?")
        if cell_type and ct != cell_type:
            continue

        src = join_source(cell.get("source", ""))
        ec = cell.get("execution_count")
        header = f"# Cell {i} [{ct}]"
        if ct == "code" and ec is not None:
            header += f" exec={ec}"
        print(header)
        print(src)

        if show_outputs and ct == "code":
            outputs = cell.get("outputs", [])
            if outputs:
                print("# --- outputs ---")
                for out in outputs:
                    for line in format_output(out, max_lines):
                        print(line)
        print()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Read notebook cell source/outputs")
    p.add_argument("notebook")
    p.add_argument("--cell", type=int, default=None, help="Read a specific cell index")
    p.add_argument("--outputs", action="store_true", help="Include cell outputs")
    p.add_argument("--max-output-lines", type=int, default=50, help="Max output lines per cell (0=unlimited)")
    p.add_argument("--type", choices=["code", "markdown", "raw"], help="Filter by cell type")
    args = p.parse_args()
    read_notebook(args.notebook, args.cell, args.outputs, args.max_output_lines or 0, args.type)
