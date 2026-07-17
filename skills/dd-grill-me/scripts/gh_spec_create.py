#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Create a spec issue and apply the 'spec' label."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        die(f"{' '.join(cmd)} failed: {stderr}")
    return result.stdout.strip()


def gh(args: list[str]) -> str:
    return run(["gh", *args])


def detect_repo() -> tuple[str, str]:
    url = run(["git", "remote", "get-url", "origin"]).strip()
    patterns = [
        r"git@github\.com:([^/]+)/(.+?)(?:\.git)?",
        r"https://(?:[^/@]+(?::[^/@]*)?@)?github\.com/([^/]+)/(.+?)(?:\.git)?",
    ]
    for pattern in patterns:
        match = re.fullmatch(pattern, url)
        if match:
            return match.group(1), match.group(2)
    die(f"cannot parse GitHub origin remote: {redact_url(url)}")


def redact_url(url: str) -> str:
    return re.sub(r"https://[^/@]+(?::[^/@]*)?@", "https://***@", url)


def parse_issue_number(output: str) -> int:
    match = re.search(r"/issues/(\d+)\b", output)
    if not match:
        match = re.search(r"#(\d+)\b", output)
    if not match:
        die(f"cannot parse issue number from gh issue create output: {output}")
    return int(match.group(1))


def parse_issue_url(output: str) -> str:
    match = re.search(r"https://github\.com/\S+/\S+/issues/\d+", output)
    if not match:
        die(f"cannot parse issue URL from gh issue create output: {output}")
    return match.group(0)


SPEC_LABEL_COLOR = "5319e7"
SPEC_LABEL_DESC = "Spec / design document"


def ensure_spec_label(owner: str, repo: str) -> None:
    """Create or update the 'spec' label matching the gitdash format."""
    result = subprocess.run(
        ["gh", "label", "create", "spec",
         "--color", SPEC_LABEL_COLOR,
         "--description", SPEC_LABEL_DESC,
         "--repo", f"{owner}/{repo}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # Label likely already exists — edit it to match the desired format
        subprocess.run(
            ["gh", "label", "edit", "spec",
             "--color", SPEC_LABEL_COLOR,
             "--description", SPEC_LABEL_DESC,
             "--repo", f"{owner}/{repo}"],
            capture_output=True, text=True, check=True,
        )


def issue_url_for(issue_number: int) -> str:
    url = gh(["issue", "view", str(issue_number), "--json", "url", "--jq", ".url"])
    if not url:
        die(f"cannot determine URL for issue #{issue_number}")
    return url


def configure_spec(issue_number: int) -> None:
    gh(["issue", "edit", str(issue_number), "--add-label", "spec"])


def create_spec(title: str | None, body: str | None, existing_issue: int | None) -> tuple[int, str]:
    owner, repo = detect_repo()
    print(f"Repo: {owner}/{repo}", file=sys.stderr)
    ensure_spec_label(owner, repo)

    if existing_issue is not None:
        issue_number = existing_issue
        issue_url = issue_url_for(issue_number)
        print(f"Resuming: {issue_url}", file=sys.stderr)
    else:
        if title is None or body is None:
            die("--title and --body-file/--body-text are required unless --issue is provided")
        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temp:
                temp.write(body)
                temp_path = temp.name

            created = gh(["issue", "create", "--title", title, "--body-file", temp_path])
        finally:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        issue_number = parse_issue_number(created)
        issue_url = parse_issue_url(created)
        print(f"Created: {issue_url}", file=sys.stderr)

    try:
        configure_spec(issue_number)
    except SystemExit:
        print(f"Recovery: retry with --issue {issue_number} to finish labeling without creating a duplicate.", file=sys.stderr)
        raise
    return issue_number, issue_url


def body_from_args(args: argparse.Namespace) -> str | None:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8")
    return args.body_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title")
    parser.add_argument("--issue", type=int, help="existing issue number to resume after partial failure")
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--body-file")
    body_group.add_argument("--body-text")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    issue_number, issue_url = create_spec(args.title, body_from_args(args), args.issue)
    print(f"issue_number={issue_number}")
    print(f"issue_url={issue_url}")


if __name__ == "__main__":
    main()
