# Create OpenSpec Change Proposal

Generate all OpenSpec artifacts for a single change.

## Source Linking

Every generated artifact MUST start with:
```markdown
<!-- Source: .claptrap/designs/<feature-slug>/design.md -->
```

## Process

### 1. Create change directory

```bash
openspec new change <change-id>
```

If this fails, STOP and report the error.

### 2. Generate proposal.md

1. Run: `openspec instructions --change <change-id> --json proposal`
2. Write `openspec/changes/<change-id>/proposal.md`:
   - Start with source comment
   - Follow OpenSpec instruction structure
   - For multi-change plans, include:
     - Reference to sibling changes
     - Dependencies on other changes
     - Scope boundary (what this change covers)
3. Optional: `openspec validate --strict --no-interactive --type change <change-id>`

### 3. Alignment review — max 2 cycles

Spawn `alignment-reviewer` subagent (via `claptrap-spawn-subagent`) with:
- design.md
- proposal.md
- For multi-change: which portion this change covers

**If ALIGNED**: continue.

**If GAPS**:
1. Apply fixes to proposal.md
2. Re-run review
3. After 2 cycles with GAPS: summarize issues and STOP

### 4. Generate specs

Run: `openspec instructions --change <change-id> --json specs`

Follow the instructions to create `specs/**/spec.md` files.

### 5. Generate tasks

Run: `openspec instructions --change <change-id> --json tasks`

Follow the instructions to create `tasks.md`.

### 6. Feasibility review — max 2 cycles

Spawn `feasibility-reviewer` subagent with:
- proposal.md
- specs/**/spec.md (all)
- tasks.md
- design.md
- For multi-change: related proposals (dependencies)

**If FEASIBLE**: continue.

**If CONCERNS**:
1. Apply fixes to tasks.md (and specs/proposal if needed)
2. Re-run review
3. After 2 cycles with CONCERNS: summarize issues and STOP

## Output

All artifacts created under `openspec/changes/<change-id>/`:
- `proposal.md`
- `specs/**/spec.md`
- `tasks.md`
