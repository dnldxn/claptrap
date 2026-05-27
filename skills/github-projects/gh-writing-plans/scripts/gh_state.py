#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Print Project #2 board state: specs + sub-plans with statuses."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any


PROJECT_NUMBER = "2"
OWNER = "dnldxn"
STATUS_FIELD = "Status"
SPEC_LABEL = "spec"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def detect_repo() -> tuple[str, str]:
    result = run(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        die(f"git remote get-url origin failed: {result.stderr.strip()}")

    url = result.stdout.strip()
    match = re.fullmatch(r"git@github\.com:([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        match = re.fullmatch(r"https://(?:[^@/]+@)?github\.com/([^/]+)/(.+?)(?:\.git)?", url)
    if not match:
        die(f"cannot parse GitHub origin remote: {redact_url(url)}")

    return match.group(1), match.group(2)


def redact_url(url: str) -> str:
    return re.sub(r"https://[^/@]+(?::[^/@]*)?@", "https://***@", url)


def status_from_item(item: dict[str, Any]) -> str:
    status = item.get(STATUS_FIELD) or item.get(STATUS_FIELD.lower())
    if isinstance(status, dict):
        return str(status.get("name") or status.get("optionName") or "")
    if status is None:
        return ""
    return str(status)


def repository_from_content(content: dict[str, Any], default_repo: str) -> str:
    repository = content.get("repository")
    if isinstance(repository, dict):
        name_with_owner = repository.get("nameWithOwner")
        if name_with_owner:
            return str(name_with_owner)
        owner = repository.get("owner")
        owner_login = owner.get("login") if isinstance(owner, dict) else owner
        name = repository.get("name")
        if owner_login and name:
            return f"{owner_login}/{name}"
    if isinstance(repository, str) and repository:
        return repository
    return default_repo


def board_items() -> list[dict[str, Any]]:
    repo_owner, repo_name = detect_repo()
    default_repo = f"{repo_owner}/{repo_name}"
    result = run([
        "gh",
        "project",
        "item-list",
        PROJECT_NUMBER,
        "--owner",
        OWNER,
        "--format",
        "json",
        "--limit",
        "100",
    ])
    if result.returncode != 0:
        die(f"gh project item-list failed: {result.stderr.strip()}")

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        die(f"gh project item-list returned invalid JSON: {exc}")
    if not isinstance(payload, dict):
        die("gh project item-list returned unexpected JSON shape")
    items = payload.get("items", [])
    if not isinstance(items, list):
        die("gh project item-list returned non-list items")

    mapped: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        content = item.get("content") or {}
        if not isinstance(content, dict):
            continue
        number = content.get("number")
        if number is None:
            continue
        try:
            issue_number = int(number)
        except (TypeError, ValueError):
            continue
        mapped.append({
            "number": issue_number,
            "title": content.get("title") or "",
            "url": content.get("url") or "",
            "repository": repository_from_content(content, default_repo),
            "status": status_from_item(item),
            "id": item.get("id") or content.get("id") or "",
        })
    return mapped


def spec_issues(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for item in items:
        repo_arg = ["--repo", item["repository"]] if item.get("repository") else []
        result = run([
            "gh",
            "issue",
            "view",
            str(item["number"]),
            *repo_arg,
            "--json",
            "labels",
            "--jq",
            ".labels[].name",
        ])
        if result.returncode == 0 and SPEC_LABEL in result.stdout.splitlines():
            specs.append(item)
    return specs


def sub_issues(repository: str, parent_number: int) -> list[int]:
    if "/" not in repository:
        print(f"warning: cannot determine repository for #{parent_number}", file=sys.stderr)
        return []
    owner, repo = repository.split("/", 1)
    result = run([
        "gh",
        "api",
        f"/repos/{owner}/{repo}/issues/{parent_number}/sub_issues",
        "--jq",
        ".[].number",
    ])
    if result.returncode != 0:
        print(f"warning: sub-issue lookup failed for {repository}#{parent_number}: {result.stderr.strip()}", file=sys.stderr)
        return []

    numbers: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
            try:
                numbers.append(int(line))
            except ValueError:
                print(f"warning: ignored non-numeric sub-issue value: {line}", file=sys.stderr)
    return numbers


def state() -> list[dict[str, Any]]:
    repo_owner, repo_name = detect_repo()
    target_repo = f"{repo_owner}/{repo_name}"
    items = [item for item in board_items() if item.get("repository") == target_repo]
    item_by_repo_number = {(item.get("repository", ""), item["number"]): item for item in items}

    rows: list[dict[str, Any]] = []
    for spec in spec_issues(items):
        plans = []
        repository = spec.get("repository", "")
        for number in sub_issues(repository, spec["number"]):
            plan = item_by_repo_number.get((repository, number), {"number": number, "title": "", "status": ""})
            plans.append({
                "number": plan["number"],
                "title": plan.get("title", ""),
                "status": plan.get("status", ""),
            })
        rows.append({
            "spec": {
                "number": spec["number"],
                "title": spec["title"],
                "url": spec["url"],
                "status": spec["status"],
            },
            "plans": plans,
        })
    return rows


def print_tree(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        spec = row["spec"]
        print(f"# {spec['number']} - {spec['title']} [{spec['status']}]")
        if spec["url"]:
            print(f"  {spec['url']}")
        if not row["plans"]:
            print("  (no plans)")
        for plan in row["plans"]:
            print(f"  - #{plan['number']} - {plan['title']} [{plan['status']}]")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    rows = state()
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print_tree(rows)


if __name__ == "__main__":
    main()
