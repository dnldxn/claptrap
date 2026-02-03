---
name: "claptrap-propose"
description: "Create OpenSpec artifacts from Design Document with alignment + feasibility review cycles. Analyzes scope and can split large designs into multiple sequential or parallel changes."
---

# Create OpenSpec Artifacts from Design Document

Convert an approved design document into OpenSpec artifacts (`proposal.md`, `specs/**/spec.md`, `tasks.md`).

## Inputs

- Design document path (optional): defaults to most recent `.claptrap/designs/**/design.md`

## Process

### Step 1: Load context

Invoke `claptrap-memory` skill to read/write memories as instructed.

### Step 2: Resolve design path

1. If `$ARGUMENTS` includes a `.md` path, use it.
2. Else, find most recent `.claptrap/designs/**/design.md` by mtime and suggest it.
3. If none found, ask user to run `/claptrap-brainstorm` first and STOP.

### Step 3: Analyze scope and plan changes

Follow [decompose-plan.md](decompose-plan.md) to:
- Analyze the design scope
- Determine if single or multiple changes are appropriate
- Get user approval on the change plan

Output: ordered list of `{ change_id, description, dependencies }`.

### Step 4: Generate artifacts for each change

If subagents are available, spawn one for each change proposal that will follow [create-change-proposal.md](create-change-proposal.md) to generate all artifacts, passing in the necessaary design context and change details.  If subagents are not available, process each change sequentially within this context.

### Step 5: Finalize

1. Update design doc with `## OpenSpec Proposals` section listing all changes:
   ```markdown
   ## OpenSpec Proposals
   - [change-id-1](openspec/changes/change-id-1/proposal.md)
   - [change-id-2](openspec/changes/change-id-2/proposal.md)
   ```

2. Print summary:
   ```
   ## Summary

   Design: .claptrap/designs/<feature-slug>/design.md
   Generated N change(s):

   | # | Change ID | Status |
   |---|-----------|--------|
   | 1 | change-id-1 | Ready |
   | 2 | change-id-2 | Ready |

   ## Recommended Implementation Order
   1. **change-id-1** — No dependencies
   2. **change-id-2** — Depends on #1

   Start with: `/opsx:apply change-id-1`
   ```
