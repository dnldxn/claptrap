---
name: "claptrap:propose"
description: "Generate OpenSpec artifacts (proposal, specs, tasks) from a design document with alignment and feasibility review cycles."
model: claude-sonnet-4
models:
  cursor: anthropic/claude-sonnet-4
  github-copilot: claude-sonnet-4
  claude: sonnet
  opencode: anthropic/claude-sonnet-4
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# Command: /claptrap:propose

Convert an approved design document into a complete OpenSpec change with proposal, specs, and tasks. Includes automatic alignment and feasibility review cycles.

## Invocation Patterns

```bash
# Explicit path
/claptrap:propose .claptrap/designs/<slug>/design.md

# Auto-detect most recent design
/claptrap:propose
```

## Skills Required

Load the following skills:
- `claptrap:memory` — Read context, write decisions
- `claptrap:propose` — Extraction and transformation logic

## Workflow

### Step 1: Initialize

1. **Read memory context** via `claptrap:memory` skill
   - Read `.claptrap/memories.md` for prior decisions and patterns
   - Use context to inform artifact generation

2. **Determine design document path**:
   - If path argument provided: use it
   - If not: auto-detect most recent design by modified time in `.claptrap/designs/*/design.md`
   - If no designs found: report error and STOP

3. **Read and parse design.md**:
   - Read entire design document
   - Parse all sections and extract content

4. **Validate required sections exist**:
   - **Intent** (required) — What and why
   - **Scope** (required) — In/out of scope
   - **Acceptance Criteria** (required) — Testable conditions
   - **Architecture Overview** (recommended) — Components, structure
   - If required sections missing: report error and STOP

5. **Derive change name from design slug**:
   - Extract slug from design path: `.claptrap/designs/<slug>/design.md`
   - Use `<slug>` as the change name (kebab-case)

### Step 2: Create OpenSpec Change

1. **Run OpenSpec command**:
   ```bash
   openspec new change <change-name>
   ```
   - Creates `openspec/changes/<change-name>/` directory
   - Creates `.openspec.yaml` metadata file

2. **Verify creation**:
   - Confirm directory exists
   - If creation fails: report error and STOP

### Step 3: Generate proposal.md

1. **Get OpenSpec instructions**:
   ```bash
   openspec instructions proposal --change <change-name> --json
   ```
   - Receive template structure, dependencies, rules

2. **Map design sections to proposal**:
   
   | Design Section | Proposal Section | Transformation |
   |----------------|------------------|----------------|
   | Intent | Why | Direct copy or light summarization |
   | Scope.InScope | What Changes | Summarize to 2-3 sentences |
   | Goals (from Intent) | Capabilities.New | Extract as kebab-case slugs |
   | Scope.OutOfScope | Non-Goals | Direct copy (add to Impact section) |
   | Key Decisions | Impact.Key Decisions | Summarize each decision |
   | Architecture.Components | Impact.Code Changes | List affected areas |

3. **Add source link**:
   ```markdown
   <!-- Source: ../../.claptrap/designs/<slug>/design.md -->
   ```

4. **Write proposal.md**:
   - Write to: `openspec/changes/<change-name>/proposal.md`
   - Follow OpenSpec proposal template structure
   - Include all mapped sections

### Step 4: Alignment Review (Max 2 Cycles)

1. **Spawn alignment-reviewer subagent**:
   - **Input 1**: `.claptrap/designs/<slug>/design.md` (full path)
   - **Input 2**: `openspec/changes/<change-name>/proposal.md` (full path)
   - Request validation of alignment between design and proposal

2. **Process review result**:
   - **If ALIGNED**: Proceed to Step 5
   - **If GAPS**: Fix proposal.md to address gaps
     - Review each gap
     - Update proposal.md with corrections
     - Re-run alignment review
     - Maximum 2 review cycles (including initial)
     - If still GAPS after 2 cycles: report unresolved gaps, ask user to decide (fix manually or proceed anyway)

### Step 5: Generate specs/*.md

1. **Extract capabilities from proposal**:
   - Read `proposal.md` Capabilities.New section
   - Extract list of capability slugs

2. **For each capability**:

   a. **Get OpenSpec instructions**:
      ```bash
      openspec instructions specs --change <change-name> --json
      ```
      - Receive template structure, dependencies, rules

   b. **Map design sections to spec**:
      
      | Design Section | Spec Section | Transformation |
      |----------------|--------------|----------------|
      | Acceptance Criteria | Requirements | Each criterion → one requirement |
      | Acceptance Criteria | Scenarios | Convert "should X when Y" → WHEN Y / THEN X |
      | Key Decisions | Constraints | Add as scenario conditions |
      | Architecture.Types | References | Link to design for type definitions |

   c. **Create spec structure**:
      - Requirements: ADDED items (from acceptance criteria)
      - Scenarios: WHEN/THEN format (from acceptance criteria)
      - Constraints: From key decisions
      - References: Link back to design.md for types/architecture

   d. **Add source link**:
      ```markdown
      <!-- Source: ../../.claptrap/designs/<slug>/design.md -->
      ```

   e. **Write spec file**:
      - Write to: `openspec/changes/<change-name>/specs/<capability>/spec.md`
      - Create capability directory if needed
      - Follow OpenSpec spec template structure

3. **Repeat for all capabilities**

### Step 6: Feasibility Review (Max 2 Cycles)

1. **Spawn feasibility-reviewer subagent**:
   - **Input 1**: `openspec/changes/<change-name>/proposal.md`
   - **Input 2**: `openspec/changes/<change-name>/specs/*/spec.md` (all spec files)
   - **Input 3**: `openspec/changes/<change-name>/tasks.md` (when available after Step 7, or omit on first pass)
   - **Input 4**: `.claptrap/designs/<slug>/design.md` (for architecture context)
   - Request validation of implementation feasibility

2. **Process review result**:
   - **If FEASIBLE**: Proceed to Step 7
   - **If CONCERNS**: Refine specs or update proposal
     - Review each concern
     - Update specs/*.md or proposal.md with corrections
     - Re-run feasibility review
     - Maximum 2 review cycles (including initial)
     - If still CONCERNS after 2 cycles: report unresolved concerns, ask user to decide

### Step 7: Generate tasks.md

1. **Get OpenSpec instructions**:
   ```bash
   openspec instructions tasks --change <change-name> --json
   ```
   - Receive template structure, dependencies, rules

2. **Map design sections to tasks**:
   
   | Design Section | Tasks Section | Transformation |
   |----------------|---------------|----------------|
   | OpenSpec Proposals table | Task Groups | Each proposal row → one group |
   | Architecture.Components | Subtasks | Each component → implementation subtasks |
   | Architecture.Package Structure | File tasks | Each directory/file → creation task |
   | Acceptance Criteria | Verification tasks | Each criterion → verification subtask |

3. **Structure tasks by phases**:
   - Implementation tasks (by component)
   - Integration tasks
   - Verification tasks (from acceptance criteria)
   - Documentation tasks

4. **Add task dependencies**:
   - Order tasks based on Architecture.Data Flow
   - Mark dependencies explicitly
   - Respect component relationships

5. **Add source link**:
   ```markdown
   <!-- Source: ../../.claptrap/designs/<slug>/design.md -->
   ```

6. **Write tasks.md**:
   - Write to: `openspec/changes/<change-name>/tasks.md`
   - Follow OpenSpec tasks template structure
   - Use checkbox format for all tasks

### Step 8: Link and Finalize

1. **Update design.md with proposal link**:
   - Find or create `## OpenSpec Proposals` section
   - Add link: `- [<change-name>](../../openspec/changes/<change-name>/proposal.md)`
   - Preserve existing proposal links if any

2. **Write .source file in change directory**:
   - Write to: `openspec/changes/<change-name>/.source`
   - Content: relative path to design document
   - Example: `../../.claptrap/designs/<slug>/design.md`

3. **Write memory entries** via `claptrap:memory` skill:
   - Record significant decisions made during artifact generation
   - Record any important transformations or trade-offs
   - Be selective: only record what would help future agents

4. **Present summary to user**:
   ```markdown
   ## OpenSpec Artifacts Created
   
   **Change**: `<change-name>`
   
   **Artifacts**:
   - Proposal: `openspec/changes/<change-name>/proposal.md`
   - Specs: `openspec/changes/<change-name>/specs/*/spec.md` (<count> capabilities)
   - Tasks: `openspec/changes/<change-name>/tasks.md`
   
   **Source**: `.claptrap/designs/<slug>/design.md`
   
   **Reviews**:
   - Alignment: ALIGNED (X cycles)
   - Feasibility: FEASIBLE (Y cycles)
   
   **Next Steps**:
   1. Review artifacts for correctness
   2. Run `/claptrap:review` to validate against design
   3. Implement via `/opsx:apply`
   4. Verify via `/opsx:verify`
   5. Archive via `/opsx:archive`
   ```

## Error Handling

- **Missing design.md**: Report error, list available designs, STOP
- **Invalid design structure**: Report missing required sections, STOP
- **OpenSpec command fails**: Report error with command output, STOP
- **Review cycles exhausted**: Report unresolved issues, ask user to decide
- **File write errors**: Report error, suggest manual creation, STOP

## Key Principles

- **Bidirectional linking**: Every artifact links back to design.md
- **Source preservation**: Design.md is the source of truth, not OpenSpec's design artifact
- **Iterative refinement**: Up to 2 cycles per review type
- **Memory integration**: Read context at start, write decisions at end
- **Auto-detection**: Default to most recent design for convenience
- **Selective memory**: Only write memories that would help future agents

## User Arguments

**$ARGUMENTS**: Optional path to design document

- If provided: use as design path
- If empty: auto-detect most recent design
