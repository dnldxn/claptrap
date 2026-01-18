---
name: finish-openspec-change
description: "Mark all remaining Tasks complete and archive this OpenSpec change."
model: github-copilot/gemini-3-flash-preview
---

## Overview

Finish an OpenSpec change by marking all remaining Tasks complete and archiving the change.

**Inputs:**
- `change-id`: $ARGUMENTS (the approved proposal under `openspec/changes/<change-id>/`)

## Skills

Load the following skills:
- `memory`
- `openspec-change-proposal`

## Workflow Steps

1. Mark all remaining tasks complete (except manual verification tasks).
    - If you are not sure how to do this, ask for help and STOP.
2. Archive the OpenSpec change proposal.
3. Optionally write any important lessons learned to memory (be selective).
