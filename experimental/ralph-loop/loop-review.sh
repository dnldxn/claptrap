#!/usr/bin/env bash
# loop-review.sh
#
# Runs the code reviewer agent.
# Typically run once per review cycle (not in a loop like propose/apply).
#
# Required environment variables:
#   AGENT_CLI - the agent CLI command to run (must accept prompt text on stdin)
#
# Optional environment variables:
#   PROMPT_FILE - path to the review prompt file (default: .claptrap/.prompts/review.md)
#
# Usage:
#   export AGENT_CLI=opencode
#   ./loop-review.sh

set -euo pipefail

: "${AGENT_CLI:?set AGENT_CLI to your agent CLI command (e.g., opencode, aider)}"
PROMPT_FILE="${PROMPT_FILE:-.claptrap/.prompts/review.md}"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo "Running code review with $AGENT_CLI"
echo "Prompt file: $PROMPT_FILE"
echo ""

cat "$PROMPT_FILE" | $AGENT_CLI

echo ""
echo "Review complete. Check the output for Must fix / Should fix / Nice to have items."
