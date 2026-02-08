# claptrap-roadmap Skill Design

**Goal:** A single claptrap skill that maintains a concise, human-readable
`docs/plans/ROADMAP.md` in target projects, tracking features and phases with
links to design and implementation documents.

**Architecture:** Pure-instructions skill (no scripts/assets) installed via
claptrap's bootstrap system. Triggered by skill description matching and an
AGENTS.md template note. Operates in three modes: create, update after
design/plan work, and update after task completion.

## Document Format

The roadmap lives at `docs/plans/ROADMAP.md`:

```markdown
# Project Roadmap

> Brief project description

## Phase 1: Foundation

- [x] Database schema — [design](2026-01-15-database-design.md)
- [~] REST API endpoints — [design](2026-01-20-api-design.md) | [plan](2026-01-22-api-endpoints.md)
- [ ] WebSocket support — [design](2026-01-20-api-design.md)
- [ ] Authentication & authorization

## Phase 2: Core Features

- [ ] User profiles — [design](2026-02-01-user-system-design.md)
- [ ] Search
```

**Format rules:**

- `[ ]` not started, `[~]` in progress, `[x]` complete
- Feature-level items (not individual implementation tasks)
- Links to design/plan docs optional, added when they exist
- Design docs have many-to-many relationship with items
- Relative links within `docs/plans/`
- No dates, estimates, or assignees
- Phases group related work; order implies sequence

## Skill Behavior

### Mode Detection

On invocation, determine mode:

1. No ROADMAP.md exists -> **Create**
2. Design or plan just written/modified -> **Update (new work)**
3. Tasks completed -> **Update (progress)**
4. User asked about status -> **Read and summarize** (no edits)

### Create Mode

- Check `docs/plans/` for existing design docs
- Ask user for project goals/phases (or infer from existing docs)
- Generate initial ROADMAP.md
- Show result, ask for adjustments
- Commit

### Update (New Work) Mode

- Read ROADMAP.md and the new/modified doc
- Add new items, update links, update statuses
- Summarize changes to the user
- Commit

### Update (Progress) Mode

- Read ROADMAP.md
- Mark completed items `[x]`, active items `[~]`
- Summarize changes to the user
- Commit

### Safety Rules

- Never remove items or restructure phases without explicit user request
- Always show what changed
- Preserve existing formatting and user-added notes
- If uncertain whether an item maps to current work, ask

## Triggering and Integration

### Skill Description

```yaml
name: claptrap-roadmap
description: >
  Create and maintain a project-level ROADMAP.md tracking features
  and phases. Use after completing a design (brainstorming), writing
  an implementation plan, finishing implementation tasks, or when the
  user asks about project status or progress. Also use when starting
  a new project to create the initial roadmap.
```

### AGENTS.md Template Note

Added to `bootstrap/templates/agents_md.txt`:

```markdown
# Project Roadmap
- After completing a design doc or implementation plan, load the
  `claptrap-roadmap` skill and update `docs/plans/ROADMAP.md`.
- After completing implementation tasks, update the roadmap to
  reflect progress.
- The roadmap should stay concise — feature-level items only.
```

## Deliverables

1. `/src/skills/claptrap-roadmap/SKILL.md` -- Skill file
2. `bootstrap/templates/agents_md.txt` -- Add "Project Roadmap" section
3. `src/skills/AGENTS.md` -- Add registry entry
4. `docs/plans/ROADMAP.md` -- Claptrap's own roadmap (working example)

## Not Building

- No scripts or bundled resources
- No modifications to upstream superpowers skills
- No subagent infrastructure
- No enforcement hooks
