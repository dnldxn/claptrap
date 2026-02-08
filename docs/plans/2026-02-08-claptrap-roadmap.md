# claptrap-roadmap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task.

**Goal:** Create the claptrap-roadmap skill and integrate it into the
bootstrap system.

**Architecture:** Single SKILL.md file with YAML frontmatter, installed via
existing claptrap bootstrap. Integration via AGENTS.md template and skill
registry.

**Tech Stack:** Markdown only (no scripts/code)

**Design:** [claptrap-roadmap design](2026-02-08-claptrap-roadmap-design.md)

---

### Task 1: Create the skill directory and SKILL.md

**Files:**
- Create: `src/skills/claptrap-roadmap/SKILL.md`

**Step 1: Create the skill file**

Write `src/skills/claptrap-roadmap/SKILL.md` with YAML frontmatter:

```yaml
---
name: "claptrap-roadmap"
description: >
  Create and maintain a project-level ROADMAP.md tracking features and phases.
  Use after completing a design (brainstorming), writing an implementation plan,
  finishing implementation tasks, or when the user asks about project status or
  progress. Also use when starting a new project to create the initial roadmap.
---
```

The skill body should cover:

- **Mode detection**: Determine create / update-new-work / update-progress /
  read-only based on whether ROADMAP.md exists and what just happened.
- **Create mode**: Check `docs/plans/` for existing docs, ask user for project
  goals/phases, generate initial ROADMAP.md, show result, commit.
- **Update (new work) mode**: Read ROADMAP.md and the new/modified doc. Add new
  items, update links, update statuses. Summarize changes. Commit.
- **Update (progress) mode**: Read ROADMAP.md, mark completed items `[x]` and
  active items `[~]`. Summarize changes. Commit.
- **Document format spec**: Include the format example from the design doc
  showing phases, checkbox states (`[ ]` `[~]` `[x]`), and doc links.
- **Safety rules**: Never remove items or restructure without user request.
  Always show what changed. Ask if uncertain about item mapping.

Follow the concise style of existing claptrap skills (`claptrap-memory`,
`memory-capture`). Target under 150 lines.

**Step 2: Verify the skill file exists and has valid frontmatter**

Run: `head -10 src/skills/claptrap-roadmap/SKILL.md`

Expected: YAML frontmatter with `name` and `description` fields.

**Step 3: Commit**

```bash
git add src/skills/claptrap-roadmap/SKILL.md
git commit -m "feat: add claptrap-roadmap skill"
```

---

### Task 2: Update the skill registry

**Files:**
- Modify: `src/skills/AGENTS.md`

**Step 1: Add registry entry**

Add a new entry under the `## Skill Registry` section, after the
`claptrap-memory` entry:

```markdown
### `claptrap-roadmap`
- **Path**: `skills/claptrap-roadmap/SKILL.md`
- **Purpose**: Create and maintain a project-level ROADMAP.md tracking features, phases, and progress.
- **Use when**: After completing a design doc or implementation plan, after finishing implementation tasks, or when asked about project status.
```

**Step 2: Verify the registry is well-formed**

Run: `grep "claptrap-roadmap" src/skills/AGENTS.md`

Expected: The new entry appears.

**Step 3: Commit**

```bash
git add src/skills/AGENTS.md
git commit -m "docs: register claptrap-roadmap in skill registry"
```

---

### Task 3: Update the AGENTS.md template

**Files:**
- Modify: `bootstrap/templates/agents_md.txt`

**Step 1: Add the Project Roadmap section**

Insert before the closing `<!-- CLAPTRAP:END -->` tag:

```markdown
# Project Roadmap
- After completing a design doc or implementation plan, load the
  `claptrap-roadmap` skill and update `docs/plans/ROADMAP.md`.
- After completing implementation tasks, update the roadmap to
  reflect progress.
- The roadmap should stay concise — feature-level items only.
```

**Step 2: Verify the template renders correctly**

Run: `cat bootstrap/templates/agents_md.txt`

Expected: New section appears before `<!-- CLAPTRAP:END -->`.

**Step 3: Commit**

```bash
git add bootstrap/templates/agents_md.txt
git commit -m "feat: add roadmap guidance to AGENTS.md template"
```

---

### Task 4: Create claptrap's own ROADMAP.md

**Files:**
- Create: `docs/plans/ROADMAP.md`

**Step 1: Create the roadmap**

Based on GOALS.md, TODO.md, existing design docs, and the current state of
the project, create an initial roadmap for claptrap itself. This serves as both
a working example and actual project tracking.

Use the format from the design doc. Reference existing design and plan files
with relative links. Include phases that reflect claptrap's current development
trajectory:

- **Phase 1 (Foundation)**: Installer, memory system, core skills. Mostly
  complete — reference the existing design docs.
- **Phase 2 (Workflow)**: Brainstorming/planning integration, roadmap skill,
  plan review with multi-agent debate, implement/review/fix loop.
- **Phase 3 (Polish)**: Cross-environment testing, documentation updates,
  Snowflake skill improvements, CLI tool installation, MCP configuration.

Mark items based on actual project state: installer and memory system are `[x]`,
roadmap skill is `[~]`, review loop and debate are `[ ]`.

**Step 2: Verify links resolve**

Run: `ls docs/plans/` and confirm referenced design/plan files exist.

**Step 3: Commit**

```bash
git add docs/plans/ROADMAP.md
git commit -m "feat: add project roadmap for claptrap"
```

---

### Task 5: Verify end-to-end

**Step 1: Verify installer discovers the new skill**

Run: `ls src/skills/claptrap-roadmap/`

Expected: `SKILL.md` exists.

**Step 2: Verify the skill is not excluded by skip patterns**

Check `bootstrap/claptrap.yaml` `skip_patterns` — confirm none match
`skills/claptrap-roadmap/**`.

**Step 3: Read through ROADMAP.md and confirm scannability**

The roadmap should be readable in under 30 seconds and clearly show what's
done, in progress, and upcoming.
