# Claptrap Workflow Refactor - Implementation Plan

**Source**: @claptrap-workflow-proposal.md
**Date**: 2026-01-28

---

## Executive Summary

Refactor Claptrap to create a unified development pipeline with three commands:
- `/claptrap-brainstorm` → Produces comprehensive `design.md`
- `/claptrap-propose` → Extracts OpenSpec artifacts from design
- `/claptrap-review` → Validates artifacts against source design

Implementation uses native OpenSpec commands (`/opsx:apply`, `/opsx:verify`, `/opsx:archive`).

## Implementation Instructions
- "lines X-Y" refer to @claptrap-workflow-proposal.md .  Lookup the specific section for additional context.
- Invoke the `claptrap-memory` skill to read/write memories as instructed.
- When you are finished, commit your changes in git: `git commit -am "<MODEL> - <ITERATION NUMBER> -  <DESCRIPTIVE MESSAGE>"`

---

## Phase 1: Create New Components

### 1.1 Create claptrap-propose Command

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 1.1.1 | `src/commands/claptrap-propose.md` | §Component Specifications > Commands > /claptrap-propose (@claptrap-workflow-proposal.md: lines 918-940) |

**Technical Details:**

Create command file with YAML frontmatter:
```yaml
---
name: "claptrap-propose"
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
```

**Command workflow (from @claptrap-workflow-proposal.md: lines 926-936):**
1. Read memory context via `claptrap-memory` skill
2. Read and parse design.md, validating required sections exist:
   - Intent (required)
   - Scope (required)
   - Acceptance Criteria (required)
   - Architecture Overview (recommended)
3. Derive change name from design slug (kebab-case)
4. Run `openspec new <change-name>` to create change directory
5. Generate `proposal.md` using `openspec instructions proposal --json`
6. Spawn `alignment-reviewer` subagent, fix gaps (max 2 cycles)
7. Generate `specs/*.md` using `openspec instructions specs --json`
8. Spawn `feasibility-reviewer` subagent, fix concerns (max 2 cycles)
9. Generate `tasks.md` using `openspec instructions tasks --json`
10. Link artifacts to design.md:
    - Add source comment: `<!-- Source: ../../.claptrap/designs/<slug>/design.md -->`
    - Create `.source` file in change directory
    - Update design.md "OpenSpec Proposals" section
11. Write memory entries for significant decisions
12. Present summary with links to all artifacts

**Invocation patterns:**
- `/claptrap-propose .claptrap/designs/<slug>/design.md` (explicit path)
- `/claptrap-propose` (auto-detect most recent design by modified time)

---

### 1.2 Create claptrap-review Command

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 1.2.1 | `src/commands/claptrap-review.md` | §Component Specifications > Commands > /claptrap-review (@claptrap-workflow-proposal.md: lines 944-961) |

**Technical Details:**

Create command file with YAML frontmatter:
```yaml
---
name: "claptrap-review"
description: "Validate all OpenSpec artifacts against source design document using plan-reviewer agent."
model: claude-sonnet-4
models:
  cursor: anthropic/claude-sonnet-4
  github-copilot: claude-sonnet-4
  claude: sonnet
  opencode: anthropic/claude-sonnet-4
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---
```

**Command workflow (from @claptrap-workflow-proposal.md: lines 555-585):**
1. Accept change-id or auto-detect most recent change
2. Read `openspec/changes/<id>/.source` to find design.md path
3. Read all artifacts:
   - `design.md` (source)
   - `proposal.md`
   - `specs/*.md` (all capability specs)
   - `tasks.md`
4. Spawn `plan-reviewer` subagent with all artifacts
5. Output verdict:
   - `APPROVED` with validation summary
   - `REVISE` with prioritized issues (Critical → Important → Minor)
6. If REVISE, guide user through resolution options:
   - Fix now: return to `/claptrap-propose --regenerate`
   - Defer: document in tasks as future work
   - Accept risk: document in memory

**Invocation patterns:**
- `/claptrap-review <change-id>` (explicit change)
- `/claptrap-review` (auto-detect most recent change)

---

### 1.3 Create claptrap-propose Skill

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 1.3.1 | `src/skills/claptrap-propose/` | §File Structure > Source Structure (lines 1148-1153) |
| 1.3.2 | `src/skills/claptrap-propose/SKILL.md` | §Component Specifications > Skills > claptrap-propose-skill (@claptrap-workflow-proposal.md: lines 985-1003) |
| 1.3.3 | `src/skills/claptrap-propose/templates/` | §File Structure (@claptrap-workflow-proposal.md: lines 1150-1153) |
| 1.3.4 | `src/skills/claptrap-propose/templates/proposal-hints.md` | §Artifact Specifications > Proposal (@claptrap-workflow-proposal.md: lines 663-721) |
| 1.3.5 | `src/skills/claptrap-propose/templates/spec-hints.md` | §Artifact Specifications > Spec (@claptrap-workflow-proposal.md: lines 724-816) |
| 1.3.6 | `src/skills/claptrap-propose/templates/tasks-hints.md` | §Artifact Specifications > Tasks (@claptrap-workflow-proposal.md: lines 820-889) |

**Technical Details for SKILL.md:**

```yaml
---
name: "claptrap-propose"
description: "Design → OpenSpec artifact extraction with review cycles"
invoked_by: "/claptrap-propose command"
---
```

**Skill capabilities (from proposal lines 993-998):**
- Design document parsing and section extraction
- OpenSpec CLI integration (`openspec instructions`, `openspec new`)
- Section mapping and transformation logic
- Review agent spawning with 2-cycle iteration limits
- Artifact linking (bidirectional references)

**Technical Details for proposal-hints.md:**

Document the extraction rules from @claptrap-workflow-proposal.md: lines 711-720:

| Design Section | Proposal Section | Transformation |
|----------------|------------------|----------------|
| Intent | Why | Direct copy or light summarization |
| Scope.InScope | What Changes | Summarize to 2-3 sentences |
| Goals (from Intent) | Capabilities.New | Extract as kebab-case slugs |
| Scope.OutOfScope | Non-Goals | Direct copy |
| Key Decisions | Impact.Key Decisions | Summarize each decision |
| Architecture.Components | Impact.Code Changes | List affected areas |

Include proposal template structure from @claptrap-workflow-proposal.md: lines 670-709.

**Technical Details for spec-hints.md:**

Document the extraction rules from @claptrap-workflow-proposal.md: lines 774-781:
| Design Section | Spec Section | Transformation |
|----------------|--------------|----------------|
| Acceptance Criteria | Requirements | Each criterion → one requirement |
| Acceptance Criteria | Scenarios | Convert "should X when Y" → WHEN Y / THEN X |
| Key Decisions | Constraints | Add as scenario conditions |
| Architecture.Types | References | Link to design for type definitions |

Include spec template structure from @claptrap-workflow-proposal.md: lines 731-772.
Include example transformation from @claptrap-workflow-proposal.md: lines 783-816.

**Technical Details for tasks-hints.md:**

Document the extraction rules from @claptrap-workflow-proposal.md: lines 849-856:

| Design Section | Tasks Section | Transformation |
|----------------|---------------|----------------|
| OpenSpec Proposals table | Task Groups | Each proposal row → one group |
| Architecture.Components | Subtasks | Each component → implementation subtasks |
| Architecture.Package Structure | File tasks | Each directory/file → creation task |
| Acceptance Criteria | Verification tasks | Each criterion → verification subtask |

Include tasks template structure from @claptrap-workflow-proposal.md: lines 827-847.
Include example transformation from @claptrap-workflow-proposal.md: lines 858-889.

---

### 1.4 Update Design Template

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 1.4.1 | `src/designs/TEMPLATE.md` | §Detailed Flow Specification > Phase 1 > Output (@claptrap-workflow-proposal.md: lines 316-388) |

**Technical Details:**

Update template to include all sections from @claptrap-workflow-proposal.md: lines 319-388:
```markdown
<!-- Source: /claptrap-brainstorm -->
<!-- Naming: .claptrap/designs/<feature-slug>/design.md -->

# Design: <Feature Name>

Date: YYYY-MM-DD
Status: Draft | Review | Approved
Author: <Name>

## Intent
<What we are building and why it matters. 2-3 sentences.>

## Scope

### In Scope
- <Specific deliverable or capability>

### Out of Scope
- <Explicitly excluded item>

## Acceptance Criteria
- [ ] <Testable condition that maps to a spec scenario>
- [ ] <Another testable condition>

## Architecture Overview

### Components
- <Component>: <Responsibility>

### Package Structure
```
<directory tree if applicable>
```

### Core Types
```typescript
// Key interfaces and types
interface Example {
  field: string
}
```

### Data Flow
<Description or diagram reference>

## Key Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| <What> | <A, B, C> | <B> | <Why B was chosen> |

## Open Questions
- [ ] <Question to resolve before or during implementation>

## Next Steps
1. Review this design document
2. Run `/claptrap-propose` to generate OpenSpec artifacts
3. Review and approve proposal
4. Implement via `/opsx:apply`

## OpenSpec Proposals
<!-- Auto-populated by /claptrap-propose -->
- (none yet)
```

**Required sections** (from @claptrap-workflow-proposal.md: lines 636-644):
- Intent, Scope (In/Out), Acceptance Criteria, Architecture Overview, Key Decisions

**Optional sections** (from @claptrap-workflow-proposal.md: lines 646-653):
- Open Questions, Core Types, Data Flow, Package Structure

---

## Phase 2: Update Existing Components

### 2.1 Update claptrap-brainstorm Command

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.1.1 | `src/commands/claptrap-brainstorm.md` | §Component Specifications > Commands > /claptrap-brainstorm (@claptrap-workflow-proposal.md: lines 897-914) |

**Technical Details:**

Modify existing command to:
1. Remove any commented-out or legacy openspec-create-proposal invocations
2. Clarify output path: `.claptrap/designs/<feature-slug>/design.md`
3. Add explicit memory read step at start (from @claptrap-workflow-proposal.md: line 163)
4. Add memory write step at end for significant decisions (from @claptrap-workflow-proposal.md: line 167)
5. Update "Next Steps" output to reference `/claptrap-propose`

**Process steps from @claptrap-workflow-proposal.md: lines 274-312:**
- Step 1: Initialize (read memory, parse idea, determine if research needed)
- Step 2: Discovery Dialogue (3-5 questions, max 2 rounds)
- Step 3: Research (spawn research/explore subagents if needed)
- Step 4: Design Generation (section by section with user feedback)
- Step 5: Finalize (derive slug, create directory, write design.md, write memory)

---

### 2.2 Update claptrap-brainstorming Skill

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.2.1 | `src/skills/claptrap-brainstorming/SKILL.md` | §Component Specifications > Skills > claptrap-brainstorm-skill (@claptrap-workflow-proposal.md: lines 967-982) |
| 2.2.2 | `src/skills/claptrap-brainstorming/templates/design.md` | §Detailed Flow Specification > Phase 1 > Output (@claptrap-workflow-proposal.md: lines 316-388) |

**Technical Details for SKILL.md:**

Add explicit memory integration steps:
- **Step 0 (new)**: Read `.claptrap/memories.md` for prior decisions and patterns
- **Step 5 (update)**: Write memory entries for significant decisions

Update skill capabilities from @claptrap-workflow-proposal.md: lines 975-979:
- Clarifying question generation (3-5 questions, max 2 rounds)
- Section-by-section design presentation with user feedback
- Subagent spawning for research/exploration
- Memory read/write integration

**Technical Details for templates/design.md:**

Must exactly match structure in `src/designs/TEMPLATE.md` (Task 1.4.1).
Ensure all required and optional sections are present.

---

### 2.3 Update alignment-reviewer Agent

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.3.1 | `src/agents/alignment-reviewer.md` | §Component Specifications > Agents > alignment-reviewer (@claptrap-workflow-proposal.md: lines 1029-1042) |

**Technical Details:**

Update Subagent Interface section to require:
- **Input 1**: Source `design.md` (full path)
- **Input 2**: Generated `proposal.md` (full path)

Add validation checks:
- Proposal links back to design.md via source comment
- Intent → Why mapping is accurate and complete
- Scope.InScope → Capabilities mapping covers all items
- Scope.OutOfScope → Non-Goals includes all excluded items
- Key Decisions → Impact.Key Decisions summarizes each decision

Update output format from @claptrap-workflow-proposal.md: lines 1038-1039:
- `ALIGNED` (no issues found)
- `GAPS: 1. [Critical/Important/Minor] <specific issue description>`

---

### 2.4 Update feasibility-reviewer Agent

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.4.1 | `src/agents/feasibility-reviewer.md` | §Component Specifications > Agents > feasibility-reviewer (@claptrap-workflow-proposal.md: lines 1045-1059) |

**Technical Details:**

Update Subagent Interface section to require (from @claptrap-workflow-proposal.md: lines 1051-1055):
- **Input 1**: `proposal.md`
- **Input 2**: `specs/*.md` (all spec files)
- **Input 3**: `tasks.md`
- **Input 4**: `design.md` (for architecture context)

Add validation checks:
- Tasks cover all spec requirements
- Task dependencies align with Architecture.Components
- Task sequencing respects data flow from design
- Estimated complexity is realistic given architecture

Update output format from @claptrap-workflow-proposal.md: lines 1057:
- `FEASIBLE` (implementation is realistic)
- `CONCERNS: 1. [Critical/Important/Minor] <specific concern>`

---

### 2.5 Refactor plan-reviewer Agent

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.5.1 | `src/agents/plan-reviewer.md` | §Component Specifications > Agents > plan-reviewer (@claptrap-workflow-proposal.md: lines 1063-1087) |

**Technical Details:**

Update Subagent Interface section to require (from @claptrap-workflow-proposal.md: lines 1069-1073):
- **Input 1**: `design.md` (source)
- **Input 2**: `proposal.md`
- **Input 3**: `specs/*.md` (all spec files)
- **Input 4**: `tasks.md`

Implement 8-point validation checklist from @claptrap-workflow-proposal.md: lines 1077-1085:

1. **Proposal.Why ↔ Design.Intent**: Motivation text aligns
2. **Proposal.Capabilities ↔ Design.Scope.InScope**: All in-scope items have corresponding capabilities
3. **Proposal.Impact ↔ Design.Key Decisions**: Each decision is summarized in impact
4. **Specs ↔ Design.Acceptance Criteria**: Every criterion has a corresponding requirement/scenario
5. **Specs scenarios format**: All scenarios use WHEN/THEN format
6. **Tasks ↔ Specs**: Every spec requirement has implementation tasks
7. **Task sequencing**: Dependencies are correctly ordered (no task depends on a later task)
8. **No orphans**: No unreferenced items in any artifact

Update output format from @claptrap-workflow-proposal.md: lines 1075:
- `APPROVED: <summary of what was validated>`
- `REVISE: <prioritized issues list>`

Output structure for REVISE from @claptrap-workflow-proposal.md: lines 608-623:
```markdown
## Review Result: REVISE

### Critical Issues (must fix)
1. **<Issue title>**: <Description with specific artifact references>

### Important Issues (should fix)
2. **<Issue title>**: <Description>

### Minor Issues (consider fixing)
3. **<Issue title>**: <Description>

### Recommended Actions
1. <Specific action to take>
```

---

### 2.6 Update Example Design

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 2.6.1 | `src/designs/example-feature/design.md` | §Artifact Specifications > Design Document (@claptrap-workflow-proposal.md: lines 627-660) |
**Technical Details:**

Update example to demonstrate all sections:
- Add `Core Types` section with example TypeScript interface
- Add `Package Structure` section with directory tree
- Update `Key Decisions` to use full table format (Decision | Options | Choice | Rationale)
- Update `Next Steps` to reference `/claptrap-propose`
- Add `OpenSpec Proposals` section with placeholder

---

## Phase 3: Remove Deprecated Components

### 3.1 Remove Commands

| Task ID | File to Delete | Reason | Proposal Reference |
|---------|----------------|--------|-------------------|
| 3.1.1 | `src/commands/propose.md` | Replaced by `claptrap-propose` | §Current State Analysis > Components to Refactor (@claptrap-workflow-proposal.md: line 140) |
| 3.1.2 | `src/commands/implement-change.md` | Use native `/opsx:apply` | §Current State Analysis > Components to Remove (@claptrap-workflow-proposal.md: line 148) |
| 3.1.3 | `src/commands/archive-change.md` | Use native `/opsx:archive` | §Current State Analysis > Components to Remove (@claptrap-workflow-proposal.md: line 149) |
| 3.1.4 | `src/commands/finish-openspec-change.md` | Use native `/opsx:archive` | §Current State Analysis > Components to Remove (@claptrap-workflow-proposal.md: line 150) |

**Technical Details:**

For each file:
1. `git rm <file>` to remove and stage deletion
2. Verify no other files reference the deleted command
3. Update any imports or references in documentation

---

### 3.2 Remove Skills

| Task ID | Directory to Delete | Reason | Proposal Reference |
|---------|---------------------|--------|-------------------|
| 3.2.1 | `src/skills/design-to-proposal/` | Merged into `claptrap-propose` | §Migration Plan > Phase 3 (@claptrap-workflow-proposal.md: line 1232) |
| 3.2.2 | `src/skills/claptrap-openspec-proposal/` | Merged into `claptrap-propose` | §Migration Plan > Phase 3 (@claptrap-workflow-proposal.md: line 1233) |
| 3.2.3 | `src/skills/claptrap-opecspec-design/` | Empty stub (typo in name, no implementation) | Codebase exploration finding |

**Technical Details:**

For each directory:
1. `git rm -r <directory>` to remove entire directory and stage deletion
2. Verify no other files reference the deleted skill
3. Check for any templates or assets that should be preserved before deletion

**Files to delete in 3.2.1:**
- `src/skills/design-to-proposal/SKILL.md`
- `src/skills/design-to-proposal/review-alignment.md`
- `src/skills/design-to-proposal/review-feasibility.md`

**Files to delete in 3.2.2:**
- `src/skills/claptrap-openspec-proposal/SKILL.md`
- `src/skills/claptrap-openspec-proposal/templates/proposal.md`

**Files to delete in 3.2.3:**
- `src/skills/claptrap-opecspec-design/SKILL.md` (empty)
- `src/skills/claptrap-opecspec-design/templates/design.md`

---

## Phase 4: Update Documentation

### 4.1 Update Commands Registry

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 4.1.1 | `src/commands/AGENTS.md` | §File Structure > Source Structure (@claptrap-workflow-proposal.md: lines 1135-1140) |

**Technical Details:**

Update command registry table to list only 4 commands:

```markdown
## Available Commands

| Command | Purpose | Invocation |
|---------|---------|------------|
| `claptrap-brainstorm` | Turn ideas into comprehensive designs through collaborative dialogue | `/claptrap-brainstorm "<idea>"` |
| `claptrap-propose` | Generate OpenSpec artifacts from design with review cycles | `/claptrap-propose [design-path]` |
| `claptrap-review` | Validate artifacts against source design | `/claptrap-review [change-id]` |
| `claptrap-refactor` | Refactor code while preserving behavior | `/claptrap-refactor` |
```

Remove entries for: `propose`, `implement-change`, `archive-change`, `finish-openspec-change`

---

### 4.2 Update Skills Registry

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 4.2.1 | `src/skills/AGENTS.md` | §File Structure > Source Structure (@claptrap-workflow-proposal.md: lines 1142-1159) |

**Technical Details:**

Add new entry for `claptrap-propose`:
```markdown
### `claptrap-propose`
- **Path**: `skills/claptrap-propose/SKILL.md`
- **Purpose**: Extract OpenSpec artifacts from design documents with alignment and feasibility review.
- **Use when**: You have an approved design.md and want to generate proposal, specs, and tasks.
- **Templates**: `proposal-hints.md`, `spec-hints.md`, `tasks-hints.md`
```

Update `claptrap-brainstorming` description to mention memory integration.

Remove entries for: `design-to-proposal`, `claptrap-openspec-proposal`, `claptrap-opecspec-design`

---

### 4.3 Update Agents Registry

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 4.3.1 | `src/agents/AGENTS.md` | §Component Specifications > Agents (@claptrap-workflow-proposal.md: lines 1027-1087) |

**Technical Details:**

Update Agent Spawning Map:

```markdown
## Agent Spawning Map

| Agent | Spawned By | Purpose |
|-------|------------|---------|
| `alignment-reviewer.md` | `/claptrap-propose` | Validate proposal against design |
| `feasibility-reviewer.md` | `/claptrap-propose` | Validate specs/tasks for realism |
| `plan-reviewer.md` | `/claptrap-review` | Comprehensive artifact validation |
| `code-reviewer.md` | `/opsx:apply` (native) | Review code changes |
| `research.md` | `/claptrap-brainstorm`, `/claptrap-propose` | External research |
| `ui-designer.md` | `/claptrap-brainstorm` | UI design assistance |
```

Update agent descriptions to reflect new inputs and outputs per Phase 2 changes.

Remove references to `/propose`, `/implement-change`, `/archive-change`.

---

### 4.4 Update Main AGENTS.md

| Task ID | File | Proposal Reference |
|---------|------|-------------------|
| 4.4.1 | `src/AGENTS.md` | §Proposed Architecture (@claptrap-workflow-proposal.md: lines 154-250) |

**Technical Details:**

Update workflow overview to reflect new three-phase flow:
1. `/claptrap-brainstorm` → `design.md`
2. `/claptrap-propose` → OpenSpec artifacts
3. `/claptrap-review` → Validation
4. `/opsx:apply` → Implementation (native OpenSpec)

Include high-level flow diagram from @claptrap-workflow-proposal.md lines 158-218.
Include component relationship diagram from @claptrap-workflow-proposal.md lines 222-250.

---

## Phase 5: Testing and Verification

### 5.1 Structure Validation

| Task ID | Action | Proposal Reference |
|---------|--------|-------------------|
| 5.1.1 | Validate all new `.md` files have valid YAML frontmatter | §Component Specifications (@claptrap-workflow-proposal.md: lines 893-1024) |
| 5.1.2 | Verify all skill directories contain `SKILL.md` | §File Structure (@claptrap-workflow-proposal.md: lines 1142-1159) |
| 5.1.3 | Confirm all referenced templates exist in correct locations | §File Structure (@claptrap-workflow-proposal.md: lines 1148-1153) |

**Verification commands:**
```bash
# Check YAML frontmatter syntax
for f in src/commands/*.md src/skills/*/SKILL.md; do
  head -20 "$f" | grep -q "^---" && echo "OK: $f" || echo "MISSING FRONTMATTER: $f"
done

# Check skill directories have SKILL.md
for d in src/skills/*/; do
  [ -f "${d}SKILL.md" ] && echo "OK: $d" || echo "MISSING SKILL.md: $d"
done
```

---

### 5.2 Cross-Reference Validation

| Task ID | Action | Proposal Reference |
|---------|--------|-------------------|
| 5.2.1 | Verify command → skill references resolve | §Component Specifications (@claptrap-workflow-proposal.md: lines 893-1024) |
| 5.2.2 | Verify skill → agent references resolve | §Component Specifications (@claptrap-workflow-proposal.md: lines 1027-1087) |
| 5.2.3 | Verify template paths in skills resolve | §File Structure (@claptrap-workflow-proposal.md: lines 1148-1153) |
| 5.2.4 | Confirm no references to removed components | §Migration Plan > Phase 3 (@claptrap-workflow-proposal.md: lines 1226-1233) |

**Verification approach:**
1. Search all `.md` files for references to deleted commands/skills
2. Grep for `propose.md`, `implement-change`, `archive-change`, `design-to-proposal`, `openspec-proposal`
3. Fix any stale references found

---

### 5.3 End-to-End Smoke Test

| Task ID | Action | Expected Result | Proposal Reference |
|---------|--------|-----------------|-------------------|
| 5.3.1 | Run `/claptrap-brainstorm "Test feature for workflow validation"` | Dialogue starts, questions asked | §Detailed Flow Specification > Phase 1 (@claptrap-workflow-proposal.md: lines 256-312) |
| 5.3.2 | Complete brainstorm dialogue | `design.md` created at `.claptrap/designs/test-feature/design.md` | §Detailed Flow Specification > Phase 1 > Output (@claptrap-workflow-proposal.md: lines 314-388) |
| 5.3.3 | Run `/claptrap-propose` | OpenSpec artifacts generated | §Detailed Flow Specification > Phase 2 (@claptrap-workflow-proposal.md: lines 403-508) |
| 5.3.4 | Verify artifact structure | `openspec/changes/<name>/` contains proposal.md, specs/, tasks.md | §Detailed Flow Specification > Phase 2 > Outputs (@claptrap-workflow-proposal.md: lines 510-531) |
| 5.3.5 | Verify source links | All artifacts have `<!-- Source: ... -->` comment | §Artifact Specifications (@claptrap-workflow-proposal.md: lines 627-889) |
| 5.3.6 | Run `/claptrap-review` | Review completes with verdict | §Detailed Flow Specification > Phase 3 (@claptrap-workflow-proposal.md: lines 535-623) |
| 5.3.7 | Verify review output | APPROVED or REVISE with actionable issues | §Detailed Flow Specification > Phase 3 > Output (lines 587-623) |

---

### 5.4 Edge Case Testing

| Task ID | Action | Expected Behavior | Proposal Reference |
|---------|--------|-------------------|-------------------|
| 5.4.1 | `/claptrap-propose` with no argument | Auto-detect most recent design by modified time | §Component Specifications (@claptrap-workflow-proposal.md: line 924) |
| 5.4.2 | `/claptrap-review` with no argument | Auto-detect most recent change | §Component Specifications (@claptrap-workflow-proposal.md: line 950) |
| 5.4.3 | Design with missing optional sections | Proceed with warning, use available sections | §Artifact Specifications (@claptrap-workflow-proposal.md: lines 646-653) |
| 5.4.4 | Alignment review returns GAPS | Fix cycle runs, max 2 iterations | §Detailed Flow Specification (@claptrap-workflow-proposal.md: lines 453-462) |
| 5.4.5 | Feasibility review returns CONCERNS | Fix cycle runs, max 2 iterations | §Detailed Flow Specification (@claptrap-workflow-proposal.md: lines 476-486) |

---

## Critical Files

Priority order for implementation (highest impact first):

1. **`src/skills/claptrap-propose/SKILL.md`** - Core extraction logic, most complex new component
   - Proposal ref: §Component Specifications > Skills > claptrap-propose-skill (@claptrap-workflow-proposal.md: lines 985-1003)

2. **`src/commands/claptrap-propose.md`** - Primary workflow entry, orchestrates the skill
   - Proposal ref: §Component Specifications > Commands > /claptrap-propose (@claptrap-workflow-proposal.md: lines 918-940)

3. **`src/designs/TEMPLATE.md`** - Foundation template, all designs must follow this structure
   - Proposal ref: §Artifact Specifications > Design Document (@claptrap-workflow-proposal.md: lines 627-660)

4. **`src/agents/plan-reviewer.md`** - Critical for /claptrap-review, comprehensive validation logic
   - Proposal ref: §Component Specifications > Agents > plan-reviewer (@claptrap-workflow-proposal.md: lines 1063-1087)

5. **`src/skills/claptrap-brainstorming/templates/design.md`** - Must match TEMPLATE.md structure
   - Proposal ref: §Detailed Flow Specification > Phase 1 > Output (@claptrap-workflow-proposal.md: lines 316-388)

---

## Task Execution Order

```
Phase 0: 0.1 → 0.2 → 0.3

Phase 1: 1.3.1 → 1.3.2 → 1.3.3 → 1.3.4 → 1.3.5 → 1.3.6 → 1.4.1 → 1.1.1 → 1.2.1
         (skill dir → SKILL.md → templates dir → hints files → design template → commands)

Phase 2: 2.2.2 → 2.2.1 → 2.1.1 → 2.3.1 → 2.4.1 → 2.5.1 → 2.6.1
         (template first → skill → command → agents → example)

Phase 3: 3.1.1 → 3.1.2 → 3.1.3 → 3.1.4 → 3.2.1 → 3.2.2 → 3.2.3
         (commands first → skills)

Phase 4: 4.1.1 → 4.2.1 → 4.3.1 → 4.4.1
         (registries in order)

Phase 5: 5.1.* → 5.2.* → 5.3.* → 5.4.*
         (validation → smoke test → edge cases)
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| New files to create | 9 |
| Existing files to update | 10 |
| Files to delete | 10 |
| Documentation files to update | 4 |
| Total tasks | 38 |
