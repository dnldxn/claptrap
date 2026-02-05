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
