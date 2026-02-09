#!/usr/bin/env python3
# Memory enforcement script - runs at session end and post-tool events.

import argparse
import json
import subprocess
import sys
from pathlib import Path

CLAPTRAP_DIR = Path(".claptrap")
INBOX_FILE = CLAPTRAP_DIR / "memory_inbox.md"


def get_session_activity():
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"], capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            return {
                "has_changes": True,
                "files": len(result.stdout.strip().split("\n")) - 1,
            }
    except Exception: pass
    return {"has_changes": False, "files": 0}


def get_inbox_entry_count():
    if not INBOX_FILE.exists(): return 0
    return INBOX_FILE.read_text().count("\n## ")


# Block session end if work was done but no memories captured. Returns 0=allow, 2=block.
def session_end_gate():
    activity = get_session_activity()
    if not activity["has_changes"] or get_inbox_entry_count() > 0: return 0

    output = {
        "action": "prompt",
        "message": (
            f"Session had activity ({activity['files']} files changed) but no memories captured.\n\n"
            "Before ending, please review:\n"
            "- Any non-obvious decisions made?\n"
            "- Patterns worth repeating or avoiding?\n"
            "- Context future sessions would need?\n\n"
            "Capture learnings to .claptrap/memory_inbox.md"
        ),
    }
    print(json.dumps(output))
    return 2


# Occasional nudge after file edits. Always returns 0.
def post_tool_nudge():
    counter_file = CLAPTRAP_DIR / ".edit_counter"

    count = int(counter_file.read_text().strip()) if counter_file.exists() else 0
    count += 1
    counter_file.write_text(str(count))

    if count % 10 == 0:
        print(
            json.dumps(
                {
                    "action": "notify",
                    "message": f"You've made {count} edits. Any learnings worth capturing?",
                }
            )
        )

    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", choices=["session-end", "post-tool"], required=True)
    args = parser.parse_args()

    sys.exit(session_end_gate() if args.event == "session-end" else post_tool_nudge())


if __name__ == "__main__":
    main()
