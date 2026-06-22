#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Create a spec issue, add it to Project #2, and set Backlog status."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ID = "PVT_kwHOABcST84BUpee"
STATUS_FIELD_ID = "PVTSSF_lAHOABcST84BUpeezhCFeD8"
BACKLOG_OPTION_ID = "f75ad846"
AUTH_SCOPE_HINT = "gh auth refresh -s project,read:project"


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        if needs_scope_hint(stderr):
            die(f"{' '.join(cmd)} failed: {stderr}\nRun: {AUTH_SCOPE_HINT}")
        die(f"{' '.join(cmd)} failed: {stderr}")
    return result.stdout.strip()


def gh(args: list[str]) -> str:
    return run(["gh", *args])


def needs_scope_hint(message: str) -> bool:
    text = message.lower()
    return "project" in text or "resource not accessible" in text or "scope" in text


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


def graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
    args = ["api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        args.extend(["-F", f"{key}={value}"])
    raw = gh(args)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"gh api graphql returned invalid JSON: {exc}")
    if not isinstance(payload, dict):
        die("gh api graphql returned unexpected JSON shape")
    errors = payload.get("errors")
    if errors:
        rendered = json.dumps(errors)
        if needs_scope_hint(rendered):
            die(f"gh api graphql returned errors: {rendered}\nRun: {AUTH_SCOPE_HINT}")
        die(f"gh api graphql returned errors: {rendered}")
    return payload


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


def preflight_project_access() -> None:
    payload = graphql(
        """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 { id }
          }
        }
        """,
        {"projectId": PROJECT_ID},
    )
    node = payload.get("data", {}).get("node")
    if not isinstance(node, dict) or node.get("id") != PROJECT_ID:
        die(f"cannot access Project #2 before creating issue. Run: {AUTH_SCOPE_HINT}")


def issue_url_for(issue_number: int) -> str:
    url = gh(["issue", "view", str(issue_number), "--json", "url", "--jq", ".url"])
    if not url:
        die(f"cannot determine URL for issue #{issue_number}")
    return url


def configure_spec(issue_number: int) -> None:
    gh(["issue", "edit", str(issue_number), "--add-label", "spec"])
    issue_id = gh(["issue", "view", str(issue_number), "--json", "id", "--jq", ".id"])
    if not issue_id:
        die(f"cannot determine node id for issue #{issue_number}")

    item_id = ensure_project_item(issue_id)
    set_project_status(item_id)


def find_project_item_id(issue_id: str) -> str | None:
    cursor: str | None = None
    query = """
    query($projectId: ID!, $cursor: String) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 50, after: $cursor) {
            nodes {
              id
              content { ... on Issue { id } }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }
    """
    while True:
        variables = {"projectId": PROJECT_ID}
        if cursor:
            variables["cursor"] = cursor
        payload = graphql(query, variables)
        items = payload.get("data", {}).get("node", {}).get("items", {})
        for item in items.get("nodes", []) or []:
            content = item.get("content") if isinstance(item, dict) else None
            if isinstance(content, dict) and content.get("id") == issue_id:
                item_id = item.get("id")
                if isinstance(item_id, str) and item_id:
                    return item_id
        page_info = items.get("pageInfo", {}) if isinstance(items, dict) else {}
        if not page_info.get("hasNextPage"):
            return None
        cursor = page_info.get("endCursor")
        if not isinstance(cursor, str) or not cursor:
            return None


def ensure_project_item(issue_id: str) -> str:
    existing_item_id = find_project_item_id(issue_id)
    if existing_item_id:
        return existing_item_id

    add_payload = graphql(
        """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """,
        {"projectId": PROJECT_ID, "contentId": issue_id},
    )
    item_id = (
        add_payload.get("data", {})
        .get("addProjectV2ItemById", {})
        .get("item", {})
        .get("id")
    )
    if not item_id:
        die("cannot determine Project item id from addProjectV2ItemById response")
    return item_id


def set_project_status(item_id: str) -> None:
    graphql(
        """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId,
            itemId: $itemId,
            fieldId: $fieldId,
            value: {singleSelectOptionId: $optionId}
          }) {
            projectV2Item { id }
          }
        }
        """,
        {
            "projectId": PROJECT_ID,
            "itemId": item_id,
            "fieldId": STATUS_FIELD_ID,
            "optionId": BACKLOG_OPTION_ID,
        },
    )


def create_spec(title: str | None, body: str | None, existing_issue: int | None) -> tuple[int, str]:
    owner, repo = detect_repo()
    print(f"Repo: {owner}/{repo}", file=sys.stderr)
    ensure_spec_label(owner, repo)
    preflight_project_access()

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
        print(f"Recovery: retry with --issue {issue_number} to finish labeling/project/status without creating a duplicate.", file=sys.stderr)
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
