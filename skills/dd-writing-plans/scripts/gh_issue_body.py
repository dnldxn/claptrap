#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Replace a GitHub issue body and optionally add a timeline comment."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str], *, fail: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if fail and result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        die(f"{' '.join(cmd)} failed: {stderr}")
    return result


def write_temp_body(body: str) -> str:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temp:
        temp.write(body)
        return temp.name


def body_path_from_args(args: argparse.Namespace) -> tuple[str, bool]:
    if args.body_file:
        path = Path(args.body_file)
        if not path.exists():
            die(f"body file does not exist: {path}")
        return str(path), False
    return write_temp_body(args.body_text), True


def replace_issue_body(issue: str, body_path: str) -> None:
    run(["gh", "issue", "edit", issue, "--body-file", body_path])


def add_comment(issue: str, comment: str) -> None:
    result = run(["gh", "issue", "comment", issue, "--body", comment], fail=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        die(f"body updated, but gh issue comment failed: {stderr}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", required=True)
    body_group = parser.add_mutually_exclusive_group(required=True)
    body_group.add_argument("--body-file")
    body_group.add_argument("--body-text")
    parser.add_argument("--comment", help="optional comment added after body edit succeeds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    body_path, delete_body = body_path_from_args(args)
    try:
        replace_issue_body(args.issue, body_path)
        if args.comment:
            add_comment(args.issue, args.comment)
    finally:
        if delete_body:
            try:
                os.unlink(body_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()
