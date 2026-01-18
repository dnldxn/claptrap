#!/usr/bin/env bash
# plan-review.sh
#
# One-shot plan review for an OpenSpec change (no code edits).
#
# Usage:
#   export AGENT_CLI="claude -p"   # or similar; must accept stdin
#   ./plan-review.sh <change-name>

set -euo pipefail

: "${AGENT_CLI:?set AGENT_CLI to your agent CLI command (must accept stdin)}"
CHANGE="${1:-}"
if [ -z "$CHANGE" ]; then
  echo "Usage: $0 <change-name>"
  exit 1
fi

cat <<EOF | $AGENT_CLI
ROLE: Plan Reviewer

Review openspec/changes/$CHANGE/{proposal.md,tasks.md} and openspec/changes/$CHANGE/specs/** against openspec/specs/**.

Checklist:
- Each task maps to a spec requirement / acceptance criterion.
- Tasks are one-iteration-sized and independently committable.
- Verification steps are explicit and realistic (AGENTS.md).
- Missing edge cases or hidden dependencies are called out.
- No refactors or scope creep disguised as "required."

Output:
- Must fix
- Should fix
- Nice to have

Do not implement code.
EOF

