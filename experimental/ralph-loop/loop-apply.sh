#!/usr/bin/env bash
# loop-apply.sh
#
# Runs the apply/developer agent in a loop (one task per iteration).
# Stop manually (Ctrl+C) when tasks.md has no remaining tasks.
#
# Required environment variables:
#   AGENT_CLI - the agent CLI command to run (must accept prompt text on stdin)
#
# Optional environment variables:
#   PROMPT_FILE - path to the apply prompt file (default: .claptrap/.prompts/apply.md)
#   MAX_ITERATIONS - maximum number of iterations (default: 10, set to 0 for unlimited)
#
# Usage:
#   export AGENT_CLI=opencode
#   ./loop-apply.sh
#
# Or with limits:
#   AGENT_CLI=aider MAX_ITERATIONS=5 ./loop-apply.sh

set -euo pipefail

: "${AGENT_CLI:?set AGENT_CLI to your agent CLI command (e.g., opencode, aider)}"
PROMPT_FILE="${PROMPT_FILE:-.claptrap/.prompts/apply.md}"
MAX_ITERATIONS="${MAX_ITERATIONS:-10}"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo "Starting apply loop with $AGENT_CLI"
echo "Prompt file: $PROMPT_FILE"
echo "Max iterations: $MAX_ITERATIONS (0 = unlimited)"
echo "Press Ctrl+C to stop when all tasks are complete."
echo ""

iteration=0
while true; do
  iteration=$((iteration + 1))
  
  if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$iteration" -gt "$MAX_ITERATIONS" ]; then
    echo "Reached maximum iterations ($MAX_ITERATIONS). Stopping."
    exit 0
  fi
  
  echo "=== Running apply iteration $iteration ==="
  cat "$PROMPT_FILE" | $AGENT_CLI
  echo ""
  echo "Iteration $iteration complete. Starting next iteration in 2 seconds..."
  echo "(Press Ctrl+C to stop)"
  sleep 2
done
