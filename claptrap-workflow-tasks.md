# Claptrap Workflow Refactor — Implementation Task List

**Source of truth**: `claptrap-workflow-proposal.md` (dated 2026-01-28)  
**Goal**: Implement the new workflow entry points:

- `/claptrap-brainstorm` → produces `.claptrap/designs/<feature-slug>/design.md`
- `/claptrap-propose` → generates `openspec/changes/<change-id>/{proposal.md, specs/**, tasks.md}` and links back to the design
- `/claptrap-review` → validates design ↔ proposal ↔ specs ↔ tasks before implementation
- Implementation remains native OpenSpec: `/opsx:apply`, `/opsx:verify`, `/opsx:archive`

---

## Definition of Done (do not claim done until ALL are true)

- [ ] New command files exist:
  - `src/commands/claptrap-propose.md`
  - `src/commands/claptrap-review.md`
- [ ] New propose skill exists and is complete:
  - `src/skills/claptrap-propose/SKILL.md`
  - `src/skills/claptrap-propose/templates/proposal-hints.md`
  - `src/skills/claptrap-propose/templates/spec-hints.md`
  - `src/skills/claptrap-propose/templates/tasks-hints.md`
- [ ] Brainstorm design template is updated and consistent in BOTH locations:
  - `src/designs/TEMPLATE.md`
  - `src/skills/claptrap-brainstorming/templates/design.md`
- [ ] Review agents match the new artifact flow:
  - `src/agents/alignment-reviewer.md` checks `design.md` ↔ `proposal.md`
  - `src/agents/feasibility-reviewer.md` checks `proposal.md` + `specs/*.md` + `tasks.md` + `design.md`
  - `src/agents/plan-reviewer.md` checks full artifact set for `/claptrap-review`
- [ ] Deprecated components are removed:
  - `src/commands/propose.md`
  - `src/commands/implement-change.md`
  - `src/commands/archive-change.md`
  - `src/commands/finish-openspec-change.md`
  - `src/skills/design-to-proposal/`
  - `src/skills/claptrap-openspec-proposal/`
  - `src/skills/claptrap-opecspec-design/` (typo + unused stub)
- [ ] Registries are updated and contain **no** references to removed components:
  - `src/commands/AGENTS.md`
  - `src/skills/AGENTS.md`
  - `src/agents/AGENTS.md`
  - `src/AGENTS.md`
- [ ] User-facing docs are updated and contain **no** references to removed components:
  - `README.md`
  - `bootstrap/README.md`
- [ ] Installer behavior is still correct and documented:
  - `bootstrap/install.py` has a minimum OpenSpec version constant and warns when too old
- [ ] Repo-wide search finds **zero** stale references:
  - No `/propose`, `/implement-change`, `/archive-change`, `/finish-openspec-change`
  - No `design-to-proposal`, `claptrap-openspec-proposal`, `claptrap-opecspec-design`

---


## Global Rules (follow exactly)

1. **Only edit canonical sources** under `src/` and `bootstrap/`. Do not hand-edit generated adapter outputs (`.opencode/`, `.claude/`, `.cursor/`, `.github/`, `.codex/`, `.gemini/`) unless a task explicitly says to regenerate them.
2. After each phase, you MUST do the “Phase Review” tasks and fix any mistakes before starting the next phase.
3. When a task says “copy Appendix X exactly”, copy/paste exactly. Do not “improve” wording.
4. When a task says “keep YAML frontmatter unchanged”, do not modify anything between the first `---` and the next `---`.

---

# Phase 0 — Pre-flight (no workflow behavior changes yet)


## 0.2 Inventory current state (write it down before changing anything)

- [ ] 0.2.1 Run `ls src/commands` and record the exact filenames that exist right now.
- [ ] 0.2.2 Run `ls src/skills` and record the exact directory names that exist right now.
- [ ] 0.2.3 Run `ls src/agents` and record the exact filenames that exist right now.
- [ ] 0.2.4 Run `rg -n \"(/propose|/implement-change|/archive-change|/finish-openspec-change)\" src README.md bootstrap/README.md` and save the output somewhere (copy/paste into a scratch note). You will re-run this later and expect **zero matches**.

## 0.3 Confirm OpenSpec CLI command syntax (do NOT assume proposal text is correct)

- [ ] 0.3.1 Run `openspec --help` and confirm you see these commands (exact or equivalent):
  - `openspec new change <name>`
  - `openspec instructions --change <id> --json`
  - `openspec validate --strict --no-interactive`
- [ ] 0.3.2 Run `openspec --version` and write down the version number. You will use it to set `OPENSPEC_MIN_VERSION` later.

## Phase 0 Review (mandatory)

- [ ] 0.R.1 Confirm no files were modified by Phase 0 (`git diff` must be empty).
- [ ] 0.R.2 If `git diff` is not empty, revert changes until `git diff` is empty, then re-check 0.R.1.

---

# Phase 1 — Add new workflow entry points (new command + new skill)

## 1.1 Create `/claptrap-propose` command (NEW FILE)

- [ ] 1.1.1 Create `src/commands/claptrap-propose.md`.
- [ ] 1.1.2 Paste **Appendix B** into `src/commands/claptrap-propose.md` (entire file).
- [ ] 1.1.3 Verify the YAML frontmatter `name:` is exactly `claptrap-propose`.
- [ ] 1.1.4 Verify the command references these skills by exact name:
  - `claptrap-memory`
  - `claptrap-spawn-subagent`
  - `claptrap-propose`

## 1.2 Create `/claptrap-review` command (NEW FILE)

- [ ] 1.2.1 Create `src/commands/claptrap-review.md`.
- [ ] 1.2.2 Paste **Appendix C** into `src/commands/claptrap-review.md` (entire file).
- [ ] 1.2.3 Verify the YAML frontmatter `name:` is exactly `claptrap-review`.
- [ ] 1.2.4 Verify the command references these skills/agents by exact name:
  - Skill: `claptrap-memory`
  - Skill: `claptrap-spawn-subagent`
  - Agent: `plan-reviewer`

## 1.3 Create `claptrap-propose` skill (NEW FILE + NEW TEMPLATES)

- [ ] 1.3.1 Create `src/skills/claptrap-propose/SKILL.md`.
- [ ] 1.3.2 Paste **Appendix D** into `src/skills/claptrap-propose/SKILL.md` (entire file).
- [ ] 1.3.3 Create these files (create directories as needed):
  - `src/skills/claptrap-propose/templates/proposal-hints.md`
  - `src/skills/claptrap-propose/templates/spec-hints.md`
  - `src/skills/claptrap-propose/templates/tasks-hints.md`
- [ ] 1.3.4 Paste the matching appendices into each file:
  - proposal-hints.md ← **Appendix E**
  - spec-hints.md ← **Appendix F**
  - tasks-hints.md ← **Appendix G**
- [ ] 1.3.5 Confirm `src/skills/claptrap-propose/templates/` contains exactly these three `*-hints.md` files (and nothing empty/placeholder).

## Phase 1 Review (mandatory)

- [ ] 1.R.1 Run `rg -n \"name: \\\"claptrap-(propose|review)\\\"\" src/commands` and confirm it matches the two new files.
- [ ] 1.R.2 Run `test -f src/skills/claptrap-propose/SKILL.md && echo OK` and confirm it prints `OK`.
- [ ] 1.R.3 Run `ls src/skills/claptrap-propose/templates` and confirm the three hints files exist.
- [ ] 1.R.4 If any of 1.R.1–1.R.3 fail, fix the filesystem/paths until they pass, then re-run 1.R.1–1.R.3.

---

# Phase 2 — Refactor brainstorm output (design template + brainstorm command/skill)

## 2.1 Update the design template (canonical template)

- [ ] 2.1.1 Open `src/designs/TEMPLATE.md`.
- [ ] 2.1.2 Replace the entire file contents with **Appendix A**.
- [ ] 2.1.3 Confirm the file starts with the two HTML comments and then `# Design: <Feature Name>`.
- [ ] 2.1.4 Confirm it contains these REQUIRED headings exactly once each:
  - `## Intent`
  - `## Scope`
  - `## Acceptance Criteria`
  - `## Architecture Overview`
  - `## Key Decisions`
  - `## Open Questions`
  - `## Next Steps`
  - `## OpenSpec Proposals`

## 2.2 Update the brainstorm skill’s embedded template (must match canonical)

- [ ] 2.2.1 Open `src/skills/claptrap-brainstorming/templates/design.md`.
- [ ] 2.2.2 Replace the entire file contents with **Appendix A** (YES: exactly the same as `src/designs/TEMPLATE.md`).
- [ ] 2.2.3 Confirm the first character in the file is `<` (this fixes the current stray leading `e` bug).

## 2.3 Update the example design (demonstrate new template sections)

- [ ] 2.3.1 Open `src/designs/example-feature/design.md`.
- [ ] 2.3.2 Replace the entire file contents with **Appendix J**.
- [ ] 2.3.3 Confirm the example includes `### Package Structure` and `### Core Types`.
- [ ] 2.3.4 Confirm the example includes an `## OpenSpec Proposals` section.

## 2.4 Update the `/claptrap-brainstorm` command to match the new workflow

- [ ] 2.4.1 Open `src/commands/claptrap-brainstorm.md`.
- [ ] 2.4.2 Keep YAML frontmatter unchanged.
- [ ] 2.4.3 Replace everything after the YAML frontmatter with **Appendix H**.
- [ ] 2.4.4 Confirm the command no longer references `openspec-create-proposal` (it must NOT).
- [ ] 2.4.5 Confirm the command’s output path is exactly `.claptrap/designs/<feature-slug>/design.md`.
- [ ] 2.4.6 Confirm the command’s “next step” explicitly tells the user to run `/claptrap-propose`.

## 2.5 Update the `claptrap-brainstorming` skill to include memory + new dialogue bounds

- [ ] 2.5.1 Open `src/skills/claptrap-brainstorming/SKILL.md`.
- [ ] 2.5.2 Keep YAML frontmatter unchanged.
- [ ] 2.5.3 Replace everything after the YAML frontmatter with **Appendix I**.
- [ ] 2.5.4 Confirm the skill says:
  - Ask **3–5** clarifying questions in a single “round”
  - Allow **max 2 rounds**
  - Read `.claptrap/memories.md` before brainstorming
  - Write memory entries for significant decisions after finalizing
- [ ] 2.5.5 Confirm the skill tells the agent to output the final design using `templates/design.md` (which is the file you updated in task 2.2).

## Phase 2 Review (mandatory)

- [ ] 2.R.1 Run `diff -u src/designs/TEMPLATE.md src/skills/claptrap-brainstorming/templates/design.md` and confirm there is **no diff output**.
- [ ] 2.R.2 Run `rg -n \"openspec-create-proposal\" src/commands/claptrap-brainstorm.md src/skills/claptrap-brainstorming/SKILL.md` and confirm there are **zero matches**.
- [ ] 2.R.3 Run `rg -n \"^## OpenSpec Proposals\" -n src/designs/TEMPLATE.md src/skills/claptrap-brainstorming/templates/design.md src/designs/example-feature/design.md` and confirm it matches all three files.
- [ ] 2.R.4 If any of 2.R.1–2.R.3 fail, fix the incorrect file(s) and re-run 2.R.1–2.R.3 until they pass.

---

# Phase 3 — Refactor review agents for the new artifact flow

## 3.1 Update alignment-reviewer (design ↔ proposal)

- [ ] 3.1.1 Open `src/agents/alignment-reviewer.md`.
- [ ] 3.1.2 Keep YAML frontmatter unchanged.
- [ ] 3.1.3 Replace everything after YAML frontmatter with **Appendix K**.
- [ ] 3.1.4 Confirm the Subagent Interface explicitly requires:
  - Input 1: `design.md`
  - Input 2: `proposal.md`
- [ ] 3.1.5 Confirm the output format is exactly `ALIGNED` or `GAPS:` with numbered severity items.

## 3.2 Update feasibility-reviewer (proposal + specs + tasks + design)

- [ ] 3.2.1 Open `src/agents/feasibility-reviewer.md`.
- [ ] 3.2.2 Keep YAML frontmatter unchanged.
- [ ] 3.2.3 Replace everything after YAML frontmatter with **Appendix L**.
- [ ] 3.2.4 Confirm the Subagent Interface explicitly requires:
  - Input 1: `proposal.md`
  - Input 2: `specs/*.md` (ALL)
  - Input 3: `tasks.md`
  - Input 4: `design.md`
- [ ] 3.2.5 Confirm the output format is exactly `FEASIBLE` or `CONCERNS:` with numbered severity items.

## 3.3 Refactor plan-reviewer (holistic validation for `/claptrap-review`)

- [ ] 3.3.1 Open `src/agents/plan-reviewer.md`.
- [ ] 3.3.2 Keep YAML frontmatter unchanged.
- [ ] 3.3.3 Replace everything after YAML frontmatter with **Appendix M**.
- [ ] 3.3.4 Confirm the checklist includes all 8 validation checks from the proposal.
- [ ] 3.3.5 Confirm the output format is exactly `APPROVED:` or `REVISE:` with prioritized issues.

## Phase 3 Review (mandatory)

- [ ] 3.R.1 Run `rg -n \"Input:.*design\\.md\" src/agents/*.md` and confirm all three reviewers reference `design.md` in their input interfaces.
- [ ] 3.R.2 Run `rg -n \"^(ALIGNED|GAPS:|FEASIBLE|CONCERNS:|APPROVED:|REVISE:)\" src/agents/*.md` and confirm each file documents the correct output tokens.
- [ ] 3.R.3 If any reviewer still references “spec deltas” as a required input, remove that requirement and re-check 3.R.1–3.R.2.

---

# Phase 4 — Remove deprecated components + update registries/docs/installer

## 4.1 Delete deprecated commands

- [ ] 4.1.1 Delete `src/commands/propose.md`.
- [ ] 4.1.2 Delete `src/commands/implement-change.md`.
- [ ] 4.1.3 Delete `src/commands/archive-change.md`.
- [ ] 4.1.4 Delete `src/commands/finish-openspec-change.md`.
- [ ] 4.1.5 Confirm `ls src/commands` no longer lists any of those four filenames.

## 4.2 Delete deprecated skills

- [ ] 4.2.1 Delete directory `src/skills/design-to-proposal/` (entire directory).
- [ ] 4.2.2 Delete directory `src/skills/claptrap-openspec-proposal/` (entire directory).
- [ ] 4.2.3 Delete directory `src/skills/claptrap-opecspec-design/` (entire directory).
- [ ] 4.2.4 Confirm `ls src/skills` no longer lists those three directories.

## 4.3 Update command registry (`src/commands/AGENTS.md`)

- [ ] 4.3.1 Open `src/commands/AGENTS.md`.
- [ ] 4.3.2 In the “Available Commands” table, replace the entire table body so it lists ONLY:
  - `claptrap-brainstorm`
  - `claptrap-propose`
  - `claptrap-review`
  - `claptrap-refactor`
- [ ] 4.3.3 Add an “Invocation” column and include the exact invocations from the proposal.
- [ ] 4.3.4 Remove any mention of `propose`, `implement-change`, `archive-change`, `finish-openspec-change`.

## 4.4 Update skill registry (`src/skills/AGENTS.md`)

- [ ] 4.4.1 Open `src/skills/AGENTS.md`.
- [ ] 4.4.2 Remove registry entries for:
  - `design-to-proposal`
  - `openspec-create-proposal` (if it’s only present as a legacy entry)
  - `claptrap-openspec-proposal`
  - `claptrap-opecspec-design`
- [ ] 4.4.3 Add registry entries for (each must include: Path, Purpose, Use when, Templates (if any)):
  - `claptrap-brainstorming` → `skills/claptrap-brainstorming/SKILL.md`
  - `claptrap-propose` → `skills/claptrap-propose/SKILL.md`
  - `claptrap-memory` → `skills/claptrap-memory/SKILL.md`
  - `claptrap-spawn-subagent` → `skills/claptrap-spawn-subagent/SKILL.md`
  - `claptrap-refactor` → `skills/claptrap-refactor/SKILL.md`
- [ ] 4.4.4 If you keep any non-workflow skills (example: `snowflake`), list them in a separate “Other Skills” subsection.

## 4.5 Update agent registry (`src/agents/AGENTS.md`)

- [ ] 4.5.1 Replace the “Core Pipeline” section so it matches the new flow:
  - Propose: `/claptrap-propose` (spawns alignment + feasibility)
  - Review: `/claptrap-review` (spawns plan-reviewer)
  - Implementation: `/opsx:apply` (native OpenSpec; may spawn code-reviewer)
- [ ] 4.5.2 Update the “Agent Spawning Map” so it matches:
  - alignment-reviewer spawned by `/claptrap-propose`
  - feasibility-reviewer spawned by `/claptrap-propose`
  - plan-reviewer spawned by `/claptrap-review`
  - code-reviewer spawned by `/opsx:apply` (native step)
  - research + ui-designer spawned by `/claptrap-brainstorm` and/or `/claptrap-propose` when needed
- [ ] 4.5.3 Remove any mention of `/propose`, `/implement-change`, `/archive-change`.

## 4.6 Update `src/AGENTS.md` to document the new workflow

- [ ] 4.6.1 Open `src/AGENTS.md`.
- [ ] 4.6.2 Append a “Workflow Overview” section that contains:
  - The 3-phase flow summary
  - The note that implementation uses native OpenSpec commands (`/opsx:apply`, `/opsx:verify`, `/opsx:archive`)
- [ ] 4.6.3 Ensure `src/AGENTS.md` contains **no** references to removed commands.

## 4.7 Update root `README.md` (user-facing docs)

- [ ] 4.7.1 In `README.md`, update the “Usage” section so it lists ONLY:
  - `/claptrap-brainstorm`
  - `/claptrap-propose <design-path>`
  - `/claptrap-review <change-id>`
  - `/opsx:apply`, `/opsx:verify`, `/opsx:archive`
- [ ] 4.7.2 In `README.md`, update the “Designs” section:
  - Design docs live in `.claptrap/designs/<feature-slug>/design.md`
  - Template source is `src/designs/TEMPLATE.md` (repo) and is installed into `.claptrap/designs/TEMPLATE.md` (target projects)
- [ ] 4.7.3 Add the “Workflow selection guide” table from the proposal’s Concern 10 (Trivial/Small/Medium/Large/Complex).
- [ ] 4.7.4 Remove any mention of `/implement-change`, `/archive-change`, `/finish-openspec-change`, and `/propose`.

## 4.8 Update `bootstrap/README.md` (installer docs)

- [ ] 4.8.1 Update the “Directory Structure After Install” block to keep it accurate:
  - `.claptrap/` contains: `code-conventions/`, `designs/`, `memories.md`
  - Provider directory contains: `agents/`, `commands/`, and `skills/` as supported by the provider
- [ ] 4.8.2 Remove any “Usage” examples that reference removed commands.
- [ ] 4.8.3 Add a note that OpenSpec CLI is required for `/claptrap-propose` and `/opsx:*` commands.

## 4.9 Update installer OpenSpec version guard (`bootstrap/install.py`)

- [ ] 4.9.1 Open `bootstrap/install.py`.
- [ ] 4.9.2 Add a constant near the top of the OpenSpec section:
  - `OPENSPEC_MIN_VERSION = \"1.0.0\"` (or the exact version from Phase 0 if you choose a higher minimum)
- [ ] 4.9.3 Add a post-install check:
  - If OpenSpec is installed and the version is **below** `OPENSPEC_MIN_VERSION`, print a warning explaining that `/claptrap-propose` may not work correctly.
  - If version is **>=** minimum, print a success message.
- [ ] 4.9.4 Do NOT change any installer behavior unrelated to OpenSpec version checking.

## Phase 4 Review (mandatory)

- [ ] 4.R.1 Run `rg -n \"(/propose|/implement-change|/archive-change|/finish-openspec-change)\" src README.md bootstrap/README.md` and confirm **zero matches**.
- [ ] 4.R.2 Run `rg -n \"(design-to-proposal|claptrap-openspec-proposal|claptrap-opecspec-design)\" src README.md bootstrap/README.md` and confirm **zero matches**.
- [ ] 4.R.3 Run `ls src/commands` and confirm only intended command files remain.
- [ ] 4.R.4 Run `ls src/skills` and confirm removed directories are gone and `claptrap-propose/` exists with its templates.
- [ ] 4.R.5 If any stale references exist, fix them immediately and re-run 4.R.1–4.R.4.

---

# Phase 5 — Verification (structure checks + smoke test)

## 5.1 Structure validation

- [ ] 5.1.1 Confirm every command file in `src/commands/` starts with YAML frontmatter (`---`).
- [ ] 5.1.2 Confirm every skill directory in `src/skills/` contains `SKILL.md`.
- [ ] 5.1.3 Confirm these specific paths exist:
  - `src/commands/claptrap-brainstorm.md`
  - `src/commands/claptrap-propose.md`
  - `src/commands/claptrap-review.md`
  - `src/skills/claptrap-brainstorming/SKILL.md`
  - `src/skills/claptrap-propose/SKILL.md`
  - `src/skills/claptrap-propose/templates/proposal-hints.md`
  - `src/skills/claptrap-propose/templates/spec-hints.md`
  - `src/skills/claptrap-propose/templates/tasks-hints.md`

## 5.2 Cross-reference validation

- [ ] 5.2.1 Run `rg -n \"claptrap-propose\" src/commands src/skills src/agents` and confirm references make sense (no broken names).
- [ ] 5.2.2 Run `rg -n \"claptrap-brainstorming\" src/commands src/skills` and confirm brainstorm command references the skill.
- [ ] 5.2.3 Run `rg -n \"plan-reviewer\" src/commands src/agents` and confirm `/claptrap-review` spawns the plan-reviewer agent.
- [ ] 5.2.4 Run `rg -n \"\\.source\" src/commands src/skills` and confirm `/claptrap-propose` writes it and `/claptrap-review` reads it.

## 5.3 End-to-end smoke test (manual, do not commit generated artifacts)

- [ ] 5.3.1 In a temporary sandbox project directory (NOT this repo), run the installer (`bootstrap/install.py`) and select a provider you can run locally.
- [ ] 5.3.2 In that sandbox project, run:
  - `/claptrap-brainstorm \"Test feature for workflow validation\"`
  - Ensure it creates `.claptrap/designs/test-feature/design.md`
- [ ] 5.3.3 Then run `/claptrap-propose` (no args) and confirm it:
  - Creates an OpenSpec change directory
  - Generates proposal/specs/tasks
  - Writes `.source`
  - Updates the design with a link in `## OpenSpec Proposals`
- [ ] 5.3.4 Then run `/claptrap-review` (no args) and confirm it:
  - Reads `.source`
  - Runs plan-reviewer
  - Outputs either `APPROVED:` or `REVISE:` with actionable issues

## Phase 5 Review (mandatory)

- [ ] 5.R.1 Re-run the Phase 4 searches (4.R.1 and 4.R.2) and confirm still zero matches.
- [ ] 5.R.2 Run `git diff` and manually scan that:
  - Only intended files changed
  - No accidental edits to generated adapter directories
- [ ] 5.R.3 If anything is wrong, fix it now and repeat 5.R.1–5.R.2.

---

# Appendices (copy/paste blocks)

## Appendix A — Design Template (copy exactly)

````markdown
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
3. Review and approve proposal/specs/tasks
4. Implement via `/opsx:apply`

## OpenSpec Proposals

<!-- Auto-populated by /claptrap-propose -->
- (none yet)
````

## Appendix B — `src/commands/claptrap-propose.md` (copy exactly)

```markdown
---
name: "claptrap-propose"
description: "Generate OpenSpec artifacts (proposal, specs, tasks) from an approved design.md, with alignment + feasibility review."
model: claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# /claptrap-propose

Generate OpenSpec artifacts from a design document. This command does NOT implement code.

## Inputs

Supported invocations:
- `/claptrap-propose .claptrap/designs/<slug>/design.md`
- `/claptrap-propose` (auto-detect most recent design)

Optional flags (parse from `$ARGUMENTS`):
- `--regenerate proposal|specs|tasks|all` (regenerate inside an existing change)
- `--change <change-id>` (REQUIRED when using `--regenerate`)

## Outputs

- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/specs/**/spec.md`
- `openspec/changes/<change-id>/tasks.md`
- `openspec/changes/<change-id>/.source` (path to the source `design.md`, relative to the change directory)

## Skills

Load and use these skills:
- `claptrap-memory` (read at start; write at end if useful)
- `claptrap-spawn-subagent` (for reviewer agents)
- `claptrap-propose` (the core step-by-step extraction workflow)

## Workflow Steps

1. Invoke `claptrap-memory` and read `.claptrap/memories.md` for context (decisions, patterns, constraints).
2. Invoke the `claptrap-propose` skill and follow it EXACTLY.
3. STOP.

**Design path / flags:** `$ARGUMENTS`
```

## Appendix C — `src/commands/claptrap-review.md` (copy exactly)

```markdown
---
name: "claptrap-review"
description: "Validate proposal/specs/tasks against the source design document before implementation."
model: claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.2-codex
---

# /claptrap-review

Validate all OpenSpec artifacts against the source design document. This is the explicit quality gate before `/opsx:apply`.

## Inputs

Supported invocations:
- `/claptrap-review <change-id>`
- `/claptrap-review` (auto-detect most recent change)

Optional flags (parse from `$ARGUMENTS`):
- `--force` (user chooses to proceed even if verdict is REVISE; MUST write an accepted-risk memory)

## Inputs (files)

For change-id `<id>`, load:
- `openspec/changes/<id>/.source` → points to the design document path (relative to the change directory)
- `openspec/changes/<id>/proposal.md`
- `openspec/changes/<id>/specs/**/spec.md` (all specs)
- `openspec/changes/<id>/tasks.md`

## Skills

Load and use these skills:
- `claptrap-memory` (write only if user accepts risk or key decision emerges)
- `claptrap-spawn-subagent` (to run `plan-reviewer`)

## Workflow Steps

1. Resolve `<change-id>`:
   - If provided in `$ARGUMENTS`, use it.
   - Else: choose the most recently modified directory under `openspec/changes/` (exclude `openspec/changes/archive/`).
2. Read `.source` and resolve the full path to `design.md`:
   - Treat the `.source` content as a path RELATIVE TO `openspec/changes/<id>/`.
3. Read: `design.md`, `proposal.md`, all `spec.md` files, and `tasks.md`.
4. Spawn the `plan-reviewer` subagent with those artifacts as input.
5. Report the verdict exactly as `APPROVED:` or `REVISE:` (do not invent new verdict words).
6. If verdict is `REVISE`:
   - If user did NOT pass `--force`: tell them to return to `/claptrap-propose` to regenerate/fix artifacts.
   - If user DID pass `--force`: clearly list the issues and write a memory entry documenting the accepted risk.
7. STOP.

**Change id / flags:** `$ARGUMENTS`
```

## Appendix D — `src/skills/claptrap-propose/SKILL.md` (copy exactly)

```markdown
---
name: "claptrap-propose"
description: "Design → OpenSpec artifact extraction with alignment + feasibility review cycles."
---

# claptrap-propose

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

## Required dependencies

- OpenSpec CLI must be available in PATH (`openspec --version` must work).
- Project must have been initialized with OpenSpec (`openspec/config.yaml` exists).

If either requirement is missing:
1. Print the exact shell commands the user must run to fix it.
2. Ask the user to run them and paste the output.
3. STOP.

## Skills

Load the following skills:
- `claptrap-memory`
- `claptrap-spawn-subagent`

## File paths (source linking rules)

Assume the design is at:
`DESIGN_PATH = .claptrap/designs/<feature-slug>/design.md`

When writing OpenSpec artifacts under:
`openspec/changes/<change-id>/`

Use these rules:
1. Every generated artifact file MUST start with:
   `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
2. Write `openspec/changes/<change-id>/.source` containing EXACTLY:
   `../../../.claptrap/designs/<feature-slug>/design.md`
   (This path is relative to the directory containing `.source`.)
3. Update the design doc `## OpenSpec Proposals` list with:
   `- [<change-id>](../../../openspec/changes/<change-id>/proposal.md)`

## Process

### Step 0: Read memory

1. Invoke `claptrap-memory`.
2. Read `.claptrap/memories.md`.
3. Extract only relevant context (patterns/decisions that affect the design or artifacts).

### Step 1: Resolve design path

1. If `$ARGUMENTS` includes a `.md` path, treat it as the design path.
2. Else, auto-detect the most recent design by modified time:
   - Search for `.claptrap/designs/**/design.md`
   - Pick the newest by mtime
3. If no design is found, ask the user to run `/claptrap-brainstorm` first and STOP.

### Step 2: Validate design document shape (hard stop on missing required sections)

Confirm the design contains ALL required headings:
- `## Intent`
- `## Scope` (with `### In Scope` and `### Out of Scope`)
- `## Acceptance Criteria`
- `## Architecture Overview`
- `## Key Decisions`

If any required heading is missing:
1. List the missing heading(s).
2. Tell the user to fix the design first (or rerun `/claptrap-brainstorm`).
3. STOP.

### Step 3: Resolve change-id

1. Let `<feature-slug>` be the parent directory name of the design path (kebab-case).
2. Default `<change-id>` to `<feature-slug>`.
3. If `$ARGUMENTS` includes `--change <change-id>`, use that change-id instead.

### Step 4: Create or reuse the OpenSpec change directory

Case A — normal run (no `--regenerate`):
1. Run: `openspec new change <change-id>`
2. If this fails, STOP and report the error.

Case B — regeneration run (`--regenerate ...`):
1. Require `--change <change-id>` to be present.
2. Confirm `openspec/changes/<change-id>/` exists.
3. If it does not exist, STOP and tell the user to run normal `/claptrap-propose` first.

### Step 5: Generate proposal.md

1. Run: `openspec instructions proposal --change <change-id> --json`
2. Read `templates/proposal-hints.md` and apply the extraction rules.
3. Write `openspec/changes/<change-id>/proposal.md`:
   - Start with the source comment (see “File paths” rules above).
   - Follow the OpenSpec instruction structure.
   - Ensure it includes: Why, What Changes, Capabilities, Non-Goals, Impact, Source link.
4. OPTIONAL but recommended: run `openspec validate --strict --no-interactive --type change <change-id>` and fix any errors.

### Step 6: Alignment review (design ↔ proposal) — max 2 cycles

1. Spawn the `alignment-reviewer` subagent (via `claptrap-spawn-subagent`) with:
   - design.md (source)
   - proposal.md (generated)
2. If output is `ALIGNED`, continue.
3. If output is `GAPS`:
   - Apply the suggested fixes to proposal.md.
   - Re-run alignment review.
4. Stop after 2 total cycles. If still `GAPS`, summarize remaining issues and STOP.

### Step 7: Generate specs/**/spec.md

1. Run: `openspec instructions specs --change <change-id> --json`
2. Read `templates/spec-hints.md` and apply the extraction rules.
3. From proposal.md, extract the list of capability slugs under “Capabilities”.
4. For EACH capability slug `<cap>`:
   - Create directory: `openspec/changes/<change-id>/specs/<cap>/`
   - Write file: `openspec/changes/<change-id>/specs/<cap>/spec.md`
   - First line MUST be the source comment.
   - Convert each Acceptance Criteria checkbox into:
     - One Requirement
     - One or more Scenarios using WHEN/THEN format

### Step 8: Generate tasks.md

1. Run: `openspec instructions tasks --change <change-id> --json`
2. Read `templates/tasks-hints.md` and apply the extraction rules.
3. Write `openspec/changes/<change-id>/tasks.md`:
   - First line MUST be the source comment.
   - Use numbered task groups (1, 2, 3...) and numbered subtasks (1.1, 1.2...).
   - Include explicit verification steps mapping back to Acceptance Criteria and Specs.

### Step 9: Feasibility review (proposal + specs + tasks + design) — max 2 cycles

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

### Step 10: Link and finalize

1. Write `.source` file (see “File paths” rules above).
2. Update the design doc:
   - Ensure it has `## OpenSpec Proposals`
   - Add the proposal link entry for `<change-id>`
3. Use `claptrap-memory` to propose 1–3 candidate memories; only write those that are genuinely reusable.
4. Print a short summary with links to:
   - design.md
   - proposal.md
   - specs/
   - tasks.md

## Regeneration behavior

If user runs `/claptrap-propose --regenerate <artifact>`:
- Only overwrite the requested artifact(s).
- Do NOT create a new change directory.
- Preserve the source comment and `.source` file.
```

## Appendix E — `proposal-hints.md` (copy exactly)

```markdown
# Proposal Hints (Design → proposal.md)

Use this file as guidance when generating `openspec/changes/<change-id>/proposal.md`.

## Non-negotiables

- The first line of proposal.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Preserve scope discipline: do not add requirements that are not in the design.

## Extraction Rules

| Design Section | Proposal Section | Transformation |
|----------------|------------------|----------------|
| Intent | Why | Direct copy or light summarization (2–3 sentences) |
| Scope → In Scope | What Changes | Summarize to 2–3 sentences |
| Intent + Scope | Capabilities | Extract kebab-case capability slugs + one-line descriptions |
| Scope → Out of Scope | Non-Goals | Direct copy |
| Key Decisions | Impact → Key Decisions | Summarize each decision (keep rationale) |
| Architecture Overview → Components | Impact → Code Changes | List impacted areas/files/modules |

## Required Sections (proposal.md must include these headings)

- `## Why`
- `## What Changes`
- `## Capabilities`
- `## Non-Goals`
- `## Impact`
- `## Source`

## Source section (must be present)

Include a link back to the design document:

`Full design: [design.md](../../../.claptrap/designs/<feature-slug>/design.md)`
```

## Appendix F — `spec-hints.md` (copy exactly)

```markdown
# Spec Hints (Design → specs/**/spec.md)

Use this file as guidance when generating capability specs under:
`openspec/changes/<change-id>/specs/<capability>/spec.md`

## Non-negotiables

- The first line of every spec.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Every scenario MUST use WHEN/THEN bullets.

## Extraction Rules

| Design Section | Spec Section | Transformation |
|----------------|--------------|----------------|
| Acceptance Criteria | Requirements | Each checkbox criterion → one Requirement |
| Acceptance Criteria | Scenarios | Convert into WHEN/THEN scenarios (testable, observable outcomes) |
| Key Decisions | Constraints | Add as scenario conditions or explicit requirement notes |
| Architecture Overview → Core Types | References | Link back to design for type/interface definitions |

## Scenario format (required)

- **WHEN** <precondition or trigger>
- **THEN** <expected observable outcome>
```

## Appendix G — `tasks-hints.md` (copy exactly)

```markdown
# Tasks Hints (Design + Specs → tasks.md)

Use this file as guidance when generating:
`openspec/changes/<change-id>/tasks.md`

## Non-negotiables

- The first line of tasks.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Tasks MUST be checkboxes and MUST be numbered (1.1, 1.2, 2.1, ...).
- Include verification tasks that map back to Acceptance Criteria and spec scenarios.

## Extraction Rules

| Input | Tasks Output | Transformation |
|-------|-------------|----------------|
| Architecture Overview → Components | Task subtasks | Each component → subtasks for implementation + wiring |
| Architecture Overview → Package Structure | File tasks | Each directory/file → explicit creation/edit task |
| Specs scenarios | Verification tasks | Each scenario → at least one verification step |
| Acceptance Criteria | Verification tasks | Each criterion → explicit verification checkbox |

## Minimum required groups

Your tasks.md MUST contain a final group:

`## N. Testing & Verification`

With tasks like:
- Verify all acceptance criteria from design.md
- Verify all scenarios from specs
- Run `/opsx:verify` after implementation
```

## Appendix H — Replacement body for `src/commands/claptrap-brainstorm.md` (paste after YAML frontmatter)

```markdown
Invoke the `claptrap-brainstorming` skill and follow it EXACTLY as presented to you.

Before brainstorming:
- Invoke `claptrap-memory` and read `.claptrap/memories.md`.

After brainstorming:
- Generate a `<feature-slug>` from the design title using kebab-case.
- Create directory: `.claptrap/designs/<feature-slug>/`
- Write the validated design to: `.claptrap/designs/<feature-slug>/design.md`
  - Use the design template at `templates/design.md` from the brainstorm skill.
- If any significant decisions were made, invoke `claptrap-memory` and write selective memory entries.

Next step:
- Run `/claptrap-propose .claptrap/designs/<feature-slug>/design.md` to generate OpenSpec artifacts.

**User Brainstorm Idea/Prompt:** $ARGUMENTS
```

## Appendix I — Replacement body for `src/skills/claptrap-brainstorming/SKILL.md` (paste after YAML frontmatter)

```markdown
# Brainstorming Ideas Into Designs (Claptrap)

## Overview

Turn raw ideas into a **clear, validated design document** before any implementation begins.

This skill MUST:
- Read `.claptrap/memories.md` before starting (context/patterns/decisions).
- Ask clarifying questions in bounded rounds.
- Produce a complete design using the design template at `templates/design.md`.
- Write selective memory entries for significant decisions.

## Dialogue bounds (hard rules)

- Ask **3–5** clarifying questions per round.
- Allow **max 2 rounds** of clarifying questions.
- Prefer multiple-choice questions when possible.

## Workflow Steps

### Step 0: Load context

1. Check the current project state if needed (files, docs).
2. Read `.claptrap/memories.md` and extract relevant context:
   - Prior decisions that constrain the design
   - Patterns to reuse
   - Anti-patterns to avoid

### Step 1: Clarifying questions (max 2 rounds)

Ask 3–5 questions covering:
- User goals and success criteria
- Scope boundaries (in/out)
- Technical constraints or preferences
- Integration points with existing systems
- Timeline/phasing constraints

Wait for answers. If answers reveal gaps, ask one more round (again 3–5 questions). Then STOP asking questions and move on.

### Step 2: Research / exploration (only if needed)

If external documentation is needed, spawn the `research` subagent (do not research yourself).
If codebase context is needed, spawn the `explore` subagent.

### Step 3: Draft the design in validated sections

Generate the design in this exact section order, validating with the user after each section:
1. Intent
2. Scope (in/out)
3. Acceptance Criteria (checkboxes)
4. Architecture Overview (components, package structure, core types, data flow)
5. Key Decisions (Decision/Options/Choice/Rationale table)
6. Open Questions (checkboxes)
7. Next Steps (must include `/claptrap-propose`)

### Step 4: Finalize

1. Produce the final design using the template at `templates/design.md`.
2. Ensure ALL required headings exist in the final output.

### Step 5: Memory write (selective)

Generate 1–3 candidate memory entries for significant decisions and filter aggressively.
Write only the entries that would help a future agent avoid mistakes.
Never write secrets.
```

## Appendix J — `src/designs/example-feature/design.md` (copy exactly)

````markdown
# Design: Example Feature (Workflow Demo)
Date: 2026-01-28
Status: Draft
Author: Example Author

## Intent

Demonstrate the complete `design.md` structure produced by `/claptrap-brainstorm`, including optional technical sections used to generate OpenSpec artifacts.

## Scope

### In Scope
- Provide a concrete example of every required design section.
- Include a realistic package structure and core types example.
- Include acceptance criteria that can be converted into spec scenarios.
- Include key decisions in the full Decision/Options/Choice/Rationale format.

### Out of Scope
- Implementing any code.
- Creating OpenSpec artifacts (proposal/specs/tasks) in this repo.

## Acceptance Criteria

- [ ] The design includes at least 2 acceptance criteria with clear, testable outcomes.
- [ ] The design includes a package structure tree that can be converted into file-creation tasks.
- [ ] The design includes at least one core type definition in TypeScript.

## Architecture Overview

### Components
- `ExampleService`: Owns the primary business operation.
- `ExampleRepository`: Persists and retrieves Example data.
- `ExampleCLI`: Provides a simple user entry point for the operation.

### Package Structure

```
packages/example/
├── src/
│   ├── index.ts
│   ├── cli.ts
│   ├── service.ts
│   └── repository.ts
└── package.json
```

### Core Types

```typescript
export interface ExampleRecord {
  id: string
  status: "new" | "processed"
}
```

### Data Flow

1. User invokes CLI command.
2. CLI calls `ExampleService.process(...)`.
3. Service fetches an `ExampleRecord` from repository.
4. Service updates status and writes back to repository.

## Key Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Persistence approach | In-memory only, file-based JSON, DB-backed | file-based JSON | Simple demo with persistence and minimal dependencies |

## Open Questions

- [ ] Should the repository support batch operations?

## Next Steps

1. Review this design document
2. Run `/claptrap-propose .claptrap/designs/example-feature/design.md` to generate OpenSpec artifacts
3. Review and approve proposal/specs/tasks
4. Implement via `/opsx:apply`

## OpenSpec Proposals

<!-- Auto-populated by /claptrap-propose -->
- (none yet)
````

## Appendix K — Replacement body for `src/agents/alignment-reviewer.md` (paste after YAML frontmatter)

```markdown
Compare the proposal against the design intent and identify substantive gaps. Be critical but pragmatic.

# Subagent Interface
- Input 1: source design document (`design.md`)
- Input 2: generated proposal (`proposal.md`)
- Context: assume fresh context; do not rely on prior conversation state.

# Review Criteria
- Completeness: are all design requirements represented in proposal sections?
- Accuracy: does proposal correctly interpret the design intent and scope?
- Scope discipline: no scope creep beyond design.md.
- Source linking: proposal includes a source comment linking back to design.md.

# Rules
- Do not implement code or edit project files.
- Suggest edits and concrete fixes only.
- Avoid nitpicks; focus on substantive alignment issues.

# Output Format

Use one of the following formats at the top of your response:

ALIGNED

GAPS:
1. [Critical/Important/Minor] <issue> — Suggested fix: <fix>
2. ...

# Tasks
1. Read design.md and proposal.md.
2. Identify gaps between design intent/scope and proposal content.
3. Suggest concrete fixes for each gap.
4. Output `ALIGNED` or `GAPS`.
```

## Appendix L — Replacement body for `src/agents/feasibility-reviewer.md` (paste after YAML frontmatter)

```markdown
Evaluate whether the artifacts are implementable and realistically sequenced. Be critical but pragmatic.

# Subagent Interface
- Input 1: proposal (`proposal.md`)
- Input 2: all specs (`specs/**/spec.md`)
- Input 3: task checklist (`tasks.md`)
- Input 4: source design (`design.md`)
- Context: assume fresh context; do not rely on prior conversation state.

# Review Criteria
- Sequencing: tasks ordered correctly with dependencies respected.
- Sizing: tasks are appropriately scoped (no mega-tasks).
- Completeness: no missing steps (setup, docs, migrations when relevant).
- Feasibility: requirements/scenarios appear implementable given architecture described.
- Risks: external dependencies and unknowns are acknowledged.

# Rules
- Do not implement code or edit project files.
- Suggest edits and concrete fixes only.
- Avoid nitpicks; focus on substantive feasibility issues.

# Output Format

Use one of the following formats at the top of your response:

FEASIBLE

CONCERNS:
1. [Critical/Important/Minor] <issue> — Suggested fix: <fix>
2. ...

# Tasks
1. Read design.md, proposal.md, all spec.md files, and tasks.md.
2. Identify sequencing/sizing/completeness risks.
3. Suggest concrete fixes for each concern.
4. Output `FEASIBLE` or `CONCERNS`.
```

## Appendix M — Replacement body for `src/agents/plan-reviewer.md` (paste after YAML frontmatter)

```markdown
Validate that proposal/specs/tasks are consistent with the source design. Act as the explicit quality gate before implementation.

# Subagent Interface
- Input 1: source design (`design.md`)
- Input 2: proposal (`proposal.md`)
- Input 3: all specs (`specs/**/spec.md`)
- Input 4: tasks (`tasks.md`)
- Context: assume fresh context; do not rely on prior conversation state.

# Validation Checks (all are required)
1. Proposal.Why aligns with Design.Intent
2. Proposal.Capabilities covers Design.Scope.InScope
3. Proposal.Impact addresses Design.Key Decisions
4. Specs cover all Design.Acceptance Criteria
5. Specs scenarios are testable (WHEN/THEN format)
6. Tasks cover all Specs requirements
7. Tasks maintain correct sequencing (no task depends on a later task)
8. No orphaned or unreferenced items across artifacts

# Rules
- Do not implement code or edit project files.
- Do not broaden scope beyond the source design.
- Ask clarifying questions only when genuinely required to resolve ambiguity.
- Keep feedback prioritized and actionable.

# Output Format

Use one of the following formats at the top of your response:

APPROVED: <brief summary of what was reviewed>
- Notes: [optional minor callouts]

REVISE:
- Must fix: [blocking issues]
- Should fix: [important improvements]
- Nice to have: [optional improvements]
- Questions: [only if needed]
```
