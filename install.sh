#!/usr/bin/env bash
# install.sh
#
# Installs the OpenSpec workflow into the project.
#
# Usage:
#   CLAPTRAP_PATH=~/projects/claptrap $CLAPTRAP_PATH/install.sh

set -euo pipefail


# ---- 1) CLAPTRAP_PATH ----
: "${CLAPTRAP_PATH:?set CLAPTRAP_PATH to the claptrap repo path}"

# ---- 2) PROVIDER (numbers-only choice) ----
PROVIDERS=("Cursor" "Github Copilot" "OpenCode" "Claude" "Codex" "Gemini")
PROVIDER_DIRS=(".cursor" ".github" ".opencode" ".claude" ".codex" ".gemini")
DEFAULT_PROVIDER_NUM=1  # 1=Cursor, 2=Github Copilot, 3=OpenCode, 4=Claude, 5=Codex, 6=Gemini

while true; do
  echo
  echo "Select PROVIDER:"
  for i in "${!PROVIDERS[@]}"; do
    printf "  %d) %s (%s)\n" $((i+1)) "${PROVIDERS[$i]}" "${PROVIDER_DIRS[$i]}"
  done

  read -r -p "Enter 1-${#PROVIDERS[@]} [$DEFAULT_PROVIDER_NUM]: " n </dev/tty
  n="${n:-$DEFAULT_PROVIDER_NUM}"

  if [[ "$n" =~ ^[0-9]+$ ]] && (( n>=1 && n<=${#PROVIDERS[@]} )); then
    PROVIDER="${PROVIDERS[$((n-1))]}"
    PROVIDER_DIR="${PROVIDER_DIRS[$((n-1))]}"
    break
  fi

  echo "Please enter a number between 1 and ${#PROVIDERS[@]}."
done

echo
echo "Using:"
echo "  CLAPTRAP_PATH=$CLAPTRAP_PATH"
echo "  PROVIDER=$PROVIDER"
echo "  PROVIDER_DIR=$PROVIDER_DIR"


export PROVIDER
export PROVIDER_DIR
# copilot --allow-all --model 'claude-haiku-4.5' --disable-mcp-server github-mcp-server --prompt "$(cat $CLAPTRAP_PATH/bootstrap/install.md)"
claude --model 'sonnet' --add-dir "$CLAPTRAP_PATH" --output-format text --tools "Bash,Read,Edit,Write,Glob,Grep,WebFetch" --allowedTools "Bash(printenv CLAPTRAP_PATH)" --no-chrome "$(cat $CLAPTRAP_PATH/bootstrap/install.md)"
# codex -m gpt-5.1-codex-mini exec "$(cat $CLAPTRAP_PATH/bootstrap/install.md)"
# gemini --model gemini-3-flash-preview --include-directories "$CLAPTRAP_PATH" "$(cat $CLAPTRAP_PATH/bootstrap/install.md)"
# gemini --model gemini-3-flash-preview --yolo --include-directories "$CLAPTRAP_PATH" "$(cat $CLAPTRAP_PATH/bootstrap/install.md)"