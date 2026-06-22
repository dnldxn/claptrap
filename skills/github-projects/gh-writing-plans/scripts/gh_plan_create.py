#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Create a plan issue, link it under a spec, and add it to Project #2."""

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


def needs_scope_hint(message: str) -> bool:
    text = message.lower()
    return "project" in text or "resource not accessible" in text or "scope" in text


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


def detect_repo() -> tuple[str, str]:
    url = run(["git", "remote", "get-url", "origin"])
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


def parse_parent(value: str, owner: str, repo: str) -> int:
    text = value.strip()
    if text.startswith("#"):
        text = text[1:]
    if text.isdigit():
        return int(text)

    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)", text)
    if not match:
        die(f"cannot parse parent issue: {value}")
    url_owner, url_repo, number = match.groups()
    if (url_owner, url_repo) != (owner, repo):
        die(f"parent issue repo {url_owner}/{url_repo} does not match detected repo {owner}/{repo}")
    return int(number)


def parse_issue_number(output: str) -> int:
    match = re.search(r"/issues/(\d+)\b", output) or re.search(r"#(\d+)\b", output)
    if not match:
        die(f"cannot parse issue number from gh issue create output: {output}")
    return int(match.group(1))


def parse_issue_url(output: str) -> str:
    match = re.search(r"https://github\.com/\S+/\S+/issues/\d+", output)
    if not match:
        die(f"cannot parse issue URL from gh issue create output: {output}")
    return match.group(0)


def issue_url_for(issue_number: int) -> str:
    url = gh(["issue", "view", str(issue_number), "--json", "url", "--jq", ".url"])
    if not url:
        die(f"cannot determine URL for issue #{issue_number}")
    return url


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


PLAN_LABEL_COLOR = "1d76db"
PLAN_LABEL_DESC = "Implementation plan"


def ensure_plan_label(owner: str, repo: str) -> None:
    """Create or update the 'plan' label matching the gitdash format."""
    result = subprocess.run(
        ["gh", "label", "create", "plan",
         "--color", PLAN_LABEL_COLOR,
         "--description", PLAN_LABEL_DESC,
         "--repo", f"{owner}/{repo}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        # Label likely already exists — edit it to match the desired format
        subprocess.run(
            ["gh", "label", "edit", "plan",
             "--color", PLAN_LABEL_COLOR,
             "--description", PLAN_LABEL_DESC,
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


def get_issue_node_id(issue_number: int) -> str:
    issue_id = gh(["issue", "view", str(issue_number), "--json", "id", "--jq", ".id"])
    if not issue_id:
        die(f"cannot determine node id for issue #{issue_number}")
    return issue_id


def ensure_parent_issue_exists(parent_number: int) -> None:
    get_issue_node_id(parent_number)


def get_issue_database_id(owner: str, repo: str, issue_number: int) -> str:
    database_id = gh(["api", f"/repos/{owner}/{repo}/issues/{issue_number}", "--jq", ".id"])
    if not database_id:
        die(f"cannot determine REST database id for issue #{issue_number}")
    return database_id


def add_to_project(issue_node_id: str) -> None:
    item_id = ensure_project_item(issue_node_id)
    set_project_status(item_id)


def find_project_item_id(issue_node_id: str) -> str | None:
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
            if isinstance(content, dict) and content.get("id") == issue_node_id:
                item_id = item.get("id")
                if isinstance(item_id, str) and item_id:
                    return item_id
        page_info = items.get("pageInfo", {}) if isinstance(items, dict) else {}
        if not page_info.get("hasNextPage"):
            return None
        cursor = page_info.get("endCursor")
        if not isinstance(cursor, str) or not cursor:
            return None


def ensure_project_item(issue_node_id: str) -> str:
    existing_item_id = find_project_item_id(issue_node_id)
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
        {"projectId": PROJECT_ID, "contentId": issue_node_id},
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


def is_sub_issue(owner: str, repo: str, parent_number: int, issue_number: int) -> bool:
    result = subprocess.run(
        ["gh", "api", f"/repos/{owner}/{repo}/issues/{parent_number}/sub_issues", "--jq", ".[ ].number".replace(" ", "")],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return False
    return str(issue_number) in result.stdout.splitlines()


def ensure_sub_issue(owner: str, repo: str, parent_number: int, issue_number: int, sub_issue_id: str) -> None:
    if is_sub_issue(owner, repo, parent_number, issue_number):
        return
    result = subprocess.run(
        [
            "gh",
            "api",
            "--method",
            "POST",
            f"/repos/{owner}/{repo}/issues/{parent_number}/sub_issues",
            "-F",
            f"sub_issue_id={sub_issue_id}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0 or is_sub_issue(owner, repo, parent_number, issue_number):
        return
    stderr = result.stderr.strip() or result.stdout.strip()
    die(f"sub-issue link failed: {stderr}")


def create_plan(title: str | None, body: str | None, parent: str, existing_issue: int | None) -> tuple[int, str]:
    owner, repo = detect_repo()
    parent_number = parse_parent(parent, owner, repo)
    print(f"Repo: {owner}/{repo}", file=sys.stderr)
    print(f"Parent spec: #{parent_number}", file=sys.stderr)
    ensure_plan_label(owner, repo)
    preflight_project_access()
    ensure_parent_issue_exists(parent_number)

    if existing_issue is not None:
        issue_number = existing_issue
        issue_url = issue_url_for(issue_number)
        print(f"Resuming: {issue_url}", file=sys.stderr)
    else:
        if title is None or body is None:
            die("--title and --body-file/--body-text are required unless --issue is provided")
        if not Path(body).exists():
            die(f"body file does not exist: {body}")
        created = gh(["issue", "create", "--title", title, "--body-file", body])
        issue_number = parse_issue_number(created)
        issue_url = parse_issue_url(created)
        print(f"Created: {issue_url}", file=sys.stderr)

    try:
        gh(["issue", "edit", str(issue_number), "--add-label", "plan"])
        issue_node_id = get_issue_node_id(issue_number)
        sub_issue_id = get_issue_database_id(owner, repo, issue_number)
        ensure_sub_issue(owner, repo, parent_number, issue_number, sub_issue_id)
        add_to_project(issue_node_id)
    except SystemExit:
        print(f"Recovery: retry with --issue {issue_number} --parent {parent_number} to finish linkage/project/status without creating a duplicate.", file=sys.stderr)
        raise
    return issue_number, issue_url


def body_file_from_args(args: argparse.Namespace) -> tuple[str | None, bool]:
    if args.body_file:
        return args.body_file, False
    if args.body_text is None:
        return None, False
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as temp:
        temp.write(args.body_text)
        return temp.name, True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title")
    parser.add_argument("--parent", required=True, help="parent spec issue number, #number, or issue URL")
    parser.add_argument("--issue", type=int, help="existing plan issue number to resume after partial failure")
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--body-file")
    body_group.add_argument("--body-text")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    body_file, delete_body = body_file_from_args(args)
    try:
        issue_number, issue_url = create_plan(args.title, body_file, args.parent, args.issue)
        print(f"issue_number={issue_number}")
        print(f"issue_url={issue_url}")
    finally:
        if delete_body:
            try:
                os.unlink(body_file)
            except OSError:
                pass


if __name__ == "__main__":
    main()
