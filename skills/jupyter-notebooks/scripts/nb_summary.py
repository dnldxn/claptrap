#!/usr/bin/env python3
"""Quick overview of a Jupyter notebook: cell types, line counts, first lines, execution order."""
import json
import sys


def summarize(path):
    with open(path) as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    if not cells:
        print("Empty notebook (no cells)")
        return

    kernel = nb.get("metadata", {}).get("kernelspec", {}).get("display_name", "unknown")
    print(f"Kernel: {kernel}  |  Cells: {len(cells)}  |  Format: v{nb.get('nbformat', '?')}")
    print()

    exec_counts = []
    for i, cell in enumerate(cells):
        ct = cell.get("cell_type", "?")
        src_lines = cell.get("source", [])
        if isinstance(src_lines, str):
            src_lines = src_lines.splitlines(True)
        n_lines = len(src_lines)
        first = (src_lines[0].rstrip("\n") if src_lines else "").strip()
        if len(first) > 80:
            first = first[:77] + "..."

        ec = cell.get("execution_count")
        n_outputs = len(cell.get("outputs", []))

        if ct == "code":
            ec_str = f"[{ec}]" if ec is not None else "[_]"
            out_str = f"  ({n_outputs} output{'s' if n_outputs != 1 else ''})" if n_outputs else ""
            print(f"  {i:>3}  {ct:<8} {ec_str:<6} {n_lines:>3}L{out_str}  {first}")
            if ec is not None:
                exec_counts.append((ec, i))
        else:
            print(f"  {i:>3}  {ct:<8}        {n_lines:>3}L  {first}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: nb_summary.py <notebook.ipynb>")
        sys.exit(1)
    summarize(sys.argv[1])
