# src/ — AI Agent Instructions

This directory contains installable workflow artifacts. When editing files here:

- **Target audience**: These files will be used in other projects after installation.
- **Relative paths**: Use paths relative to the installed location (e.g., `skills/memory/SKILL.md`), not this repo's root.
- **Provider-agnostic**: Avoid provider-specific features; adapters handle differences.
- **Self-contained**: Each agent/command/skill should work independently with minimal dependencies.

For repo-level guidance (contributing, structure decisions), see the root `/AGENTS.md`.

## Workflow Overview

The Claptrap workflow has three phases:

### Phase 1: Brainstorm (`/claptrap-brainstorm`)
- Turn raw ideas into validated design documents
- Output: `.claptrap/designs/<feature-slug>/design.md`

### Phase 2: Propose (`/claptrap-propose`)
- Generate OpenSpec artifacts from an approved design
- Runs alignment + feasibility review (max 2 cycles each)
- Output: `openspec/changes/<change-id>/{proposal.md, specs/**/spec.md, tasks.md}`

### Phase 3: Review (`/claptrap-review`)
- Validate all artifacts against the source design
- Explicit quality gate before implementation
- Output: `APPROVED` or `REVISE` verdict

### Implementation (Native OpenSpec)
- `/opsx:apply` — Implement tasks from a reviewed change
- `/opsx:verify` — Validate implementation matches specs
- `/opsx:archive` — Archive completed change
