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
