#!/usr/bin/env python3
"""Search notebook cell sources (and optionally outputs) for a regex pattern."""
import argparse
import json
import re
import sys

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def join_source(src):
    return "".join(src) if isinstance(src, list) else src


def extract_output_text(output):
    otype = output.get("output_type", "")
    if otype == "stream":
        return join_source(output.get("text", ""))
    if otype == "error":
        return ANSI_RE.sub("", "\n".join(output.get("traceback", [])))
    if otype in ("execute_result", "display_data"):
        data = output.get("data", {})
        for mime in ("text/plain", "text/markdown", "text/html"):
            if mime in data:
                return join_source(data[mime])
    return ""


def search(path, pattern, search_outputs=False, ignore_case=False):
    with open(path) as f:
        nb = json.load(f)

    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(f"Invalid regex: {e}", file=sys.stderr)
        sys.exit(1)

    found = 0
    for i, cell in enumerate(nb.get("cells", [])):
        ct = cell.get("cell_type", "?")
        src = join_source(cell.get("source", ""))

        matches = []
        for line_no, line in enumerate(src.splitlines(), 1):
            if regex.search(line):
                matches.append((line_no, line.rstrip()))

        if matches:
            found += len(matches)
            print(f"Cell {i} [{ct}]:")
            for ln, text in matches:
                print(f"  {ln}: {text}")

        if search_outputs and ct == "code":
            for j, output in enumerate(cell.get("outputs", [])):
                out_text = extract_output_text(output)
                out_matches = []
                for line_no, line in enumerate(out_text.splitlines(), 1):
                    if regex.search(line):
                        out_matches.append((line_no, line.rstrip()))
                if out_matches:
                    found += len(out_matches)
                    print(f"Cell {i} [{ct}] output {j}:")
                    for ln, text in out_matches:
                        print(f"  {ln}: {text}")

    if found == 0:
        print("No matches found.")
    else:
        print(f"\n{found} match{'es' if found != 1 else ''} found.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Search notebook cells for a pattern")
    p.add_argument("notebook")
    p.add_argument("pattern", help="Regex pattern to search for")
    p.add_argument("--outputs", action="store_true", help="Also search cell outputs")
    p.add_argument("-i", "--ignore-case", action="store_true")
    args = p.parse_args()
    search(args.notebook, args.pattern, args.outputs, args.ignore_case)
