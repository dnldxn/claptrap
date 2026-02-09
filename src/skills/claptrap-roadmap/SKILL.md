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

## Update (new work) Mode

1. Read `docs/plans/ROADMAP.md` and the new/modified design or plan doc.
2. Add new roadmap items at feature level.
3. Add or update links to design/plan docs.
4. Update status markers when appropriate.
5. Summarize exactly what changed.

## Update (progress) Mode

1. Read `docs/plans/ROADMAP.md`.
2. Mark completed items `[x]`.
3. Mark active items `[~]`.
4. Leave not-started items as `[ ]`.
5. Summarize exactly what changed.

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

- [x] [Database schema](#database-schema)
- [~] [REST API endpoints](#rest-api-endpoints)
- [ ] [WebSocket support](#websocket-support)
- [ ] [Authentication & authorization](#authentication--authorization)

## Phase 2: Core Features

- [ ] [User profiles](#user-profiles)
- [ ] [Search](#search)

## Feature Details

### Phase 1: Foundation

#### Database schema
Core data model covering users, sessions, permissions, and audit tables. Defines foreign-key relationships, indexes, and migration strategy.
- [Design](2026-01-15-database-design.md)

#### REST API endpoints
CRUD and query endpoints for all main resources, including versioning conventions, pagination, and standardized error responses.
- [Design](2026-01-20-api-design.md) | [Plan](2026-01-22-api-endpoints.md)

#### WebSocket support
Real-time bidirectional messaging layer for live updates, presence, and push notifications to connected clients.
- [Design](2026-01-20-api-design.md)

#### Authentication & authorization
User login, token lifecycle (issue/refresh/revoke), and role-based access control across all API surfaces.
- (No design/plan doc yet.)

### Phase 2: Core Features

#### User profiles
Profile storage, user preferences, avatar upload/crop, and public profile pages with privacy controls.
- [Design](2026-02-01-user-system-design.md)

#### Search
Full-text and filtered search across key entities with ranking, facets, and type-ahead suggestions.
- (No design/plan doc yet.)
```

Format rules:
- `[ ]` not started, `[~]` in progress, `[x]` complete
- Feature-level items only (not implementation task checklists)
- Checklist items link to their corresponding heading in the **Feature Details** section (internal anchor links)
- **Feature Details** mirrors the phase structure (`### Phase N`) with a `####` heading per feature, a 1–3 sentence description (~200 chars), and links to design/plan/proposal docs (relative paths within `docs/plans/`); design/plan links are optional and many-to-many
- No dates, estimates, or assignees in roadmap content (linked docs may have dated filenames)

## Ownership & Scope Rules

This skill is the sole owner of the roadmap's format and structure. The roadmap is not designed for manual editing outside this skill.

**Scope constraint — touch only what the current task requires:**

- When adding or updating items, only modify the items and text directly relevant to the feature or task being updated.
- Never refactor, reorganize, or rewrite the document as a whole. Changes to items outside the scope of the current work are prohibited.
- Do not modify items solely to fix or normalize formatting/structure. Format changes are permitted only when the *intent* of an item needs to change (e.g., updating a description, adding a link, changing status).

**Other guardrails:**

- Never remove items unless the user explicitly requests removal.
- Always show a concise before/after style summary of edits.
- If mapping from work to roadmap item is uncertain, ask before editing.
