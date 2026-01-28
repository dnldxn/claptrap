---
name: "claptrap:brainstorm"
description: "Turn ideas into fully formed OpenSpec proposals through collaborative dialogue, memory context, and targeted research."
model: claude-opus-4.5
models:
  cursor: anthropic/claude-opus-4.5
  github-copilot: claude-opus-4.5
  claude: opus
  opencode: anthropic/claude-opus-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

Invoke the `claptrap:brainstorming` skill and follow it EXACTLY as presented to you.  Before and after brainstorming, read and/or write memories as instructed by the `claptrap:memory` skill.

<!-- After brainstorming, invoke the `openspec-create-proposal` skill and follow it EXACTLY as presented to you. -->
After brainstorming: 
- Generate a `<feature-slug>` from the design title using kebab-case.
- Write the validated design to `.claptrap/designs/<feature-slug>/design.md`.

**User Brainstorm Idea/Prompt:** $ARGUMENTS
