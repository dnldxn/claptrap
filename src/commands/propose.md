---
name: propose
description: "Create OpenSpec change proposals from an existing design document."
model: claude-opus-4.5
models:
  cursor: anthropic/claude-opus-4.5
  github-copilot: claude-opus-4.5
  claude: opus
  opencode: anthropic/claude-opus-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

## Overview

Create OpenSpec change proposal(s) from an existing design document, then run a two-stage review (alignment + feasibility).

**Inputs:**
- Optional design document path (e.g., `/propose .workflow/designs/auth-flow/design.md`).

If no path is provided, list recent designs under `.workflow/designs/` and prompt the user to select one.

## Skills

Load the following skills:
- `memory`
- `design-to-proposal`

## Workflow Steps

1. Read memory for project context, decisions, anti-patterns, and patterns.
2. Determine the design document path:
   - If a path argument is provided, use it.
   - If not, list recent designs in `.workflow/designs/` and prompt the user to choose.
3. Read the design document. If it cannot be found, ask for help and STOP.
4. Invoke the `design-to-proposal` skill to create and review proposal(s).
5. Ensure the design is updated with a `## OpenSpec Proposals` section listing the created change-id(s).
6. If any significant decisions were made, write them to memory before stopping (be selective).
7. STOP. The user triggers `/implement-change` separately.
