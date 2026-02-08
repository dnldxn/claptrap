---
name: "claptrap-roadmap"
description: >
  Create and maintain a project-level ROADMAP.md tracking features and phases.
  Use after completing a design (brainstorming), writing an implementation plan,
  finishing implementation tasks, or when the user asks about project status or
  progress. Also use when starting a new project to create the initial roadmap.
---

# claptrap-roadmap

Maintain `docs/plans/ROADMAP.md` as a concise, phase-based view of project progress.

## Mode Detection

Pick exactly one mode at invocation time:

1. `docs/plans/ROADMAP.md` missing -> **Create**
2. A design/plan doc was just created or updated -> **Update (new work)**
3. Implementation tasks were just completed -> **Update (progress)**
4. User asked for status only -> **Read-only** (no edits)

If uncertain between modes, ask one clarifying question.

## Create Mode

1. Inspect `docs/plans/` for existing design/plan docs.
2. Ask for project goals/phases if they are unclear.
3. Create `docs/plans/ROADMAP.md` using the format spec below.
4. Show the generated roadmap to the user.
5. Commit the new roadmap.

## Update (new work) Mode

1. Read `docs/plans/ROADMAP.md` and the new/modified design or plan doc.
2. Add new roadmap items at feature level.
3. Add or update links to design/plan docs.
4. Update status markers when appropriate.
5. Summarize exactly what changed.
6. Commit.

## Update (progress) Mode

1. Read `docs/plans/ROADMAP.md`.
2. Mark completed items `[x]`.
3. Mark active items `[~]`.
4. Leave not-started items as `[ ]`.
5. Summarize exactly what changed.
6. Commit.

## Read-only Mode

1. Read `docs/plans/ROADMAP.md`.
2. Summarize by phase: complete, in progress, upcoming.
3. Do not edit files.

## ROADMAP Format Spec

Use this exact structure and marker semantics:

```markdown
# Project Roadmap

> Brief project description

## Phase 1: Foundation

- [x] Database schema - [design](2026-01-15-database-design.md)
- [~] REST API endpoints - [design](2026-01-20-api-design.md) | [plan](2026-01-22-api-endpoints.md)
- [ ] WebSocket support - [design](2026-01-20-api-design.md)
- [ ] Authentication & authorization

## Phase 2: Core Features

- [ ] User profiles - [design](2026-02-01-user-system-design.md)
- [ ] Search
```

Format rules:
- `[ ]` not started, `[~]` in progress, `[x]` complete
- Feature-level items only (not implementation task checklists)
- Design/plan links are optional and many-to-many
- Use relative links within `docs/plans/`
- No dates, estimates, or assignees

## Safety Rules

- Never remove items unless the user explicitly requests removal.
- Never restructure phases unless the user explicitly requests it.
- Always preserve user-authored notes and existing formatting style.
- Always show a concise before/after style summary of edits.
- If mapping from work to roadmap item is uncertain, ask before editing.
