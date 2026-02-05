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
