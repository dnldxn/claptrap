---
name: "claptrap-propose"
description: "Create OpenSpec artifacts from Design Document with alignment + feasibility review cycles."
---

# Create OpenSpec Artifacts from Design Document

## Overview

Convert an approved design document into OpenSpec artifacts:
- `proposal.md`
- `specs/**/spec.md`
- `tasks.md`

This skill MUST:
- Use OpenSpec CLI for artifact instructions (`openspec instructions ... --json`).
- Preserve a source link back to the design doc in every generated artifact.
- Run alignment and feasibility reviews (bounded to 2 cycles each).

This skill MUST NOT:
- Implement code changes.
- Replace OpenSpec generation logic with custom schemas.

## Inputs

- Design document path (optional):
  - Preferred: `.claptrap/designs/<feature-slug>/design.md`
  - If missing: auto-detect most recent `design.md` under `.claptrap/designs/**/design.md` by modified time.
- Optional flags (parse from `$ARGUMENTS`):
  - `--regenerate proposal|specs|tasks|all`
  - `--change <change-id>` (REQUIRED when using `--regenerate`)

## Required Dependencies

- OpenSpec CLI must be available in PATH (`openspec --version` must work).
- Project must have been initialized with OpenSpec (`openspec/config.yaml` exists).

If either requirement is missing:
1. Print the exact shell commands the user must run to fix it.
2. Ask the user to run them and paste the output.
3. STOP.

## File Paths (source linking rules)

Assume the design is at:
`DESIGN_PATH = .claptrap/designs/<feature-slug>/design.md`

When writing OpenSpec artifacts under:
`openspec/changes/<change-id>/`

Use these rules:
1. Every generated artifact file MUST start with:
   `<!-- Source: .claptrap/designs/<feature-slug>/design.md -->`
2. Update the design doc `## OpenSpec Proposals` list with:
   `- [<change-id>](openspec/changes/<change-id>/proposal.md)`

## Process

### Step 0: Load Context

- Invoke the `claptrap-memory` skill to read and/or write memories as instructed.

### Step 1: Resolve design path

1. If `$ARGUMENTS` includes a `.md` path, treat it as the design path.
2. Else, auto-detect the most recent design by modified time:
   - Search for `.claptrap/designs/**/design.md`
   - Pick the newest by mtime
3. If no design is found, ask the user to run `/claptrap-brainstorm` first and STOP.

### Step 2: Resolve change-id

1. Let `<feature-slug>` be the parent directory name of the design path (kebab-case).
2. Default `<change-id>` to `<feature-slug>`.
3. If `$ARGUMENTS` includes `--change <change-id>`, use that change-id instead.

### Step 3: Create or reuse the OpenSpec change directory

**Case A — normal run (no `--regenerate`):**
1. Run: `openspec new change <change-id>`
2. If this fails, STOP and report the error.

**Case B — regeneration run (`--regenerate ...`):**
1. Require `--change <change-id>` to be present.
2. Confirm `openspec/changes/<change-id>/` exists.
3. If it does not exist, STOP and tell the user to run normal `/claptrap-propose` first.

### Step 4: Generate proposal.md

1. Run `openspec instructions --change <change-id> --json proposal` and follow the instructions.
2. Write `openspec/changes/<change-id>/proposal.md`:
   - Start with the source comment (see "File Paths" rules above).
   - Follow the OpenSpec instruction structure.
3. OPTIONAL but recommended: run `openspec validate --strict --no-interactive --type change <change-id>` and fix any errors.

### Step 5: Alignment review (design <-> proposal) — max 2 cycles

1. Spawn the `alignment-reviewer` subagent (via the `claptrap-spawn-subagent` skill) with:
   - design.md (source)
   - proposal.md (generated)
2. If output is `ALIGNED`, continue.
3. If output is `GAPS`:
   - Apply the suggested fixes to proposal.md.
   - Re-run alignment review.
4. Stop after 2 total cycles. If still `GAPS`, summarize remaining issues and STOP.

### Step 6: Generate specs/**/spec.md

Run `openspec instructions --change <change-id> --json specs` and follow the instructions.

### Step 7: Generate tasks.md

Run `openspec instructions --change <change-id> --json tasks` and follow the instructions.

### Step 8: Feasibility review (proposal + specs + tasks + design) — max 2 cycles
1. Spawn the `feasibility-reviewer` subagent with:
   - proposal.md
   - specs/**/spec.md (all)
   - tasks.md
   - design.md
2. If output is `FEASIBLE`, continue.
3. If output is `CONCERNS`:
   - Apply the suggested fixes to tasks.md (and specs/proposal if required).
   - Re-run feasibility review.
4. Stop after 2 total cycles. If still `CONCERNS`, summarize remaining issues and STOP.

### Step 9: Link and finalize

1. Update the design doc:
   - Ensure it has `## OpenSpec Proposals`
   - Add the proposal link entry for `<change-id>`
2. Print a short summary with links to:
   - design.md
   - proposal.md
   - specs/
   - tasks.md

## Regeneration Behavior

If user runs `/claptrap-propose --regenerate <artifact>`:
- Only overwrite the requested artifact(s).
- Do NOT create a new change directory.
