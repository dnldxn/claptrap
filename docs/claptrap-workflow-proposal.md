# Claptrap Workflow Refactor Proposal

**Date:** 2026-01-28
**Status:** Draft
**Author:** Claude (with user direction)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Requirements](#requirements)
3. [Background & Context](#background--context)
4. [Current State Analysis](#current-state-analysis)
5. [Proposed Architecture](#proposed-architecture)
6. [Detailed Flow Specification](#detailed-flow-specification)
7. [Artifact Specifications](#artifact-specifications)
8. [Component Specifications](#component-specifications)
9. [Integration with OpenSpec](#integration-with-openspec)
10. [File Structure](#file-structure)
11. [Migration Plan](#migration-plan)
12. [Risks, Concerns & Mitigations](#risks-concerns--mitigations)
13. [Open Questions Resolved](#open-questions-resolved)
14. [Final Summary](#final-summary)

---

## Executive Summary

This proposal refactors the Claptrap workflow to create a unified, modular development pipeline where:

- **`/claptrap-brainstorm`** is the front-door entry point for all feature work
- **Brainstorm output** (`design.md`) is the comprehensive source of truth
- **OpenSpec artifacts** are generated views extracted from the design, optimized for tracking and validation
- **Skills are modular** and can be composed, added, or removed independently
- **The workflow is environment-agnostic**, working across Cursor, VS Code, OpenCode CLI, and Codex
- **The memory system is preserved** and integrated at key workflow points

The core insight is that the brainstorm `design.md` contains more detail than OpenSpec artifacts individually. Rather than replacing this detail, we **extract** OpenSpec-compatible artifacts from it while preserving the original as the authoritative source for implementation.

---

## Requirements

### Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | `/claptrap-brainstorm` must be the primary entry point for all feature development workflows | User input |
| FR-2 | Brainstorm must produce a comprehensive technical design document with architecture, code snippets, key decisions, and acceptance criteria | Example: `design.md` |
| FR-3 | Brainstorm output must be compatible with and feed into the OpenSpec workflow | User input |
| FR-4 | The workflow must generate OpenSpec-compatible artifacts: proposal.md, specs/*.md, tasks.md | User input |
| FR-5 | All technical details from brainstorm must be preserved and accessible during implementation | User input |
| FR-6 | A plan review step must validate proposal, specs, and tasks before implementation | User input |
| FR-7 | Steps must be executable individually (step-by-step) with future subagent automation possible | User input |
| FR-8 | The existing memory system must be preserved and integrated | User input |
| FR-9 | Generated artifacts must link back to source design document | User input |
| FR-10 | Implementation phase is separate and out of scope for this proposal | User input |

### Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-1 | **Simple**: Minimize complexity, moving parts, dependencies, and abstractions | GOALS.md |
| NFR-2 | **Provider/Model Agnostic**: Work with multiple AI providers through subscription plans | GOALS.md |
| NFR-3 | **Environment Agnostic**: Run in Cursor, VS Code, OpenCode CLI, Codex, and other environments | GOALS.md |
| NFR-4 | **Easy to Install**: Install in under 5 minutes with sensible defaults | GOALS.md |
| NFR-5 | **Modular**: Skills are focused, self-contained, with minimal dependencies | GOALS.md |
| NFR-6 | **Maintainable**: Version pinning, documented upgrades, minimal complexity | GOALS.md |
| NFR-7 | **Built on Popular OSS**: Leverage OpenSpec as the foundation | GOALS.md |
| NFR-8 | **Scalable**: Handle small projects through large projects with hundreds of files | User input |

### Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| C-1 | Must use OpenSpec CLI for artifact instructions, not duplicate generation logic | Maintainability - OpenSpec updates flow through |
| C-2 | Skills must be markdown-based playbooks, not code | Environment agnosticism |
| C-3 | No per-request API billing dependencies | GOALS.md - subscription model only |
| C-4 | Memory entries must follow existing format (type, date, tags) | Preserve existing system |

---

## Background & Context

### Key Insights from Research

#### OpenSpec Architecture
- **Artifact DAG**: `proposal → specs → design → tasks` (design is conditional/optional)
- **Commands**: `/opsx:new`, `/opsx:continue`, `/opsx:ff`, `/opsx:apply`, `/opsx:verify`, `/opsx:archive`
- **Schema-driven**: Artifacts have dependencies enforced by schema
- **CLI provides instructions**: `openspec instructions <artifact>` returns schema-aware generation prompts
- **Verification**: Three dimensions - completeness, correctness, coherence

#### Current Claptrap Architecture
- **Commands**: `claptrap-brainstorm`, `propose`, `implement-change`, `archive-change`, `claptrap-refactor`
- **Skills**: `claptrap-memory`, `claptrap-brainstorming`, `design-to-proposal`, `claptrap-spawn-subagent`
- **Agents**: alignment-reviewer, feasibility-reviewer, code-reviewer, plan-reviewer, research, ui-designer
- **Flow**: brainstorm → design.md → propose (with reviews) → implement → archive

#### The Design Document Gap

**OpenSpec's design.md** (optional artifact):
- Created AFTER specs
- Contains technical decisions
- Relatively brief

**Claptrap's brainstorm design.md** (from examples):
- Created FIRST through dialogue
- Contains comprehensive architecture with code snippets
- Contains TypeScript interfaces and package structure
- Contains phased implementation plan
- Much more detailed than any single OpenSpec artifact

**Resolution**: Claptrap's design.md is the **comprehensive source document**. OpenSpec artifacts are **extracted views** from it. OpenSpec's optional design.md artifact is skipped as redundant.

---

## Current State Analysis

### Existing Components to Preserve

| Component | Location | Status |
|-----------|----------|--------|
| Memory skill | `src/skills/claptrap-memory/` | Keep unchanged |
| Spawn-subagent skill | `src/skills/claptrap-spawn-subagent/` | Keep unchanged |
| Alignment reviewer | `src/agents/alignment-reviewer.md` | Keep, minor updates |
| Feasibility reviewer | `src/agents/feasibility-reviewer.md` | Keep, minor updates |
| Plan reviewer | `src/agents/plan-reviewer.md` | Keep, refocus for new flow |
| Research agent | `src/agents/research.md` | Keep unchanged |
| UI designer agent | `src/agents/ui-designer.md` | Keep unchanged |
| Code reviewer | `src/agents/code-reviewer.md` | Keep unchanged |

### Components to Refactor

| Component | Current | Proposed Change |
|-----------|---------|-----------------|
| `claptrap-brainstorm` command | Produces design.md | Refactor to use updated template |
| `claptrap-brainstorming` skill | Dialogue + design output | Update template, add memory integration |
| `propose` command | Calls design-to-proposal skill | Replace with `claptrap-propose` |
| `design-to-proposal` skill | Complex multi-artifact generation | Replace with `claptrap-propose` skill |
| `claptrap-openspec-proposal` skill | Standalone proposal creation | Merge into `claptrap-propose` |

### Components to Remove

| Component | Reason |
|-----------|--------|
| `implement-change` command | Use native `/opsx:apply` |
| `archive-change` command | Use native `/opsx:archive` |
| `finish-openspec-change` command | Use native `/opsx:archive` |

---

## Proposed Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: BRAINSTORM (Discovery & Design)                                   │
│                                                                             │
│  /claptrap-brainstorm "Add user authentication"                             │
│  ├── Read memory context                                                    │
│  ├── Dialogue: Ask clarifying questions                                     │
│  ├── Spawn research subagent (if needed)                                    │
│  ├── Spawn explore subagent (if needed)                                     │
│  ├── Present design in validated sections                                   │
│  ├── Write memory (significant decisions)                                   │
│  └── Output: .claptrap/designs/<slug>/design.md                             │
│                                                                             │
│  USER CHECKPOINT: Review design, request changes, or approve                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: PROPOSE (Artifact Generation & Review)                            │
│                                                                             │
│  /claptrap-propose [design-path]                                            │
│  ├── Read memory context                                                    │
│  ├── Read design.md                                                         │
│  ├── Initialize OpenSpec change (openspec new <name>)                       │
│  ├── Generate proposal.md (using openspec instructions)                     │
│  ├── Spawn alignment-reviewer → fix gaps (max 2 cycles)                     │
│  ├── Generate specs/*.md (using openspec instructions)                      │
│  ├── Spawn feasibility-reviewer → fix concerns (max 2 cycles)               │
│  ├── Generate tasks.md (using openspec instructions)                        │
│  ├── Link artifacts to design.md                                            │
│  ├── Write memory (decisions, patterns)                                     │
│  └── Output: openspec/changes/<id>/{proposal.md, specs/*, tasks.md}         │
│                                                                             │
│  USER CHECKPOINT: Review artifacts, request changes, or approve             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: REVIEW (Optional Explicit Validation)                             │
│                                                                             │
│  /claptrap-review [change-id]                                               │
│  ├── Read all artifacts                                                     │
│  ├── Read source design.md                                                  │
│  ├── Spawn plan-reviewer                                                    │
│  ├── Validate: proposal ↔ design alignment                                  │
│  ├── Validate: specs ↔ design acceptance criteria                           │
│  ├── Validate: tasks ↔ specs coverage                                       │
│  └── Output: APPROVED or REVISE with prioritized issues                     │
│                                                                             │
│  USER CHECKPOINT: Address issues or proceed to implementation               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: IMPLEMENTATION (Native OpenSpec - Out of Scope)                   │
│                                                                             │
│  /opsx:apply                                                                │
│  /opsx:verify                                                               │
│  /opsx:archive                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  COMMANDS (User-facing entry points)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  /claptrap-brainstorm    /claptrap-propose    /claptrap-review              │
│         │                       │                    │                      │
│         │ invokes               │ invokes            │ invokes              │
│         ▼                       ▼                    ▼                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  SKILLS (Reusable playbooks)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  claptrap-brainstorm-skill     claptrap-propose-skill                       │
│  claptrap-memory               claptrap-spawn-subagent                      │
│         │                             │                                     │
│         │ spawns                      │ spawns                              │
│         ▼                             ▼                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  AGENTS (Specialized subagents)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  research          alignment-reviewer       feasibility-reviewer            │
│  ui-designer       plan-reviewer            code-reviewer                   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  EXTERNAL: OpenSpec CLI                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  openspec new         openspec instructions        openspec status          │
│  openspec apply       openspec verify              openspec archive         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Flow Specification

### Phase 1: `/claptrap-brainstorm`

#### Trigger
```
/claptrap-brainstorm "Add user authentication with OAuth support"
```

#### Inputs
| Input | Source | Required |
|-------|--------|----------|
| Idea/feature description | User command argument | Yes |
| Memory context | `.claptrap/memories.md` | Auto-read |
| Codebase context | Explore subagent | As needed |
| External research | Research subagent | As needed |

#### Process Steps

```
Step 1: Initialize
├── Read .claptrap/memories.md for prior decisions and patterns
├── Parse user's idea/feature description
└── Determine if research or exploration is needed

Step 2: Discovery Dialogue
├── Ask 3-5 clarifying questions about:
│   ├── User goals and success criteria
│   ├── Scope boundaries (what's in/out)
│   ├── Technical constraints or preferences
│   ├── Integration points with existing system
│   └── Timeline or phasing preferences
├── Wait for user responses
└── Iterate if answers reveal more questions (max 2 rounds)

Step 3: Research (if needed)
├── Spawn research subagent for external docs/APIs
├── Spawn explore subagent for codebase analysis
└── Collect findings

Step 4: Design Generation
├── Generate design document section by section:
│   ├── Intent (from user's idea + clarifications)
│   ├── Scope: In Scope / Out of Scope (from dialogue)
│   ├── Acceptance Criteria (testable conditions)
│   ├── Architecture Overview (components, data flow)
│   ├── Key Decisions (choices with rationale)
│   ├── Open Questions (unresolved items)
│   └── Next Steps (always: create OpenSpec proposal)
├── Present each section for user feedback
└── Iterate on sections as requested

Step 5: Finalize
├── Derive slug from feature name (kebab-case)
├── Create directory: .claptrap/designs/<slug>/
├── Write design.md with all sections
├── Write memory entries for significant decisions
└── Present summary and next steps
```

#### Output

**Primary Output**: `.claptrap/designs/<slug>/design.md`

**Structure** (updated template):
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

**Secondary Output**: Memory entries in `.claptrap/memories.md`

```markdown
---
## <Decision Title>
Type: decision | Date: YYYY-MM-DD | Tags: <feature-slug>, architecture

<1-3 sentences about the decision and rationale>
---
```

---

### Phase 2: `/claptrap-propose`

#### Trigger
```
/claptrap-propose .claptrap/designs/user-auth/design.md
```

Or with default (most recent design):
```
/claptrap-propose
```

#### Inputs

| Input | Source | Required |
|-------|--------|----------|
| Design document path | User argument or auto-detect | Yes |
| Memory context | `.claptrap/memories.md` | Auto-read |
| OpenSpec schema | `openspec/config.yaml` or default | Auto-read |

#### Process Steps

```
Step 1: Initialize
├── Read .claptrap/memories.md for context
├── Read design.md and parse all sections
├── Validate design has required sections:
│   ├── Intent (required)
│   ├── Scope (required)
│   ├── Acceptance Criteria (required)
│   └── Architecture Overview (recommended)
└── Derive change name from design slug

Step 2: Create OpenSpec Change
├── Run: openspec new <change-name>
├── Creates: openspec/changes/<change-name>/
└── Record: .openspec.yaml with metadata

Step 3: Generate proposal.md
├── Run: openspec instructions proposal --change <name> --json
├── Receive: template structure, dependencies, rules
├── Map design sections to proposal:
│   ├── Intent → Why
│   ├── Scope.InScope → What Changes
│   ├── Goals (from Intent) → Capabilities.New
│   ├── Scope.OutOfScope → Non-Goals (add to Impact)
│   └── Key Decisions → Impact
├── Add source link: <!-- Source: ../../.claptrap/designs/<slug>/design.md -->
└── Write: openspec/changes/<name>/proposal.md

Step 4: Alignment Review
├── Spawn: alignment-reviewer subagent
├── Input:
│   ├── .claptrap/designs/<slug>/design.md (source)
│   └── openspec/changes/<name>/proposal.md (generated)
├── Output: ALIGNED or GAPS: [list]
├── If GAPS:
│   ├── Fix proposal.md to address gaps
│   └── Re-run alignment review (max 2 cycles)
└── Proceed when ALIGNED

Step 5: Generate specs/*.md
├── For each capability in proposal.Capabilities:
│   ├── Run: openspec instructions specs --change <name> --capability <cap> --json
│   ├── Receive: template, dependencies, rules
│   ├── Map design sections to spec:
│   │   ├── Acceptance Criteria → ADDED Requirements with Scenarios
│   │   ├── Key Decisions → Constraints on scenarios
│   │   └── Architecture types → Referenced in scenarios
│   ├── Add source link
│   └── Write: openspec/changes/<name>/specs/<capability>/spec.md
└── Repeat for all capabilities

Step 6: Feasibility Review
├── Spawn: feasibility-reviewer subagent
├── Input:
│   ├── proposal.md
│   ├── specs/*.md
│   └── design.md (for architecture context)
├── Output: FEASIBLE or CONCERNS: [list]
├── If CONCERNS:
│   ├── Refine specs or update proposal
│   └── Re-run feasibility review (max 2 cycles)
└── Proceed when FEASIBLE

Step 7: Generate tasks.md
├── Run: openspec instructions tasks --change <name> --json
├── Receive: template, dependencies, rules
├── Map design sections to tasks:
│   ├── OpenSpec Proposals table (if exists) → Task groups
│   ├── Architecture.Components → Subtasks per component
│   ├── Architecture.Package Structure → File creation tasks
│   └── Acceptance Criteria → Verification tasks
├── Maintain phase ordering from design
├── Add source link
└── Write: openspec/changes/<name>/tasks.md

Step 8: Link and Finalize
├── Update design.md:
│   └── Add to "OpenSpec Proposals" section:
│       "- [<change-name>](../../openspec/changes/<name>/proposal.md)"
├── Write .source file in change directory:
│   └── "../../.claptrap/designs/<slug>/design.md"
├── Write memory entries for significant decisions
└── Present summary with links to all artifacts
```

#### Outputs

**Primary Output**: `openspec/changes/<change-name>/`

```
openspec/changes/<change-name>/
├── .openspec.yaml          # Metadata (schema, status, source link)
├── .source                  # Path to source design.md
├── proposal.md              # Why, What, Capabilities, Impact
├── specs/
│   ├── <capability-1>/
│   │   └── spec.md          # ADDED/MODIFIED requirements with scenarios
│   └── <capability-2>/
│       └── spec.md
└── tasks.md                 # Checkbox implementation steps
```

**Note**: OpenSpec's optional `design.md` artifact is **NOT created**. The source `.claptrap/designs/<slug>/design.md` serves this purpose and contains more detail.

**Secondary Output**: Updated design.md with proposal link

**Tertiary Output**: Memory entries

---

### Phase 3: `/claptrap-review`

#### Trigger
```
/claptrap-review user-auth
```

Or auto-detect most recent change:
```
/claptrap-review
```

#### Inputs

| Input | Source | Required |
|-------|--------|----------|
| Change ID | User argument or auto-detect | Yes |
| All change artifacts | `openspec/changes/<id>/` | Auto-read |
| Source design | `.source` file reference | Auto-read |

#### Process Steps

```
Step 1: Load Context
├── Read openspec/changes/<id>/.source to find design.md
├── Read design.md
├── Read proposal.md
├── Read all specs/*.md
└── Read tasks.md

Step 2: Plan Review
├── Spawn: plan-reviewer subagent
├── Input: All artifacts + design.md
├── Validate:
│   ├── Proposal.Why aligns with Design.Intent
│   ├── Proposal.Capabilities covers Design.Scope.InScope
│   ├── Proposal.Impact addresses Design.Key Decisions
│   ├── Specs cover all Acceptance Criteria
│   ├── Specs scenarios are testable (WHEN/THEN format)
│   ├── Tasks cover all Specs requirements
│   ├── Tasks maintain correct sequencing
│   └── No orphaned or unreferenced items
├── Output: APPROVED or REVISE with prioritized issues
└── Report findings to user

Step 3: Resolution (if REVISE)
├── Present issues by priority (Critical → Important → Minor)
├── User decides: fix now, defer, or accept risk
├── If fix: return to /claptrap-propose for regeneration
└── If accept: document accepted risks in memory
```

#### Output

**Primary Output**: Review verdict

```markdown
## Review Result: APPROVED

All artifacts are consistent with the source design.

### Validation Summary
- [ ] Proposal ↔ Design: ✓ Aligned
- [ ] Specs ↔ Acceptance Criteria: ✓ Complete
- [ ] Tasks ↔ Specs: ✓ Full coverage
- [ ] Sequencing: ✓ Valid dependency order

### Ready for Implementation
Run `/opsx:apply` to begin implementation.
```

Or:

```markdown
## Review Result: REVISE

### Critical Issues (must fix)
1. **Missing spec for capability X**: Design.Scope includes "OAuth support" but no spec exists for `oauth-integration`

### Important Issues (should fix)
2. **Task sequencing**: Task 3.2 depends on 4.1 but is ordered before it

### Minor Issues (consider fixing)
3. **Acceptance criteria coverage**: "Session timeout" criterion has no corresponding scenario

### Recommended Actions
1. Run `/claptrap-propose` with `--regenerate specs` to add missing capability
2. Manually reorder tasks in tasks.md
```

---

## Artifact Specifications

### Design Document (design.md)

**Location**: `.claptrap/designs/<feature-slug>/design.md`

**Purpose**: Comprehensive source of truth created through brainstorm dialogue. Contains all technical detail needed for implementation.

**Required Sections**:

| Section | Purpose | Maps To |
|---------|---------|---------|
| Intent | Why we're building this | proposal.Why |
| Scope.InScope | What's included | proposal.Capabilities |
| Scope.OutOfScope | What's excluded | proposal.Non-Goals |
| Acceptance Criteria | Testable conditions | specs.Scenarios |
| Architecture Overview | Technical structure | tasks.Groups, implementation context |
| Key Decisions | Choices with rationale | proposal.Impact, specs.Constraints |

**Optional Sections**:

| Section | Purpose |
|---------|---------|
| Open Questions | Unresolved items (should be empty before propose) |
| Core Types | TypeScript/code interfaces |
| Data Flow | Diagrams or descriptions |
| Package Structure | Directory layout |

**Lifecycle**:
1. Created by `/claptrap-brainstorm`
2. Updated with proposal link by `/claptrap-propose`
3. Referenced during `/opsx:apply` for implementation detail
4. Archived with change by `/opsx:archive`

---

### Proposal (proposal.md)

**Location**: `openspec/changes/<change-id>/proposal.md`

**Purpose**: Compact summary of what changes and why. OpenSpec-compatible format.

**Structure**:
```markdown
<!-- Source: ../../.claptrap/designs/<slug>/design.md -->

# Proposal: <Change Name>

## Why

<Motivation from design.Intent. 2-3 sentences.>

## What Changes

<High-level description of modifications from design.Scope.InScope>

## Capabilities

### New Capabilities
- `<capability-slug>`: <One-line description>

### Modified Capabilities
- `<existing-capability>`: <What changes>

## Non-Goals

- <From design.Scope.OutOfScope>

## Impact

### Code Changes
- <Affected files/modules>

### Dependencies
- <New dependencies if any>

### Key Decisions
- <From design.Key Decisions, summarized>

## Source

Full design: [design.md](../../.claptrap/designs/<slug>/design.md)
```

**Extraction Rules**:

| Design Section | Proposal Section | Transformation |
|----------------|------------------|----------------|
| Intent | Why | Direct copy or light summarization |
| Scope.InScope | What Changes | Summarize to 2-3 sentences |
| Goals (from Intent) | Capabilities.New | Extract as kebab-case slugs |
| Scope.OutOfScope | Non-Goals | Direct copy |
| Key Decisions | Impact.Key Decisions | Summarize each decision |
| Architecture.Components | Impact.Code Changes | List affected areas |

---

### Spec (spec.md)

**Location**: `openspec/changes/<change-id>/specs/<capability>/spec.md`

**Purpose**: Testable requirements with behavioral scenarios. One file per capability.

**Structure**:
```markdown
<!-- Source: ../../.claptrap/designs/<slug>/design.md -->

# Spec: <Capability Name>

## ADDED Requirements

### Requirement: <Requirement Name>

<Description of what this requirement accomplishes>

#### Scenario: <Scenario Name>

- **WHEN** <precondition or trigger>
- **THEN** <expected observable outcome>

#### Scenario: <Another Scenario>

- **WHEN** <condition>
- **THEN** <outcome>

### Requirement: <Another Requirement>

...

## MODIFIED Requirements

### Requirement: <Existing Requirement Name>

<What changed and why>

#### Scenario: <Updated Scenario>

- **WHEN** <updated condition>
- **THEN** <updated outcome>

## REMOVED Requirements

### Requirement: <Requirement Being Removed>

<Reason for removal>
```

**Extraction Rules**:

| Design Section | Spec Section | Transformation |
|----------------|--------------|----------------|
| Acceptance Criteria | Requirements | Each criterion → one requirement |
| Acceptance Criteria | Scenarios | Convert "should X when Y" → WHEN Y / THEN X |
| Key Decisions | Constraints | Add as scenario conditions |
| Architecture.Types | References | Link to design for type definitions |

**Example Transformation**:

```markdown
# From design.md Acceptance Criteria:
- [ ] Status panel shows one line per provider with progress bar
- [ ] Provider card displays usage percentage as progress ring

# Becomes specs/status-panel-widget/spec.md:

## ADDED Requirements

### Requirement: Provider Status Display

Display each configured provider's quota status in a compact, scannable format.

#### Scenario: Single provider row

- **WHEN** user opens Status Panel with one configured provider
- **THEN** provider appears on single line with name, progress bar, and percentage

#### Scenario: Multiple providers

- **WHEN** user opens Status Panel with 3 configured providers
- **THEN** each provider appears on its own line, sorted by name

### Requirement: Usage Visualization

See [Core Types](../../.claptrap/designs/quota-monitor/design.md#core-types) for QuotaInfo interface.

#### Scenario: Progress ring display

- **WHEN** provider card is rendered with quotaUsed=70 and quotaLimit=100
- **THEN** progress ring shows 70% filled with appropriate color (ok/warning/critical)
```

---

### Tasks (tasks.md)

**Location**: `openspec/changes/<change-id>/tasks.md`

**Purpose**: Checkbox-based implementation checklist with numbered groups and subtasks.

**Structure**:
```markdown
<!-- Source: ../../.claptrap/designs/<slug>/design.md -->

# Tasks: <Change Name>

## 1. <Task Group Name>

- [ ] 1.1 <Specific implementation task>
- [ ] 1.2 <Another task>
- [ ] 1.3 <Verification task: confirm X works>

## 2. <Another Task Group>

- [ ] 2.1 <Task>
- [ ] 2.2 <Task>

## 3. Testing & Verification

- [ ] 3.1 Verify all acceptance criteria from design.md
- [ ] 3.2 Run `/opsx:verify` to validate implementation
```

**Extraction Rules**:

| Design Section | Tasks Section | Transformation |
|----------------|---------------|----------------|
| OpenSpec Proposals table | Task Groups | Each proposal row → one group |
| Architecture.Components | Subtasks | Each component → implementation subtasks |
| Architecture.Package Structure | File tasks | Each directory/file → creation task |
| Acceptance Criteria | Verification tasks | Each criterion → verification subtask |

**Example Transformation**:

```markdown
# From design.md OpenSpec Proposals:
| 4 | scaffold-quota-monitor-package | Create package structure |
| 5 | add-provider-abstraction-layer | Design provider interface |

# From design.md Architecture.Package Structure:
packages/quota-monitor/
├── src/
│   ├── index.ts
│   ├── types/
│   │   └── provider.ts

# Becomes tasks.md:

## 1. Scaffold Package

- [ ] 1.1 Create `packages/quota-monitor/` directory
- [ ] 1.2 Create `package.json` with name, dependencies, scripts
- [ ] 1.3 Create `tsconfig.json` extending root config
- [ ] 1.4 Create `src/index.ts` with placeholder exports
- [ ] 1.5 Add package to workspace in root `package.json`
- [ ] 1.6 Verify: `npm install` succeeds, `npm run build` succeeds

## 2. Provider Abstraction Layer

- [ ] 2.1 Create `src/types/provider.ts` with QuotaProvider interface
- [ ] 2.2 Create `src/types/quota.ts` with QuotaInfo, ModelUsage types
- [ ] 2.3 Create `src/providers/base.ts` with abstract BaseProvider
- [ ] 2.4 Verify: Types compile, base class is extensible
```

---

## Component Specifications

### Commands

#### `/claptrap-brainstorm`

**File**: `src/commands/claptrap-brainstorm.md`

**Invocation**: `/claptrap-brainstorm "<idea or feature description>"`

**Behavior**:
1. Read memory context
2. Engage in discovery dialogue (3-5 questions, max 2 rounds)
3. Spawn research/explore subagents as needed
4. Generate design document section by section
5. Write design.md to `.claptrap/designs/<slug>/`
6. Write memory entries for decisions
7. Present summary and next steps

**Model**: Sonnet (default) or user-configured

**Output**: `.claptrap/designs/<slug>/design.md`

---

#### `/claptrap-propose`

**File**: `src/commands/claptrap-propose.md`

**Invocation**:
- `/claptrap-propose .claptrap/designs/<slug>/design.md`
- `/claptrap-propose` (auto-detect most recent)

**Behavior**:
1. Read memory context and design.md
2. Run `openspec new <change-name>`
3. Generate proposal.md using `openspec instructions proposal`
4. Spawn alignment-reviewer, fix gaps (max 2 cycles)
5. Generate specs/*.md using `openspec instructions specs`
6. Spawn feasibility-reviewer, fix concerns (max 2 cycles)
7. Generate tasks.md using `openspec instructions tasks`
8. Link artifacts to design.md
9. Write memory entries
10. Present summary with artifact links

**Model**: Sonnet (default) or user-configured

**Output**: `openspec/changes/<id>/{proposal.md, specs/*, tasks.md}`

---

#### `/claptrap-review`

**File**: `src/commands/claptrap-review.md`

**Invocation**:
- `/claptrap-review <change-id>`
- `/claptrap-review` (auto-detect most recent)

**Behavior**:
1. Read all artifacts from change directory
2. Read source design.md via .source link
3. Spawn plan-reviewer
4. Report APPROVED or REVISE with prioritized issues
5. If REVISE, guide user through resolution options

**Model**: Sonnet (default) or user-configured

**Output**: Review verdict with action items

---

### Skills

#### `claptrap-brainstorm-skill`

**File**: `src/skills/claptrap-brainstorm/SKILL.md`

**Purpose**: Dialogue-driven design discovery

**Invoked by**: `/claptrap-brainstorm` command

**Capabilities**:
- Clarifying question generation
- Section-by-section design presentation
- Subagent spawning for research/exploration
- Memory read/write integration

**Template**: `src/skills/claptrap-brainstorm/templates/design.md`

---

#### `claptrap-propose-skill`

**File**: `src/skills/claptrap-propose/SKILL.md`

**Purpose**: Design → OpenSpec artifact extraction

**Invoked by**: `/claptrap-propose` command

**Capabilities**:
- Design document parsing
- OpenSpec CLI integration (`openspec instructions`, `openspec new`)
- Section mapping and extraction
- Review agent spawning with iteration limits
- Artifact linking

**Templates**:
- `src/skills/claptrap-propose/templates/proposal-hints.md`
- `src/skills/claptrap-propose/templates/spec-hints.md`
- `src/skills/claptrap-propose/templates/tasks-hints.md`

---

#### `claptrap-memory` (Unchanged)

**File**: `src/skills/claptrap-memory/SKILL.md`

**Purpose**: Read/write project decisions, patterns, lessons

**Invoked by**: All commands at start (read) and end (write)

---

#### `claptrap-spawn-subagent` (Unchanged)

**File**: `src/skills/claptrap-spawn-subagent/SKILL.md`

**Purpose**: Spawn subagents with fresh context and bounded scope

**Invoked by**: Commands and skills needing specialized work

---

### Agents

#### alignment-reviewer

**File**: `src/agents/alignment-reviewer.md`

**Purpose**: Validate proposal against source design

**Input**:
- Source design.md
- Generated proposal.md

**Output**: `ALIGNED` or `GAPS: 1. [Critical/Important/Minor] <issue>`

**Changes from current**: Add design.md to input context

---

#### feasibility-reviewer

**File**: `src/agents/feasibility-reviewer.md`

**Purpose**: Validate specs and tasks for realism and sequencing

**Input**:
- proposal.md
- specs/*.md
- tasks.md
- design.md (for architecture context)

**Output**: `FEASIBLE` or `CONCERNS: 1. [Critical/Important/Minor] <issue>`

**Changes from current**: Add design.md and specs to input context

---

#### plan-reviewer

**File**: `src/agents/plan-reviewer.md`

**Purpose**: Comprehensive validation of all artifacts

**Input**:
- design.md (source)
- proposal.md
- specs/*.md
- tasks.md

**Output**: `APPROVED: <summary>` or `REVISE: <prioritized issues>`

**Validation Checks**:
1. Proposal.Why aligns with Design.Intent
2. Proposal.Capabilities covers Design.Scope.InScope
3. Proposal.Impact addresses Design.Key Decisions
4. Specs cover all Design.Acceptance Criteria
5. Specs scenarios are testable (WHEN/THEN format)
6. Tasks cover all Specs requirements
7. Tasks maintain correct sequencing
8. No orphaned or unreferenced items

**Changes from current**: Refocus for new artifact flow

---

## Integration with OpenSpec

### CLI Commands Used

| Command | When Used | Purpose |
|---------|-----------|---------|
| `openspec new <name>` | Start of `/claptrap-propose` | Create change directory |
| `openspec instructions proposal --json` | Generating proposal.md | Get schema-aware template and rules |
| `openspec instructions specs --json` | Generating specs/*.md | Get spec template and rules |
| `openspec instructions tasks --json` | Generating tasks.md | Get tasks template and rules |
| `openspec status --json` | Optional status check | Verify artifact completion |

### What We Use from OpenSpec

- Change directory structure (`openspec/changes/<id>/`)
- Artifact templates and generation instructions
- Schema-aware rules and constraints
- Status tracking and verification

### What We Skip from OpenSpec

- `/opsx:new` command (we call CLI directly)
- `/opsx:continue` command (we generate all artifacts in one flow)
- `/opsx:ff` command (we have our own flow)
- OpenSpec's optional `design.md` artifact (redundant with brainstorm output)

### What We Defer to OpenSpec

- `/opsx:apply` for implementation
- `/opsx:verify` for implementation verification
- `/opsx:archive` for change archival
- `/opsx:sync` for spec synchronization

---

## File Structure

### Source Structure (this repo)

```
src/
├── AGENTS.md                           # Overview of all components
├── README.md                           # Directory guide
│
├── commands/
│   ├── AGENTS.md                       # Command registry
│   ├── claptrap-brainstorm.md          # REFACTORED
│   ├── claptrap-propose.md             # NEW
│   ├── claptrap-review.md              # NEW
│   └── claptrap-refactor.md            # UNCHANGED
│
├── skills/
│   ├── AGENTS.md                       # Skill registry
│   ├── claptrap-brainstorm/            # REFACTORED
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── design.md               # Updated template
│   ├── claptrap-propose/               # NEW
│   │   ├── SKILL.md
│   │   └── templates/
│   │       ├── proposal-hints.md
│   │       ├── spec-hints.md
│   │       └── tasks-hints.md
│   ├── claptrap-memory/                # UNCHANGED
│   │   └── SKILL.md
│   ├── claptrap-spawn-subagent/        # UNCHANGED
│   │   └── SKILL.md
│   └── claptrap-refactor/              # UNCHANGED
│       └── SKILL.md
│
├── agents/
│   ├── AGENTS.md                       # Agent registry
│   ├── alignment-reviewer.md           # UPDATED (add design.md input)
│   ├── feasibility-reviewer.md         # UPDATED (add design.md, specs input)
│   ├── plan-reviewer.md                # REFACTORED
│   ├── code-reviewer.md                # UNCHANGED
│   ├── research.md                     # UNCHANGED
│   └── ui-designer.md                  # UNCHANGED
│
├── templates/
│   └── design.md                       # Updated design template
│
└── code-conventions/                   # UNCHANGED
    ├── python.md
    └── snowflake.md
```

### Installed Structure (target projects)

```
.claptrap/
├── commands/                           # Copy of src/commands
├── skills/                             # Copy of src/skills
├── agents/                             # Copy of src/agents
├── templates/                          # Copy of src/templates
├── code-conventions/                   # Copy of src/code-conventions
├── memories.md                         # Project memory file
└── designs/                            # User-created designs
    └── <feature-slug>/
        └── design.md

openspec/
├── config.yaml                         # OpenSpec configuration
├── changes/                            # Active changes
│   └── <change-id>/
│       ├── .openspec.yaml
│       ├── .source                     # Link to design.md
│       ├── proposal.md
│       ├── specs/
│       │   └── <capability>/
│       │       └── spec.md
│       └── tasks.md
└── specs/                              # Main specs (synced from changes)
```

---

## Migration Plan

### Phase 1: Create New Components

1. Create `src/commands/claptrap-propose.md`
2. Create `src/commands/claptrap-review.md`
3. Create `src/skills/claptrap-propose/SKILL.md`
4. Create `src/skills/claptrap-propose/templates/`
5. Update `src/templates/design.md`

### Phase 2: Update Existing Components

1. Update `src/commands/claptrap-brainstorm.md` to use new template
2. Update `src/skills/claptrap-brainstorm/SKILL.md` for memory integration
3. Update `src/agents/alignment-reviewer.md` to accept design.md
4. Update `src/agents/feasibility-reviewer.md` to accept design.md, specs
5. Update `src/agents/plan-reviewer.md` for new validation flow

### Phase 3: Remove Deprecated Components

1. Remove `src/commands/propose.md` (replaced by claptrap-propose)
2. Remove `src/commands/implement-change.md` (use /opsx:apply)
3. Remove `src/commands/archive-change.md` (use /opsx:archive)
4. Remove `src/commands/finish-openspec-change.md` (use /opsx:archive)
5. Remove `src/skills/design-to-proposal/` (merged into claptrap-propose)
6. Remove `src/skills/claptrap-openspec-proposal/` (merged into claptrap-propose)

### Phase 4: Update Documentation

1. Update `src/AGENTS.md` with new component list
2. Update `src/commands/AGENTS.md` registry
3. Update `src/skills/AGENTS.md` registry
4. Update `src/agents/AGENTS.md` registry
5. Update install script if needed

---

## Risks, Concerns & Mitigations

This section examines potential concerns with the proposed workflow, evaluates whether each concern is justified, and proposes mitigations where appropriate.

### Concern 1: Added Complexity vs. Simplicity Goal

**The Concern**: GOALS.md prioritizes simplicity, but this proposal introduces a multi-phase workflow with three commands, extraction logic, review cycles, and OpenSpec CLI integration. Is this actually simpler than the current system?

**Analysis**: This concern is **partially justified**.

The proposal adds:
- Explicit artifact extraction rules (new complexity)
- OpenSpec CLI dependency (new external dependency)
- Two review cycles with iteration limits (new logic)

However, it removes:
- 4 commands (`propose`, `implement-change`, `archive-change`, `finish-openspec-change`)
- 2 skills (`design-to-proposal`, `claptrap-openspec-proposal`)
- Duplicated artifact generation logic (now delegated to OpenSpec)
- Ambiguous handoff between brainstorm and OpenSpec

**Verdict**: Net neutral to slightly simpler. The workflow has more explicit steps, but fewer components and clearer boundaries. The complexity is **visible** rather than hidden, which aids maintainability.

**Mitigation**: Document the "fast path" for simple changes that don't need full workflow (see Concern 10).

---

### Concern 2: OpenSpec CLI Dependency

**The Concern**: The workflow depends on `openspec instructions` CLI calls. What if:
- OpenSpec CLI is not installed?
- OpenSpec CLI changes its interface?
- OpenSpec CLI has bugs or unexpected behavior?

**Analysis**: This concern is **justified and important**.

The proposal creates a hard dependency on OpenSpec CLI. If OpenSpec changes, Claptrap breaks.

**Verdict**: Accept this risk with mitigations. The alternative (duplicating OpenSpec logic) is worse for maintainability.

**Mitigations**:
1. **Version pinning**: Document minimum OpenSpec version in install requirements
2. **Graceful degradation**: If CLI is unavailable, fall back to template-only generation with warning
3. **CLI wrapper**: Create thin wrapper function that validates CLI output format before use
4. **Integration tests**: Add smoke tests that verify CLI commands work as expected

```markdown
# Add to install.py or setup script:
OPENSPEC_MIN_VERSION = "1.0.0"

def verify_openspec():
    result = run("openspec --version")
    if version < OPENSPEC_MIN_VERSION:
        warn(f"OpenSpec {version} may have compatibility issues. Recommended: {OPENSPEC_MIN_VERSION}+")
```

---

### Concern 3: Artifact Extraction Accuracy

**The Concern**: The proposal relies on AI to extract OpenSpec artifacts from design.md. What if:
- The extraction is inconsistent across runs?
- The AI misses important details?
- The mapping rules are ambiguous?

**Analysis**: This concern is **justified**.

AI-driven extraction is inherently non-deterministic. The same design.md could produce slightly different artifacts on different runs.

**Verdict**: Accept with mitigations. This is the fundamental tradeoff of AI-assisted workflows.

**Mitigations**:
1. **Explicit mapping rules**: The proposal documents exactly which sections map where (see Artifact Specifications)
2. **Review cycles**: Alignment and feasibility reviewers catch extraction errors
3. **Source links**: Every artifact links back to design.md, allowing human verification
4. **Template hints**: `proposal-hints.md`, `spec-hints.md`, `tasks-hints.md` provide structured guidance
5. **Regeneration option**: If extraction is wrong, user can run `/claptrap-propose --regenerate <artifact>`

**Open question**: Should we add a "diff review" step that shows the user what was extracted before writing artifacts?

---

### Concern 4: Review Agent Effectiveness

**The Concern**: The workflow spawns alignment-reviewer, feasibility-reviewer, and plan-reviewer agents. Are these reviews actually effective? What if:
- Reviews are too lenient (miss real issues)?
- Reviews are too strict (block valid work)?
- 2 iteration cycles aren't enough?

**Analysis**: This concern is **partially justified**.

Review agents are only as good as their prompts. Current prompts are untested against the new artifact flow.

**Verdict**: Accept with monitoring. Review effectiveness should be evaluated after implementation.

**Mitigations**:
1. **Specific review criteria**: Update agent prompts with explicit checklists (see plan-reviewer Validation Checks)
2. **Severity tiers**: Critical/Important/Minor classification prevents blocking on minor issues
3. **Override option**: User can proceed despite REVISE verdict with `--force` flag (documents accepted risk)
4. **Feedback loop**: Track how often reviews catch real issues vs. false positives
5. **Adjustable cycles**: Make iteration limit configurable per project

**Observation**: The 2-cycle limit is a pragmatic choice. If 2 cycles don't resolve issues, there's likely a deeper problem that automated iteration won't fix.

---

### Concern 5: Design.md as Single Source of Truth

**The Concern**: The proposal makes design.md the authoritative source. What if:
- Design.md is incomplete or poorly structured?
- Design.md drifts from artifacts after manual edits?
- Design.md gets deleted or corrupted?

**Analysis**: This concern is **justified**.

Single source of truth creates single point of failure.

**Verdict**: Accept with mitigations. The alternative (multiple sources of truth) is worse.

**Mitigations**:
1. **Validation on propose**: `/claptrap-propose` validates design.md has required sections before proceeding
2. **Git tracking**: Design.md is version-controlled, allowing recovery
3. **Bidirectional links**: Artifacts link to design.md, design.md links to artifacts, making drift visible
4. **Drift detection**: `/claptrap-review` compares design.md against artifacts to detect inconsistencies
5. **Template enforcement**: Brainstorm skill uses template that ensures required sections exist

**Potential enhancement**: Add checksum or hash to `.source` file to detect design.md modifications after artifact generation.

---

### Concern 6: Memory System Integration Points

**The Concern**: The proposal says memory is read at start and written at end of each phase. But:
- What exactly gets written?
- Will memory entries be useful or become noise?
- How do we prevent memory bloat?

**Analysis**: This concern is **partially justified**.

Memory is valuable but can become cluttered with low-value entries.

**Verdict**: Accept with existing memory skill guidelines.

**Mitigations** (already in memory skill):
1. **Filter-then-write**: Generate candidates, critically evaluate, only add if useful to future agents
2. **7 valid types**: decision, pattern, anti-pattern, lesson, solution, architectural decision
3. **Prefer updates**: Update existing entries rather than adding duplicates
4. **1-3 sentences**: Keep entries concise
5. **No secrets**: Explicitly prohibit sensitive data

**Specific guidance for new workflow**:

| Phase | Read | Write |
|-------|------|-------|
| Brainstorm | Prior decisions, patterns for this domain | Key architecture decisions, chosen approaches |
| Propose | Prior decisions (context for extraction) | Significant capability definitions, review lessons |
| Review | (none - uses artifacts directly) | Accepted risks if proceeding despite issues |

---

### Concern 7: Environment Compatibility

**The Concern**: The proposal claims environment agnosticism (Cursor, VS Code, OpenCode, Codex). But:
- Different environments may have different capabilities
- Some environments may not support subagent spawning
- Model behavior varies by provider

**Analysis**: This concern is **justified**.

The proposal has not been tested across all target environments.

**Verdict**: Accept with graceful degradation strategy.

**Mitigations**:
1. **Markdown-based skills**: Skills are markdown files, not code, so they work anywhere that can read files
2. **Subagent fallback**: If spawning fails, present the subagent prompt for user to run manually
3. **CLI fallback**: If OpenSpec CLI is unavailable, provide manual artifact creation instructions
4. **Provider-aware prompts**: Avoid provider-specific features in skill prompts
5. **Testing matrix**: Add environment compatibility to acceptance criteria

**Known limitations to document**:
- Codex may not support interactive dialogue well (single-turn bias)
- Some environments may have token limits that affect design.md size
- Subagent spawning behavior may vary

---

### Concern 8: User Friction and Learning Curve

**The Concern**: Users must learn:
- When to use `/claptrap-brainstorm` vs. `/opsx:new`
- The artifact structure and linking
- Review verdicts and how to respond
- When the workflow is overkill

**Analysis**: This concern is **justified**.

Any workflow imposes cognitive overhead. The question is whether the overhead is worth the benefits.

**Verdict**: Accept with good documentation and escape hatches.

**Mitigations**:
1. **Clear entry point**: `/claptrap-brainstorm` is always the starting point for new features
2. **Guided flow**: Each command outputs explicit next steps
3. **Help text**: Commands include usage examples and common scenarios
4. **Escape hatches**: Users can always drop to native OpenSpec commands if preferred
5. **Progressive disclosure**: Start with brainstorm → propose → implement. Review is optional.

**Documentation needed**:
- Quick start guide (5-minute walkthrough)
- Decision tree: "Which command should I use?"
- Troubleshooting: "What if review fails?"

---

### Concern 9: Scaling to Large Projects

**The Concern**: The examples show a single feature with ~10 acceptance criteria. What about:
- Large designs with 50+ acceptance criteria?
- Designs that span multiple capabilities?
- Projects with hundreds of files?
- Token limits during artifact generation?

**Analysis**: This concern is **partially justified**.

Large designs may hit practical limits (token size, artifact count, review complexity).

**Verdict**: Accept with guidance for decomposition.

**Mitigations**:
1. **Encourage decomposition**: Large features should be split into multiple designs
2. **Capability-based partitioning**: Each capability gets its own spec file, naturally partitioning work
3. **Phased proposals**: Design.md can list proposals by phase, allowing incremental generation
4. **Streaming generation**: Generate artifacts one at a time to manage token limits
5. **Parallel changes**: OpenSpec supports multiple concurrent changes

**Guidance to add**:

> **When to split a design:**
> - More than 5 capabilities
> - More than 20 acceptance criteria
> - Architecture spans more than 3 major system boundaries
> - Estimated implementation > 2 weeks
>
> Split by creating multiple design.md files in the same feature directory, each focused on a subset of capabilities.

---

### Concern 10: Overkill for Small Changes

**The Concern**: The full workflow (brainstorm → propose → review → implement) is heavyweight. What about:
- Typo fixes?
- Single-line bug fixes?
- Small enhancements?
- Urgent hotfixes?

**Analysis**: This concern is **strongly justified**.

Not every change needs a design document and formal artifact generation.

**Verdict**: Accept by documenting escape hatches and "fast paths".

**Mitigations**:
1. **Direct OpenSpec**: For changes where requirements are already clear, use `/opsx:new` directly
2. **Skip brainstorm**: If you already have a design, jump to `/claptrap-propose`
3. **Skip propose**: For small changes, use `/opsx:new` + `/opsx:continue` natively
4. **No workflow needed**: Typo fixes and trivial changes don't need formal workflow at all

**Guidance to add**:

> **Workflow selection guide:**
>
> | Change Size | Workflow |
> |-------------|----------|
> | Trivial (typos, formatting) | Direct commit, no workflow |
> | Small (single-file fixes) | `/opsx:new` → `/opsx:continue` → `/opsx:apply` |
> | Medium (clear requirements) | `/claptrap-propose` with inline design |
> | Large (needs discovery) | `/claptrap-brainstorm` → full workflow |
> | Complex (architecture changes) | Full workflow with extended brainstorm |

---

### Concern 11: Artifact Drift Over Time

**The Concern**: After artifacts are generated, users may manually edit them. This creates drift between:
- design.md and proposal.md
- proposal.md and specs/*.md
- specs/*.md and tasks.md

**Analysis**: This concern is **justified**.

Editing is normal and expected. Drift is a natural consequence.

**Verdict**: Accept with detection and guidance.

**Mitigations**:
1. **Prefer regeneration**: If design changes, re-run `/claptrap-propose` rather than manual edits
2. **Drift detection**: `/claptrap-review` can detect inconsistencies between artifacts
3. **Source links preserved**: Links help identify which artifact is authoritative
4. **Edit guidance**: Document that edits should flow design.md → proposal → specs → tasks

**Observation**: Some drift is acceptable. The goal is that artifacts are *useful*, not that they're perfectly synchronized. If proposal.md is edited to clarify something, that's fine as long as the clarification is consistent with design.md intent.

---

### Concern 12: Testing the Workflow Itself

**The Concern**: How do we validate that the workflow works correctly? What if:
- Skills have bugs in their prompts?
- Extraction rules are incorrect?
- Review agents have false negatives?

**Analysis**: This concern is **justified**.

The workflow is itself software that needs testing.

**Verdict**: Accept by adding testing strategy.

**Mitigations**:
1. **Example-based testing**: Create reference design.md files with expected artifact outputs
2. **Skill smoke tests**: Verify each skill runs without errors against example inputs
3. **Round-trip testing**: brainstorm → propose → review should produce APPROVED for well-formed designs
4. **Regression tracking**: Save artifact outputs from known-good runs, compare against future runs
5. **User feedback loop**: Collect issues from real usage, fix skill prompts iteratively

**Test cases to create**:
- Minimal design (single capability, 2 acceptance criteria)
- Medium design (3 capabilities, 10 acceptance criteria)
- Edge case: design with missing optional sections
- Edge case: design with very long architecture section
- Edge case: design that references external files

---

### Concern 13: Maintenance Burden

**The Concern**: The workflow adds:
- 3 command files to maintain
- 2 skill directories to maintain
- 4 template files to maintain
- Updated agent prompts to maintain

What's the ongoing maintenance burden?

**Analysis**: This concern is **partially justified**.

More files = more maintenance. But fewer, clearer files may be easier to maintain than the current tangled structure.

**Verdict**: Accept with maintenance guidelines.

**Mitigations**:
1. **Single responsibility**: Each file has one clear purpose
2. **DRY templates**: Hints files are shared, not duplicated
3. **OpenSpec delegation**: Heavy lifting delegated to OpenSpec, reducing our maintenance
4. **Version documentation**: Track which OpenSpec version was tested
5. **Changelog**: Maintain changelog for workflow changes

**Maintenance tasks to schedule**:
- Quarterly: Verify against latest OpenSpec release
- Per-release: Run smoke tests against example designs
- As-needed: Update prompts based on user feedback

---

### Concern 14: What If OpenSpec Is Abandoned?

**The Concern**: The workflow deeply integrates with OpenSpec. If OpenSpec development stops or the project is abandoned, what happens?

**Analysis**: This concern is **valid but low probability**.

OpenSpec is actively maintained and has a growing user base. However, all dependencies carry this risk.

**Verdict**: Accept with exit strategy.

**Mitigations**:
1. **Thin integration layer**: We wrap OpenSpec CLI, not embed it. Replacement is possible.
2. **Artifact format documented**: Our artifact specs are documented independently of OpenSpec
3. **Fallback templates**: We have our own template hints that could become primary
4. **Fork option**: OpenSpec is open-source, could be forked if abandoned

**Exit strategy if OpenSpec is abandoned**:
1. Fork OpenSpec at last known-good version
2. Maintain minimal fork with CLI commands we use
3. Or: Replace CLI calls with direct template generation using our hints files

---

### Summary: Risk Assessment Matrix

| Concern | Severity | Likelihood | Mitigation Quality | Residual Risk |
|---------|----------|------------|-------------------|---------------|
| 1. Added complexity | Medium | High | Good | Low |
| 2. OpenSpec CLI dependency | High | Medium | Good | Medium |
| 3. Extraction accuracy | Medium | Medium | Good | Low |
| 4. Review effectiveness | Medium | Medium | Moderate | Medium |
| 5. Single source of truth | Medium | Low | Good | Low |
| 6. Memory integration | Low | Low | Good | Very Low |
| 7. Environment compatibility | Medium | Medium | Moderate | Medium |
| 8. User friction | Medium | High | Good | Low |
| 9. Scaling to large projects | Medium | Low | Good | Low |
| 10. Overkill for small changes | Medium | High | Good | Low |
| 11. Artifact drift | Low | High | Moderate | Low |
| 12. Testing the workflow | Medium | Medium | Moderate | Medium |
| 13. Maintenance burden | Medium | Medium | Good | Low |
| 14. OpenSpec abandonment | High | Very Low | Good | Very Low |

**Overall assessment**: The workflow has manageable risks. The highest residual risks are:
1. **OpenSpec CLI dependency** - mitigated by version pinning and graceful degradation
2. **Review effectiveness** - mitigated by specific criteria and override options
3. **Environment compatibility** - mitigated by fallback strategies and testing

None of these risks are blocking. All can be addressed through careful implementation and iterative refinement.

---

## Open Questions Resolved

### Q1: Should I use a custom workflow or merge with standard OpenSpec?

**Resolution**: Merge with light customization.

- Brainstorming is a **pre-OpenSpec phase** that produces input for OpenSpec
- We use the standard `spec-driven` schema for artifacts
- We skip OpenSpec's optional `design.md` artifact (brainstorm output is more detailed)
- We call OpenSpec CLI for instructions, not duplicate logic

### Q2: Do I need all artifacts (proposal, design, specs, tasks)?

**Resolution**: proposal + specs + tasks. Design is conditional (skipped in our flow).

- **proposal.md** - Compact summary: Why, What, Capabilities, Impact
- **specs/*.md** - Testable requirements with scenarios
- **tasks.md** - Implementation checklist
- **design.md** - SKIPPED, brainstorm output serves this purpose

### Q3: How should I create artifacts? Skills + templates or OpenSpec built-in?

**Resolution**: Hybrid - thin skills wrapping OpenSpec CLI.

- Call `openspec instructions <artifact>` for schema-aware prompts
- Use our own extraction logic to map design → artifacts
- Add memory integration and review agent spawning
- Don't duplicate OpenSpec's artifact generation logic

---

## Final Summary

### What This Proposal Achieves

1. **Unified Entry Point**: `/claptrap-brainstorm` is the front-door for all feature work
2. **Preserved Detail**: Brainstorm's comprehensive design.md is the source of truth, never lost
3. **OpenSpec Compatibility**: Generated artifacts are fully OpenSpec-compatible
4. **Modular Architecture**: Skills are focused and composable
5. **Environment Agnostic**: Markdown-based playbooks work everywhere
6. **Quality Gates**: Alignment, feasibility, and plan review at key checkpoints
7. **Memory Integration**: Decisions captured throughout the workflow

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Brainstorm output format | Comprehensive design.md | More detail than any single OpenSpec artifact |
| OpenSpec integration | CLI wrapper | Maintainability - OpenSpec updates flow through |
| Design.md artifact | Skip | Redundant with brainstorm output |
| Artifact generation | All at once in /propose | User control at phase boundaries, not per-artifact |
| Review timing | After all artifacts | Holistic validation catches cross-artifact issues |

### Component Summary

| Component | Count | Purpose |
|-----------|-------|---------|
| Commands | 3 | User-facing entry points: brainstorm, propose, review |
| Skills | 4 | Reusable playbooks: brainstorm, propose, memory, spawn-subagent |
| Agents | 6 | Specialized reviewers and workers |
| Templates | 4 | Design, proposal hints, spec hints, tasks hints |

### Success Criteria

- [ ] `/claptrap-brainstorm` produces complete design.md through dialogue
- [ ] `/claptrap-propose` generates valid OpenSpec artifacts from design
- [ ] All artifacts link back to source design.md
- [ ] Review agents validate artifact consistency
- [ ] Memory captures decisions at each phase
- [ ] Implementation can proceed with `/opsx:apply` using generated artifacts
- [ ] Workflow is installable in under 5 minutes
- [ ] No per-request API billing required

### Next Steps

1. Review this proposal document
2. Create OpenSpec change for implementation: `/claptrap-propose claptrap-workflow-proposal.md`
3. Implement in phases per Migration Plan
4. Test with real feature development workflow
5. Document and release

---

*Document generated: 2026-01-28*
*Status: Ready for review*
