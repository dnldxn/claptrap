#!/usr/bin/env bash

# Required environment variables:
#   AGENT_CLI - the agent CLI command to run (must accept prompt text on stdin)
#
# Usage:
#   export AGENT_CLI=opencode
#   ./propose.sh "Add OAuth login with GitHub"

set -euo pipefail

: "${AGENT_CLI:?set AGENT_CLI to your agent CLI command (must accept stdin)}"

PROMPT_FILE="${PROMPT_FILE:-.claptrap/.prompts/propose.md}"


echo "Generating proposal..."
{
  cat "$PROMPT_FILE"
  echo ""
  echo "Request: $SPEC"
} | $AGENT_CLI 
