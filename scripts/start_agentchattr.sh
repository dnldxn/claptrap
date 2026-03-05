#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

RIGHT_PANE=$(wezterm cli split-pane --right --percent 50 --cwd "$PWD" -- zsh -lc 'sh ~/apps/agentchattr/macos-linux/start_codex.sh')
BOTTOM_LEFT=$(wezterm cli split-pane --bottom --percent 50 --cwd "$PWD" -- zsh -lc 'exec zsh')
BOTTOM_RIGHT=$(wezterm cli split-pane --pane-id "$RIGHT_PANE" --bottom --percent 50 --cwd "$PWD" -- zsh -lc 'exec zsh')

exec sh ~/apps/agentchattr/macos-linux/start_claude.sh
