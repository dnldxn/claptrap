# Memory Skills Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the two-skill memory system (memory-capture + memory-curator) to replace the current single-skill approach.

**Architecture:** Two separate skills with clear responsibilities: capture (high recall, during work) and curator (high precision, periodic review). The existing claptrap-memory skill becomes a meta-skill that loads at session start and references both.

**Tech Stack:** Markdown skills with YAML frontmatter, following the superpowers/claptrap skill conventions.

---

## Background

The design document (`docs/plans/2025-02-02-claptrap-memory-design.md`) specifies:
- **memory-capture**: Captures candidates to `.claptrap/memory_inbox.md` during work
- **memory-curator**: Reviews inbox, scores candidates (0-8 rubric), promotes winners to `.claptrap/memories.md`

The infrastructure is already complete:
- `bootstrap/lib/enforcement.py` - Enforcement script
- `bootstrap/lib/memory.py` - Installation logic
- `bootstrap/lib/providers.py` - Hooks configuration
- Templates for both files exist

---

## Task 1: Create memory-capture skill

**Files:**
- Create: `src/skills/memory-capture/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p src/skills/memory-capture
```

**Step 2: Write the skill file**

Create `src/skills/memory-capture/SKILL.md` with this content:

```markdown
---
name: "memory-capture"
description: High-recall capture of candidate memories into .claptrap/memory_inbox.md during work sessions.
---

# Memory Capture

You maintain a two-file memory system:
- **Durable memories**: `.claptrap/memories.md` (high precision, curated)
- **Candidate inbox**: `.claptrap/memory_inbox.md` (high recall, captured during work)

## Your job

Continuously capture *candidate* learnings while working, not only on failures or incidents.

## Trigger signals (capture when any of these happen)

- A **non-obvious decision** or tradeoff is made that future sessions could accidentally undo
- A **gotcha** is discovered (environment, tooling, CI, build, dependencies, docs)
- The user **corrects a misconception** or states a preference that should persist
- A **pattern** or **anti-pattern** emerges during implementation
- A **multi-step procedure** is performed that's easy to forget
- A **constraint** is discovered that future changes could violate
- You learn something about **this codebase** that isn't obvious from the code

## Candidate format (required)

Write candidates to `.claptrap/memory_inbox.md` with this exact shape:

```
## [YYYY-MM-DD] - [Brief descriptive title]
- **Trigger**: When this applies (include recognizable signature/error/message if possible)
- **Action**: What to do (or avoid) in future
- **Context**: Area/module this applies to
```

### Rules

1. **Required fields**: Every candidate MUST have Trigger and Action. If you can't state both, don't capture.
2. **Capture early**: Write candidates as soon as the insight appears, don't wait until session end.
3. **1-3 per session**: Prefer a few high-quality candidates over many weak ones.
4. **Never store secrets**: No API keys, tokens, credentials, or sensitive data.
5. **Don't curate yet**: Only write to inbox, never directly to `memories.md` from this skill.

## Examples

### Good candidate

```
## 2025-02-04 - pytest fixtures in conftest.py must use absolute imports
- **Trigger**: Import errors when running tests from different directories
- **Action**: Always use `from package.module import X` not relative imports in conftest.py
- **Context**: Testing, pytest configuration
```

### Bad candidate (too vague)

```
## 2025-02-04 - Tests are tricky
- **Trigger**: When tests fail
- **Action**: Debug more carefully
- **Context**: Testing
```

## Behavior

- Read inbox at session start to avoid duplicates
- Append new candidates after the `<!-- Add new entries below this line -->` marker
- If a similar candidate exists, don't duplicate - mention you're skipping it
```

**Step 3: Verify file was created**

```bash
ls -la src/skills/memory-capture/SKILL.md
cat src/skills/memory-capture/SKILL.md | head -20
```

**Step 4: Commit**

```bash
git add src/skills/memory-capture/
git commit -m "feat: add memory-capture skill for high-recall candidate capture"
```

---

## Task 2: Create memory-curator skill

**Files:**
- Create: `src/skills/memory-curator/SKILL.md`

**Step 1: Create skill directory**

```bash
mkdir -p src/skills/memory-curator
```

**Step 2: Write the skill file**

Create `src/skills/memory-curator/SKILL.md` with this content:

```markdown
---
name: "memory-curator"
description: Score candidates in .claptrap/memory_inbox.md and persist winners to .claptrap/memories.md
---

# Memory Curator

You curate candidate memories into durable entries using a deterministic scoring rubric.

## Inputs

- **Candidates**: `.claptrap/memory_inbox.md`
- **Durable store**: `.claptrap/memories.md`

## Scoring rubric (0-8 scale)

Score each candidate on three dimensions:

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| **Recurrence** | One-time issue | Might recur occasionally | Will definitely recur |
| **Impact** | Minor annoyance | Moderate (saves time) | Significant (prevents bugs/data loss) |
| **Actionability** | Vague guidance | Somewhat clear | Crystal clear trigger + action |

**Additional points:**
- +1 if includes specific error message or signature
- +1 if repo-specific (not generic knowledge)

### Threshold decisions

| Score | Action |
|-------|--------|
| >= 6 | **Persist** to `memories.md` |
| 4-5 | **Keep** in inbox - needs better Trigger/Verify |
| <= 3 | **Drop** from inbox |

## Persisted memory format

Each saved memory must follow this format in `.claptrap/memories.md`:

```
---

## [Descriptive title - imperative or declarative]
Type: decision | pattern | anti-pattern | lesson | solution | Date: YYYY-MM-DD | Tags: tag1, tag2

[1-3 sentences: Trigger condition + Action to take + Brief rationale if not obvious]

---
```

## Curation rules

1. **Score every candidate** using the rubric before deciding
2. **Show your work** - state the score breakdown for each candidate
3. **Update over duplicate** - if a memory on the same topic exists, update it rather than adding new
4. **Keep entries short** - 3-5 lines max per memory
5. **Newest first** - insert new memories at the top (after the header)
6. **Clear the processed** - remove dropped and promoted candidates from inbox
7. **Never store secrets**

## Workflow

1. Read `.claptrap/memory_inbox.md`
2. For each candidate:
   - Score using rubric (show breakdown)
   - Decide: persist (>=6), keep (4-5), or drop (<=3)
3. For persisted candidates:
   - Check if similar memory exists in `.claptrap/memories.md`
   - If yes: update existing entry
   - If no: add new entry at top
4. Update inbox:
   - Remove dropped candidates
   - Remove persisted candidates
   - Keep borderline (4-5) candidates for future context

## Example curation

**Candidate:**
```
## 2025-02-04 - pytest fixtures in conftest.py must use absolute imports
- **Trigger**: Import errors when running tests from different directories
- **Action**: Always use `from package.module import X` not relative imports
- **Context**: Testing, pytest configuration
```

**Scoring:**
- Recurrence: 2 (will hit this every time we add fixtures)
- Impact: 1 (moderate - wastes debugging time)
- Actionability: 2 (clear trigger and action)
- Specific signature: +1 (import errors)
- Repo-specific: +0 (general pytest knowledge)

**Total: 6 - PERSIST**

**Resulting memory entry:**
```
---

## Use absolute imports in pytest conftest.py
Type: pattern | Date: 2025-02-04 | Tags: testing, pytest

When adding fixtures to conftest.py, always use absolute imports (`from package.module import X`) not relative imports. Running tests from different directories causes import errors with relative imports.

---
```
```

**Step 3: Verify file was created**

```bash
ls -la src/skills/memory-curator/SKILL.md
cat src/skills/memory-curator/SKILL.md | head -20
```

**Step 4: Commit**

```bash
git add src/skills/memory-curator/
git commit -m "feat: add memory-curator skill with deterministic scoring rubric"
```

---

## Task 3: Update claptrap-memory skill as meta-skill

**Files:**
- Modify: `src/skills/claptrap-memory/SKILL.md`

**Step 1: Read current file**

Review the existing content (already read in planning phase).

**Step 2: Replace with meta-skill content**

Update `src/skills/claptrap-memory/SKILL.md` with:

```markdown
---
name: "claptrap-memory"
description: Capture and retain project decisions, patterns, anti-patterns, and lessons learned.
---

# Memory Skill

This is a **two-file, two-skill memory system** for capturing and retaining project knowledge.

## Files

| File | Purpose | Access |
|------|---------|--------|
| `.claptrap/memory_inbox.md` | Candidate learnings (high recall) | Write during work |
| `.claptrap/memories.md` | Durable memories (high precision) | Read anytime, write via curator |

## Skills

### memory-capture
**Use during work** to capture candidate learnings as they happen.

Trigger signals:
- Non-obvious decisions or tradeoffs
- Gotchas (env, tooling, CI, dependencies)
- User corrections or preferences
- Patterns/anti-patterns discovered
- Multi-step procedures
- Constraints that could be violated

### memory-curator
**Use periodically** (or at session end) to review inbox and promote quality entries.

Uses scoring rubric (0-8):
- Recurrence (0-2)
- Impact (0-2)  
- Actionability (0-2)
- Bonuses for specificity and repo-relevance

Thresholds: >=6 persist, 4-5 keep, <=3 drop

## Quick reference

### Session start
1. Read `.claptrap/memories.md` for relevant context
2. Skim inbox for pending candidates

### During work
Use **memory-capture** when you notice durable learnings.

### Session end (or periodically)
Use **memory-curator** to review and promote inbox candidates.

## Memory format

### Inbox candidate
```
## [YYYY-MM-DD] - [Brief title]
- **Trigger**: When this applies
- **Action**: What to do/avoid
- **Context**: Area this applies to
```

### Durable memory
```
---

## [Descriptive title]
Type: decision | pattern | anti-pattern | lesson | solution | Date: YYYY-MM-DD | Tags: tag1, tag2

[1-3 sentences describing trigger, action, and rationale]

---
```

## Valid memory types

| Type | When to use |
|------|-------------|
| decision | Significant tradeoffs or choices |
| pattern | Approaches that worked well |
| anti-pattern | Approaches to avoid |
| lesson | Post-change learnings |
| solution | Solutions to tricky problems |

## Rules

- **Never store secrets**: No API keys, tokens, credentials, or sensitive data
- **Update over duplicate**: Prefer updating existing memories to adding duplicates
- **Prefer update over delete**: Delete only when incorrect, redundant, or harmful
- **Be selective**: Not everything is worth remembering - that's what the rubric is for
```

**Step 3: Verify changes**

```bash
cat src/skills/claptrap-memory/SKILL.md | head -30
```

**Step 4: Commit**

```bash
git add src/skills/claptrap-memory/SKILL.md
git commit -m "refactor: update claptrap-memory to meta-skill referencing capture and curator"
```

---

## Task 4: Update design doc status

**Files:**
- Modify: `docs/plans/2025-02-02-claptrap-memory-design.md`

**Step 1: Update the checklist**

Change the "Remaining" items to "Completed" in the Implementation Checklist section:

```markdown
### Completed

- [x] Research hooks across all 6 environments
- [x] Document hooks in `docs/*.md` for each environment
- [x] Design two-file data model
- [x] Design two-skill system with rubric
- [x] Design enforcement strategy (soft + hard)
- [x] Create `bootstrap/lib/` module structure
- [x] Implement `lib/providers.py` with hooks metadata
- [x] Implement `lib/memory.py` installation logic
- [x] Implement `lib/enforcement.py` script
- [x] Integrate into `bootstrap/install.py`
- [x] Create `memory_inbox_md.txt` template
- [x] Create `src/skills/memory-capture/SKILL.md`
- [x] Create `src/skills/memory-curator/SKILL.md`
- [x] Update `src/skills/claptrap-memory/SKILL.md`

### Remaining

- [ ] Test installation across environments
- [ ] Add memory system to AGENTS.md template
```

**Step 2: Commit**

```bash
git add docs/plans/2025-02-02-claptrap-memory-design.md
git commit -m "docs: update memory design checklist - skills implemented"
```

---

## Task 5: Update skills registry in AGENTS.md

**Files:**
- Modify: `src/skills/AGENTS.md`

**Step 1: Add new skills to registry**

Add entries for memory-capture and memory-curator in the Skill Registry section:

```markdown
### `memory-capture`
- **Path**: `skills/memory-capture/SKILL.md`
- **Purpose**: Capture candidate learnings to inbox during work sessions (high recall).
- **Use when**: You discover non-obvious decisions, gotchas, patterns, or lessons worth potentially keeping.

### `memory-curator`
- **Path**: `skills/memory-curator/SKILL.md`
- **Purpose**: Score inbox candidates and promote quality entries to durable memory (high precision).
- **Use when**: Session end, or periodically when inbox has accumulated candidates.
```

**Step 2: Commit**

```bash
git add src/skills/AGENTS.md
git commit -m "docs: add memory-capture and memory-curator to skills registry"
```

---

## Task 6: Verify installation works

**Step 1: Test the installer copies new skills**

```bash
cd /tmp && mkdir test-memory-install && cd test-memory-install && git init
python ~/projects/claptrap/bootstrap/install.py
# Select OpenCode (option 1)
```

**Step 2: Verify skills were copied**

```bash
ls -la ~/.config/opencode/skills/memory-capture/
ls -la ~/.config/opencode/skills/memory-curator/
ls -la ~/.config/opencode/skills/claptrap-memory/
```

**Step 3: Verify memory files created**

```bash
ls -la .claptrap/
cat .claptrap/memory_inbox.md
cat .claptrap/memories.md
```

**Step 4: Cleanup**

```bash
cd ~ && rm -rf /tmp/test-memory-install
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Create memory-capture skill | `src/skills/memory-capture/SKILL.md` |
| 2 | Create memory-curator skill | `src/skills/memory-curator/SKILL.md` |
| 3 | Update claptrap-memory as meta-skill | `src/skills/claptrap-memory/SKILL.md` |
| 4 | Update design doc status | `docs/plans/2025-02-02-claptrap-memory-design.md` |
| 5 | Update skills registry | `src/skills/AGENTS.md` |
| 6 | Verify installation | (no file changes) |

**Total commits:** 5 (one per task except verification)
