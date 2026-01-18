---
name: memory
description: Read and write project memory files for decisions, patterns, and lessons.
---

# Memory Skill

## What this skill does
Provides a lightweight memory system that lets agents record and retrieve project context, decisions, patterns, anti-patterns, and lessons.

## When to activate
Trigger this skill when **you (the agent)** believe project memory should be **read, written, updated, or deleted**.

### Agent autonomy rules
- **Do not wait for the user to ask** to record or maintain memory. Decide proactively.
- **Be selective**: only write memory that is likely to be reused in future work (avoid transient notes).
- **Prefer update over duplication**: if a memory already exists, update it instead of writing a new, overlapping entry.
- **Prefer update over delete**: delete only when an entry is clearly incorrect, redundant, or harmful.
- **Never store secrets**: do not write API keys, tokens, credentials, private customer data, or copied logs that may contain sensitive information.

### Common activation signals (agent-observed)
- A **non-obvious decision** was made (trade-off, constraint, convention) that future work could accidentally undo.
- A **pattern** emerged that should be repeated (e.g., “how we structure prompts”, “how we name change IDs”).
- An **anti-pattern** caused avoidable pain and should be prevented going forward.
- A **lesson** was learned after implementing/reviewing/debugging a change.
- You need to **recall** prior choices (“what did we decide about X?”) to avoid re-litigating or conflicting guidance.

## Memory-read operation

**Inputs**
- `query` (string): what to search for
- `types` (optional list): `decision`, `pattern`, `anti-pattern`, `lesson`
- `tags` (optional list): tag filters
- `limit` (optional int, default 5): maximum results

**Behavior rules**
- Always include `.memory/project.md` in results.
- Match by title, tags, and content.
- Return most recent matches first.

## Memory-write operation

**Inputs**
- `type` (string): `decision`, `pattern`, `anti-pattern`, `lesson`
- `title` (string): descriptive name
- `context` (string): what prompted this
- `summary` (string): 2-3 sentences, standalone
- `details` (string): concise explanation
- `tags` (list): relevant tags
- `related` (optional string): change-id or design slug

**Behavior rules**
- Auto-generate filename as `YYYY-MM-DD-<slug>.md`.
- Place file in the matching subdirectory under `.workflow/memory/`.
- Validate that `details` does not exceed 150 words.
- Validate that `summary` can stand alone without `details`.

## Memory-update operation

Use this when an existing memory is **still the right topic** but the content is outdated, incomplete, or contradicted by a newer decision.

**Inputs**
- `path` (string): path to the existing `.workflow/memory` file to update
- `context` (string): what changed and why this update is needed
- `summary` (string): updated 2-3 sentence standalone summary
- `details` (string): updated details (still \<= 150 words)
- `tags` (list): updated tags (add/remove as needed)
- `related` (optional string): change-id or design slug

**Behavior rules**
- Keep the existing filename (do not “rename by date”).
- If the file has frontmatter, preserve `Date:` and add `Updated: YYYY-MM-DD` (or update it if it already exists).
- If the old content is now wrong, replace it (don’t append long “history” sections).
- Avoid making multiple near-duplicate memories; consolidate into the best single entry.

## Memory-delete operation

Use this only when a memory entry is clearly **incorrect**, **duplicative**, or **actively misleading**.

**Inputs**
- `path` (string): path to the `.workflow/memory` file to delete
- `reason` (string): brief explanation for why deletion is the right action

**Behavior rules**
- Prefer **update** if the memory is mostly correct but needs revision.
- Prefer **update + merge** if two memories overlap (choose the better entry to keep, delete the other).

## Conciseness rules
- Summary must be understandable without reading Details.
- Details must be 150 words or fewer.
- Prefer linking to deeper context instead of repeating it.

## Memory type reference
| Type | Folder | When to use |
| --- | --- | --- |
| decision | `.workflow/memory/decisions/` | Significant trade-offs or choices |
| pattern | `.workflow/memory/patterns/` | Approaches that worked well |
| anti-pattern | `.workflow/memory/anti-patterns/` | Approaches to avoid |
| lesson | `.workflow/memory/lessons/` | Post-change learnings |
