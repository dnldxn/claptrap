# Claptrap Workflow Guide

This document explains how the Claptrap AI development workflow operates, from initial idea to completed implementation.

---

## Quick Reference

```
/claptrap-brainstorm <idea>        # Create design from idea
/claptrap-propose [design-path]    # Generate OpenSpec artifacts
/claptrap-review [change-id]       # Validate before implementation
/opsx:apply [change-id]            # Implement (native OpenSpec)
/opsx:verify [change-id]           # Verify implementation
/opsx:archive [change-id]          # Archive completed change
```

### Workflow Selection

| Change Size | Approach | Commands |
|-------------|----------|----------|
| Trivial | Direct edit | None needed |
| Small | Quick brainstorm | `/claptrap-brainstorm` then implement manually |
| Medium | Full workflow | brainstorm -> propose -> review -> apply |
| Large | Multi-proposal | Design may spawn multiple proposals |
| Complex | Iterative | Multiple review cycles, design revisions |

### Key Paths

| Artifact | Location |
|----------|----------|
| Designs | `.claptrap/designs/<YYYY-MM-DD><feature-slug>/design.md` |
| Proposals | `openspec/changes/<change-id>/proposal.md` |
| Specs | `openspec/changes/<change-id>/specs/<capability>/spec.md` |
| Tasks | `openspec/changes/<change-id>/tasks.md` |
| Memories | `.claptrap/memories.md` |

---

## Overview

Claptrap provides a structured workflow for AI-assisted software development that bridges ideation and implementation. The workflow is built on three principles:

1. **Design-first**: Every change starts with a clear, validated design document
2. **Artifact generation**: OpenSpec artifacts are extracted views from the design
3. **Review gates**: Automated validation ensures alignment before implementation

The core insight is that a brainstorm `design.md` contains more detail than OpenSpec artifacts individually. Rather than replacing this detail, we **extract** OpenSpec-compatible artifacts from it while preserving the original as the authoritative source.

---

## How It Works

```
+---------------------------------------------------------------------------+
|  PHASE 1: BRAINSTORM                                                      |
|                                                                           |
|  /claptrap-brainstorm "Add user authentication"                           |
|  +-- Read memory context                                                  |
|  +-- Dialogue: clarifying questions until 100% clarity (min 3 questions)  |
|  +-- Spawn research/explore subagents if needed                           |
|  +-- Generate design section by section                                   |
|  +-- Write memory entries for decisions                                   |
|  +-- Output: .claptrap/designs/<slug>/design.md                           |
|                                                                           |
|  USER CHECKPOINT: Review design, request changes, or approve              |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
|  PHASE 2: PROPOSE                                                         |
|                                                                           |
|  /claptrap-propose [design-path]                                          |
|  +-- Read memory and design.md                                            |
|  +-- Initialize OpenSpec change                                           |
|  +-- Generate proposal.md -> alignment review (max 2 cycles)              |
|  +-- Generate specs/*.md -> feasibility review (max 2 cycles)             |
|  +-- Generate tasks.md                                                    |
|  +-- Link artifacts back to design                                        |
|  +-- Output: openspec/changes/<id>/{proposal.md, specs/*, tasks.md}       |
|                                                                           |
|  USER CHECKPOINT: Review artifacts or approve                             |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
|  PHASE 3: REVIEW                                                          |
|                                                                           |
|  /claptrap-review [change-id]                                             |
|  +-- Load all artifacts + source design                                   |
|  +-- Spawn plan-reviewer for comprehensive validation                     |
|  +-- Output: APPROVED or REVISE with prioritized issues                   |
|                                                                           |
|  USER CHECKPOINT: Fix issues or proceed                                   |
+---------------------------------------------------------------------------+
                                    |
                                    v
+---------------------------------------------------------------------------+
|  PHASE 4: IMPLEMENTATION (Native OpenSpec)                                |
|                                                                           |
|  /opsx:apply    - Implement tasks                                         |
|  /opsx:verify   - Validate implementation                                 |
|  /opsx:archive  - Archive completed change                                |
+---------------------------------------------------------------------------+
```

### Component Relationships

```
+--[ COMMANDS (User entry points) ]------------------------------------------+
|                                                                            |
|  /claptrap-brainstorm     /claptrap-propose      /claptrap-review          |
|         |                        |                      |                  |
|         | invokes                | invokes              | invokes          |
|         v                        v                      v                  |
+--[ SKILLS (Reusable playbooks) ]-------------------------------------------+
|                                                                            |
|  claptrap-brainstorming        claptrap-propose                            |
|  claptrap-memory               claptrap-spawn-subagent                     |
|         |                             |                                    |
|         | spawns                      | spawns                             |
|         v                             v                                    |
+--[ AGENTS (Specialized subagents) ]----------------------------------------+
|                                                                            |
|  research           alignment-reviewer        feasibility-reviewer         |
|  ui-designer        plan-reviewer             code-reviewer                |
|                                                                            |
+--[ EXTERNAL: OpenSpec CLI ]------------------------------------------------+
|                                                                            |
|  openspec new       openspec instructions     openspec validate            |
|  /opsx:apply        /opsx:verify              /opsx:archive                |
+----------------------------------------------------------------------------+
```

---

## Goals Fulfilled

This workflow addresses the project goals defined in [GOALS.md](../GOALS.md):

| Goal | How Addressed |
|------|---------------|
| **Simple** | 3 commands (brainstorm, propose, review) + native OpenSpec for implementation |
| **Provider-agnostic** | Works with Claude, Copilot, Cursor, Codex, Gemini, OpenCode |
| **Environment-agnostic** | Markdown-based playbooks, no provider-specific features |
| **Easy to install** | Single installer, sensible defaults, < 5 minutes |
| **Modular** | Skills are self-contained, agents have single responsibilities |
| **Maintainable** | Uses OpenSpec CLI for artifact rules (updates flow through) |
| **Built on OSS** | Leverages OpenSpec for change management |

---

## Commands

### `/claptrap-brainstorm`

**Purpose**: Turn raw ideas into validated design documents through guided dialogue.

**Invocation**:
```
/claptrap-brainstorm "Add user authentication with OAuth support"
```

**What happens**:
1. Reads `.claptrap/memories.md` for prior decisions and patterns
2. Asks 3-5 clarifying questions about goals, scope, constraints (max 2 rounds)
3. Spawns research/explore subagents if external docs or codebase analysis needed
4. Generates design section by section, validating with user
5. Creates `.claptrap/designs/<feature-slug>/design.md`
6. Writes memory entries for significant decisions

**Output**: Design document at `.claptrap/designs/<slug>/design.md`

**Template**: [src/designs/TEMPLATE.md](../src/designs/TEMPLATE.md)

---

### `/claptrap-propose`

**Purpose**: Generate OpenSpec artifacts (proposal, specs, tasks) from an approved design.

**Invocations**:
```
/claptrap-propose .claptrap/designs/user-auth/design.md
/claptrap-propose                                        # auto-detect most recent
/claptrap-propose --regenerate proposal|specs|tasks|all --change <id>
```

**What happens**:
1. Reads memory context and validates design has required sections
2. Creates OpenSpec change directory via `openspec new <name>`
3. Generates `proposal.md` using OpenSpec instructions
4. Spawns alignment-reviewer to validate proposal matches design (max 2 fix cycles)
5. Generates `specs/**/spec.md` for each capability
6. Spawns feasibility-reviewer to validate specs are implementable (max 2 fix cycles)
7. Generates `tasks.md` with numbered task groups
8. Links artifacts to source design via `.source` file
9. Updates design's `## OpenSpec Proposals` section with link

**Outputs**:
```
openspec/changes/<change-id>/
+-- .source              # Path to source design.md
+-- proposal.md          # Why, What, Capabilities, Impact
+-- specs/
|   +-- <capability>/
|       +-- spec.md      # Requirements with WHEN/THEN scenarios
+-- tasks.md             # Checkbox implementation steps
```


---

### `/claptrap-review`

**Purpose**: Validate all artifacts against the source design before implementation.

**Invocations**:
```
/claptrap-review user-auth
/claptrap-review                    # auto-detect most recent
/claptrap-review --force            # proceed despite issues (documents accepted risk)
```

**What happens**:
1. Reads `.source` to find the design document
2. Loads all artifacts: design, proposal, specs, tasks
3. Spawns plan-reviewer with comprehensive validation checklist
4. Reports verdict: `APPROVED` or `REVISE` with prioritized issues

**Validation checks**:
1. Proposal.Why aligns with Design.Intent
2. Proposal.Capabilities covers Design.Scope.InScope
3. Proposal.Impact addresses Design.Key Decisions
4. Specs cover all Design.Acceptance Criteria
5. Specs scenarios are testable (WHEN/THEN format)
6. Tasks cover all Specs requirements
7. Tasks maintain correct sequencing (no task depends on later task)
8. No orphaned or unreferenced items

**Output**: `APPROVED: <summary>` or `REVISE:` with Must fix / Should fix / Nice to have items

---

### `/claptrap-refactor`

**Purpose**: Refactor code for simplicity and readability while preserving behavior.

**Invocation**:
```
/claptrap-refactor src/services/auth.ts
```

This command operates independently of the brainstorm->propose->review flow and can be used for targeted code improvements.

---

## Skills

Skills are reusable playbooks that commands invoke. Each skill has a `SKILL.md` file with detailed instructions.

| Skill | Purpose | Used By |
|-------|---------|---------|
| `claptrap-brainstorming` | Dialogue-driven design discovery | `/claptrap-brainstorm` |
| `claptrap-propose` | Design to OpenSpec artifact extraction | `/claptrap-propose` |
| `claptrap-memory` | Read/write project decisions and patterns | All commands |
| `claptrap-spawn-subagent` | Spawn agents with fresh context | Commands needing specialized work |
| `claptrap-refactor` | Code simplification patterns | `/claptrap-refactor` |

### Other Skills

| Skill | Purpose |
|-------|---------|
| `claptrap-code-conventions` | Load language-specific style guidelines |
| `claptrap-code-review` | Review code changes against requirements |
| `snowflake` | Execute Snowflake SQL queries |

Full registry: [src/skills/AGENTS.md](../src/skills/AGENTS.md)

---

## Agents

Agents are specialized subagents spawned by commands and skills. Each agent has fresh context and bounded scope.

| Agent | Purpose | Spawned By | Output |
|-------|---------|------------|--------|
| `alignment-reviewer` | Validate proposal matches design | `/claptrap-propose` | `ALIGNED` or `GAPS` |
| `feasibility-reviewer` | Validate specs are implementable | `/claptrap-propose` | `FEASIBLE` or `CONCERNS` |
| `plan-reviewer` | Comprehensive artifact validation | `/claptrap-review` | `APPROVED` or `REVISE` |
| `code-reviewer` | Review code for correctness | `/opsx:apply` | Structured feedback |
| `research` | Research external docs/APIs | Brainstorm, propose | Developer reference |
| `claptrap-explore-project` | Explore codebase patterns/structure | Brainstorm, propose | Context summary |
| `ui-designer` | Design UI specifications | Brainstorm (if needed) | UI spec |

Full registry: [src/agents/AGENTS.md](../src/agents/AGENTS.md)

---

## File Structure

### After Installation

```
your-project/
+-- .claptrap/
|   +-- code-conventions/        # Language style guides
|   +-- designs/                 # Your design documents
|   |   +-- TEMPLATE.md          # Design template
|   |   +-- example-feature/     # Example design
|   +-- memories.md              # Project memory
|
+-- .cursor/                     # (or .github/, .opencode/, .claude/, etc.)
|   +-- agents/                  # Agent definitions
|   +-- commands/                # Command workflows
|   +-- skills/                  # Skill playbooks
|
+-- openspec/                    # Created by openspec init
|   +-- config.yaml              # OpenSpec configuration
|   +-- changes/                 # Active changes
|   +-- specs/                   # Main specs (synced from changes)
|
+-- AGENTS.md                    # Updated with claptrap instructions
```

### After Running Workflow

```
.claptrap/designs/user-auth/
+-- design.md                    # Created by /claptrap-brainstorm

openspec/changes/user-auth/
+-- .source                      # Link back to design.md
+-- proposal.md                  # Created by /claptrap-propose
+-- specs/
|   +-- oauth-integration/
|       +-- spec.md
+-- tasks.md
```

---

## Artifact Flow

```
design.md (comprehensive source)
    |
    +---> proposal.md
    |        Intent -> Why
    |        Scope.InScope -> What Changes, Capabilities
    |        Scope.OutOfScope -> Non-Goals
    |        Key Decisions -> Impact
    |
    +---> specs/*.md
    |        Acceptance Criteria -> Requirements
    |        Each criterion -> WHEN/THEN scenarios
    |        Key Decisions -> Constraints
    |
    +---> tasks.md
             Architecture.Components -> Task groups
             Package Structure -> File creation tasks
             Acceptance Criteria -> Verification tasks
```

Every generated artifact includes a source comment:
```markdown
<!-- Source: ../../../.claptrap/designs/user-auth/design.md -->
```

---

## Memory System

The memory system captures project decisions, patterns, and lessons learned at `.claptrap/memories.md`.

**When memories are written**:
- End of `/claptrap-brainstorm` (significant design decisions)
- End of `/claptrap-propose` (architecture patterns, constraints)
- When user accepts risk via `--force` flag

**When memories are read**:
- Start of every command (provides context for agent decisions)

**Memory format**:
```markdown
---
## <Decision Title>
Type: decision | Date: YYYY-MM-DD | Tags: feature-slug, architecture

<1-3 sentences about the decision and rationale>
---
```

Full documentation: [src/skills/claptrap-memory/SKILL.md](../src/skills/claptrap-memory/SKILL.md)

---

## Updating Claptrap

### Re-running the Installer

Safe to run multiple times from your project directory:

```bash
python ~/projects/claptrap/bootstrap/install.py
```

What happens:
- Provider directory files are overwritten with latest versions
- Existing `memories.md` is preserved
- `AGENTS.md` claptrap section is updated in place
- `.gitignore` entries are only added if missing

### OpenSpec Updates

OpenSpec is updated automatically by the installer. Manual update:

```bash
npm install -g @fission-ai/openspec@latest
openspec update  # Update project integration
```

Minimum required version: **1.0.2**

If OpenSpec is below minimum version, the installer warns that `/claptrap-propose` may not work correctly.

### Checking Versions

```bash
openspec --version      # Check OpenSpec version
npm list -g @fission-ai/openspec  # Check installed version
```

---

## OpenSpec Integration

### CLI Commands Used by Claptrap

| Command | When | Purpose |
|---------|------|---------|
| `openspec new <name>` | `/claptrap-propose` start | Create change directory |
| `openspec instructions proposal --json` | Generating proposal | Get schema-aware rules |
| `openspec instructions specs --json` | Generating specs | Get spec template |
| `openspec instructions tasks --json` | Generating tasks | Get tasks template |
| `openspec validate --strict --no-interactive` | After generation | Validate artifacts |

### Commands Deferred to Native OpenSpec

| Command | Purpose |
|---------|---------|
| `/opsx:apply` | Implement tasks from reviewed change |
| `/opsx:verify` | Validate implementation matches specs |
| `/opsx:archive` | Archive completed change |

### What Claptrap Skips

- OpenSpec's optional `design.md` artifact (redundant with brainstorm output)
- `/opsx:new`, `/opsx:continue`, `/opsx:ff` (Claptrap manages its own flow)

---

## Troubleshooting

### "OpenSpec CLI not found"

```bash
npm install -g @fission-ai/openspec@latest
```

### "Design missing required sections"

The design must have: `## Intent`, `## Scope` (with In/Out), `## Acceptance Criteria`, `## Architecture Overview`, `## Key Decisions`

Run `/claptrap-brainstorm` to create a properly structured design.

### "Alignment review keeps failing"

After 2 cycles, the command stops. Check:
1. Does proposal.Why match design.Intent?
2. Are all Scope.InScope items represented in Capabilities?
3. Is there a source link in the proposal?

### "Review says REVISE"

Options:
1. Fix the issues in the artifacts
2. Re-run `/claptrap-propose --regenerate <artifact>` to regenerate specific parts
3. Use `--force` to proceed (documents accepted risk in memory)

---

## Additional Resources

- [Installation Guide](../bootstrap/README.md)
- [Design Template](../src/designs/TEMPLATE.md)
- [Example Design](../src/designs/example-feature/design.md)
- [OpenSpec Documentation](https://github.com/Fission-AI/OpenSpec)
- [MCP Server Setup](../bootstrap/mcp_setup.md)
