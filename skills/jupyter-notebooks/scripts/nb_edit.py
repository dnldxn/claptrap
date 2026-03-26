#!/usr/bin/env python3
"""Edit notebook cells: string replacement, insert, delete, clear outputs."""
import argparse
import json
import sys
import uuid


def load(path):
    with open(path) as f:
        return json.load(f)


def save(nb, path):
    with open(path, "w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"Saved: {path}")


def join_source(src):
    return "".join(src) if isinstance(src, list) else src


def split_source(text):
    lines = text.splitlines(True)
    if lines and not lines[-1].endswith("\n"):
        pass
    return lines


def cmd_replace(args):
    nb = load(args.notebook)
    cells = nb["cells"]
    if args.cell < 0 or args.cell >= len(cells):
        print(f"Error: cell {args.cell} out of range (0-{len(cells)-1})", file=sys.stderr)
        sys.exit(1)

    cell = cells[args.cell]
    src = join_source(cell.get("source", ""))
    count = src.count(args.old)
    if count == 0:
        print(f"Error: string not found in cell {args.cell}", file=sys.stderr)
        sys.exit(1)
    if count > 1 and not args.all:
        print(f"Error: {count} occurrences found. Use --all to replace all, or provide a longer unique string.", file=sys.stderr)
        sys.exit(1)

    new_src = src.replace(args.old, args.new) if args.all else src.replace(args.old, args.new, 1)
    cell["source"] = split_source(new_src)
    cell["execution_count"] = None
    save(nb, args.notebook)
    print(f"Replaced {count if args.all else 1} occurrence(s) in cell {args.cell}")


def cmd_insert(args):
    nb = load(args.notebook)
    cells = nb["cells"]
    idx = min(args.at, len(cells))
    new_cell = {
        "cell_type": args.type,
        "source": split_source(args.source),
        "metadata": {},
    }
    if nb.get("nbformat", 4) >= 4 and nb.get("nbformat_minor", 0) >= 5:
        new_cell["id"] = uuid.uuid4().hex[:8]
    if args.type == "code":
        new_cell["execution_count"] = None
        new_cell["outputs"] = []
    cells.insert(idx, new_cell)
    save(nb, args.notebook)
    print(f"Inserted {args.type} cell at index {idx}")


def cmd_delete(args):
    nb = load(args.notebook)
    cells = nb["cells"]
    if args.cell < 0 or args.cell >= len(cells):
        print(f"Error: cell {args.cell} out of range (0-{len(cells)-1})", file=sys.stderr)
        sys.exit(1)
    removed = cells.pop(args.cell)
    save(nb, args.notebook)
    first = join_source(removed.get("source", "")).splitlines()
    preview = (first[0][:60] if first else "empty").strip()
    print(f"Deleted cell {args.cell} ({removed['cell_type']}): {preview}")


def cmd_clear_outputs(args):
    nb = load(args.notebook)
    cleared = 0
    for i, cell in enumerate(nb["cells"]):
        if cell.get("cell_type") == "code":
            if args.cell is not None and i != args.cell:
                continue
            if cell.get("outputs"):
                cell["outputs"] = []
                cell["execution_count"] = None
                cleared += 1
    save(nb, args.notebook)
    print(f"Cleared outputs from {cleared} cell(s)")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Edit notebook cells")
    sub = p.add_subparsers(dest="command", required=True)

    rp = sub.add_parser("replace", help="String replacement in a cell")
    rp.add_argument("notebook")
    rp.add_argument("cell", type=int, help="Cell index")
    rp.add_argument("old", help="String to find")
    rp.add_argument("new", help="Replacement string")
    rp.add_argument("--all", action="store_true", help="Replace all occurrences")

    ip = sub.add_parser("insert", help="Insert a new cell")
    ip.add_argument("notebook")
    ip.add_argument("--at", type=int, required=True, help="Insert position")
    ip.add_argument("--type", choices=["code", "markdown", "raw"], default="code")
    ip.add_argument("--source", default="", help="Cell content")

    dp = sub.add_parser("delete", help="Delete a cell")
    dp.add_argument("notebook")
    dp.add_argument("cell", type=int, help="Cell index to delete")

    cp = sub.add_parser("clear-outputs", help="Clear cell outputs")
    cp.add_argument("notebook")
    cp.add_argument("--cell", type=int, default=None, help="Specific cell (default: all)")

    args = p.parse_args()
    {"replace": cmd_replace, "insert": cmd_insert, "delete": cmd_delete, "clear-outputs": cmd_clear_outputs}[args.command](args)
