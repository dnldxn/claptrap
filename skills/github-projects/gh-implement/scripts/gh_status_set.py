#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Set the Status field for an issue on GitHub Project #2."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


PROJECT_ID = "PVT_kwHOABcST84BUpee"
STATUS_FIELD_ID = "PVTSSF_lAHOABcST84BUpeezhCFeD8"
STATUS_OPTIONS = {
    "Backlog": "f75ad846",
    "Up Next": "19adf077",
    "In progress": "47fc9ee4",
    "Done": "98236657",
}


AUTH_SCOPE_HINT = "If this is an auth scope issue, run: gh auth refresh -s project,read:project"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def append_auth_hint(message: str) -> str:
    lowered = message.lower()
    scope_markers = (
        "project",
        "scope",
        "resource not accessible",
        "requires authentication",
        "permission",
        "forbidden",
    )
    if any(marker in lowered for marker in scope_markers):
        return f"{message}\n{AUTH_SCOPE_HINT}"
    return message


def gh_json(cmd: list[str], context: str) -> Any:
    result = run(cmd)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        die(append_auth_hint(f"{context} failed: {detail}"))
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        die(f"{context} returned invalid JSON: {exc}")


def issue_node_id(issue: int) -> str:
    result = run(["gh", "issue", "view", str(issue), "--json", "id", "--jq", ".id"])
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        die(append_auth_hint(f"gh issue view #{issue} failed: {detail}"))
    node_id = result.stdout.strip()
    if not node_id:
        die(f"gh issue view #{issue} returned an empty issue node ID")
    return node_id


def graphql(query: str, variables: dict[str, str | None], context: str) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is None:
            continue
        cmd.extend(["-f", f"{key}={value}"])

    payload = gh_json(cmd, context)
    if not isinstance(payload, dict):
        die(f"{context} returned unexpected JSON shape")

    errors = payload.get("errors")
    if errors:
        die(append_auth_hint(f"{context} returned GraphQL errors: {json.dumps(errors)}"))
    return payload


def find_project_item_id(issue: int, node_id: str) -> str:
    query = """
    query($project: ID!, $cursor: String) {
      node(id: $project) {
        ... on ProjectV2 {
          items(first: 50, after: $cursor) {
            nodes {
              id
              content {
                ... on Issue {
                  id
                  number
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
    """
    cursor: str | None = None
    while True:
        payload = graphql(
            query,
            {"project": PROJECT_ID, "cursor": cursor},
            "Project item lookup",
        )
        node = payload.get("data", {}).get("node")
        if not isinstance(node, dict):
            die(append_auth_hint("Project item lookup failed: project node not found"))

        items = node.get("items")
        if not isinstance(items, dict):
            die(append_auth_hint("Project item lookup failed: ProjectV2 items not found"))

        nodes = items.get("nodes") or []
        if not isinstance(nodes, list):
            die("Project item lookup failed: ProjectV2 items nodes were not a list")

        for item in nodes:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, dict):
                continue
            if content.get("id") == node_id:
                item_id = item.get("id")
                if isinstance(item_id, str) and item_id:
                    return item_id

        page_info = items.get("pageInfo")
        if not isinstance(page_info, dict) or not page_info.get("hasNextPage"):
            break
        next_cursor = page_info.get("endCursor")
        if not isinstance(next_cursor, str) or not next_cursor:
            break
        cursor = next_cursor

    die(f"Issue #{issue} is not on Project #2")


def update_status(item_id: str, status: str) -> None:
    option_id = STATUS_OPTIONS[status]
    mutation = """
    mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $project,
        itemId: $item,
        fieldId: $field,
        value: { singleSelectOptionId: $option }
      }) {
        projectV2Item {
          id
        }
      }
    }
    """
    graphql(
        mutation,
        {
            "project": PROJECT_ID,
            "item": item_id,
            "field": STATUS_FIELD_ID,
            "option": option_id,
        },
        "Project status update",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", required=True, type=int, help="GitHub issue number on Project #2")
    parser.add_argument(
        "--status",
        required=True,
        help=f"target Status value: {', '.join(sorted(STATUS_OPTIONS))}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.status not in STATUS_OPTIONS:
        die(f"Unknown status {args.status!r}. Expected one of: {', '.join(sorted(STATUS_OPTIONS))}")
    node_id = issue_node_id(args.issue)
    item_id = find_project_item_id(args.issue, node_id)
    update_status(item_id, args.status)
    print(f"#{args.issue} -> {args.status}", file=sys.stderr)


if __name__ == "__main__":
    main()
