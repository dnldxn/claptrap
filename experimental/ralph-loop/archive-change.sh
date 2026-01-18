#!/usr/bin/env bash
# archive-change.sh
#
# Archives a completed OpenSpec change (merges spec deltas into living specs).
#
# Usage:
#   ./archive-change.sh <change-name>

set -euo pipefail

CHANGE="${1:-}"
if [ -z "$CHANGE" ]; then
  echo "Usage: $0 <change-name>"
  exit 1
fi

openspec archive "$CHANGE" --yes

