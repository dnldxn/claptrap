#!/usr/bin/env bash
# refresh-openspec-workflow.sh
#
# Refreshes OpenSpec integration in a project (after upgrading tools or switching IDEs).
#
# Required environment variables:
#   PROJECT_PATH - absolute path to the target project repo
#
# Usage:
#   export PROJECT_PATH=/path/to/your-project
#   ./refresh-openspec-workflow.sh

set -euo pipefail

: "${PROJECT_PATH:?set PROJECT_PATH to the target project repo path}"
cd "$PROJECT_PATH"
openspec update
