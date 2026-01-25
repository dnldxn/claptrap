#!/usr/bin/env bash
# loop-resolve.sh
#
# Runs the resolver agent to apply review fixes.
# Run after review to address "Must fix" items.
#
# Required environment variables:
#   AGENT_CLI - the agent CLI command to run (must accept prompt text on stdin)
#
# Optional environment variables:
#   PROMPT_FILE - path to the resolve prompt file (default: .claptrap/.prompts/resolve.md)
#
# Usage:
#   export AGENT_CLI=opencode
#   ./loop-resolve.sh

set -euo pipefail

: "${AGENT_CLI:?set AGENT_CLI to your agent CLI command (e.g., opencode, aider)}"
PROMPT_FILE="${PROMPT_FILE:-.claptrap/.prompts/resolve.md}"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo "Running resolver with $AGENT_CLI"
echo "Prompt file: $PROMPT_FILE"
echo ""

cat "$PROMPT_FILE" | $AGENT_CLI

echo ""
echo "Resolve complete. Run verification and re-review if needed."
