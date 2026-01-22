# AGENTS.md

This document is the **source-of-truth for AI agents working on this repo**: what the project is for, how it should be organized, and the constraints to follow when adding or changing workflows/tools.

## Purpose

This repository aims to be a **provider/model agnostic** set of AI development workflows and tools that work across **different Providers, CLIs, and IDEs**.

- **Provider/model agnostic**: workflows should not assume a single model vendor, API, or prompt dialect.
- **Environment agnostic**: workflows should be usable in multiple execution contexts (IDE agents, CLI agents, chat-based code assistants).

### Supported Providers (examples)

The project is intended to support (at minimum) the following providers/models, while remaining compatible with others:

- **OpenAI** (e.g., Codex)
- **Anthropic** (e.g., Claude)
- **Google** (e.g., Gemini)

### Supported Development Environments (examples)

The project is intended to support (at minimum) the following environments, while remaining compatible with others:

- **Cursor**
- **VS Code**
- **OpenCode CLI**
- **AntiGravity**

## Scope and non-goals

- **In scope**
  - Agent roles (planner/developer/reviewer/etc.) and repeatable workflows for common dev tasks.
  - Cross-provider prompt patterns and guidance that degrade gracefully across models.
  - Environment-specific "adapters" (installation steps, file placement, naming conventions) that let the same roles/workflows run in different IDEs/CLIs.
- **Out of scope**
  - Building provider-specific SDK wrappers (unless the repo later introduces a runtime/tooling layer).
  - Hardcoding instructions that only work for one model's tool schema (unless isolated behind an environment/provider adapter).

## High-level concept: agents + workflows + adapters

Think of this repo as three layers:

- **Agents**: named agents with clear responsibilities (e.g., UI Designer, Planner, Developer, Code Reviewer).
- **Workflows**: step-by-step patterns that agents follow (e.g., plan → implement → review → resolve).
- **Adapters**: environment/provider-specific packaging that maps roles/workflows into a given tool (Cursor rules, VS Code Copilot agents, OpenCode CLI config, etc.).

The **agents and workflows should stay stable**, and adapters should handle differences between environments/providers.

## Current state of the repo

At the moment, the repository is mostly documentation (e.g., `README.md`) describing the intent and listing example roles, plus setup notes (e.g., symlinking agent/config folders into a project).

As more content is added, keep it organized according to the "Recommended repository organization" below.

## Recommended repository organization

When adding content, prefer this structure (names can be adjusted, but keep the separation of concerns):

- **`/src/`** — Installable content (symlinked/copied to target projects)
  - **`/src/agents/`** — Provider-neutral agent definitions.
  - **`/src/commands/`** — Slash command workflows that orchestrate agents.
  - **`/src/skills/`** — Reusable playbooks for common operations (includes memory system).
  - **`/src/code-conventions/`** — Code conventions and style guidance.
  - **`/src/designs/`** — Design document templates and examples.
- **`/bootstrap/`** — Installation scripts and templates for setting up claptrap in target projects.
- **`/docs/`** — Environment-specific documentation and research notes.
- **Top-level (this repo only)**
  - `README.md` (human intro)
  - `AGENTS.md` (this doc: operational guidance for agents working on this repo)
  - `GOALS.md` (project goals and roadmap)
  - `experimental/` (internal experiments)

If dotfolders exist (e.g., `.claude`, `.codex`, `.github`, `.opencode`), treat them as **generated adapter outputs** rather than the canonical source. Canonical source should live under `/src/`, then be rendered/copied/symlinked as needed.


## Agent roles (baseline set)

The following agents exist in `/src/agents/`. Keep the contract boundaries clear:

- **UI Designer** (`ui-designer.md`)
  - Produces UI specs: layouts, components, UX constraints, accessibility notes, states, and acceptance criteria.
- **Plan Reviewer** (`plan-reviewer.md`)
  - Checks plan vs. requirements; requests small iterative edits; prevents scope creep.
- **Alignment Reviewer** (`alignment-reviewer.md`)
  - Validates that proposals align with project goals and constraints.
- **Feasibility Reviewer** (`feasibility-reviewer.md`)
  - Assesses technical feasibility and identifies implementation risks.
- **Code Reviewer** (`code-reviewer.md`)
  - Reviews for correctness, security, performance, maintainability, and alignment with plan/spec.
- **Refactor** (`refactor.md`)
  - Performs targeted refactors with explicit intent and measurable improvements.
- **Research** (`research.md`)
  - Researches documentation and writes concise developer references.

### Handoffs and artifacts

To keep workflows provider-agnostic, role outputs should be **text-first** and easy to map into any environment:

- **Plan**: steps + file list + "definition of done".
- **Change summary**: what changed + why + how to verify.
- **Review notes**: prioritized issues + suggested remediation.
- **Decision log** (optional): key tradeoffs and why.

Avoid requiring proprietary tool calls as the *only* way to complete a role.

## Workflow conventions

These conventions are meant to work across IDEs/CLIs/providers:

- **Be explicit about intent**
  - Each change should map to a requirement or a documented improvement.
- **Keep changes small and reviewable**
  - Prefer incremental commits/patches and avoid drive-by refactors.
- **Defer environment-specific mechanics to adapters**
  - Example: "where to place prompts" or "how to register agents" belongs in `/adapters/*`, not in core workflow docs.
- **Prefer deterministic outputs**
  - Use checklists, expected file names, and stable formatting.

## Provider/model agnostic prompting guidelines

When writing prompts or instructions that might be used across providers:

- **Avoid provider-only features**
  - Don't assume a specific tool schema or "function calling" dialect.
  - If tool usage differs per provider, document it in the relevant adapter.
- **Use strong structure**
  - Specify required sections in outputs (e.g., "Plan", "Risks", "Files to touch").
- **Define terminology**
  - Spell out what "done" means and what "don't change" means.
- **Safety and privacy**
  - Don't instruct agents to exfiltrate secrets, logs, tokens, or proprietary data.
  - Treat API keys and `.env` content as sensitive by default.

## Setup notes (based on current README)

The `README.md` suggests a symlink-based approach for VS Code (and mentions OpenCode). If you keep that approach:

- Keep **adapter source** in this repo, and symlink/copy into target projects.
- Prefer **explicit env vars** that make automation repeatable (example shown in `README.md`).

## How to add or update content safely

- **Adding a new provider**
  - First ensure the core role/workflow is provider-neutral.
  - Add a provider adapter only to handle formatting/packaging differences.
- **Adding a new environment**
  - Add a new adapter directory and document installation + mapping.
  - Reuse the same role/workflow sources; don't fork the content unless unavoidable.
- **Changing a workflow**
  - Update the workflow doc, then verify each adapter still maps cleanly to it.
  - If behavior changes, update acceptance criteria and "definition of done".

## Expectations for future contributors (human or AI)

- **Keep docs canonical**: roles/workflows should be the canonical source; adapters are projections.
- **Minimize duplication**: shared text belongs in one place and referenced elsewhere.
- **Document assumptions**: if a workflow requires git, tests, or a particular stack, say so explicitly.

## Decisions / current conventions

These are the current project decisions; follow them unless explicitly changed:

- **Canonical source lives in `/src/`**: all installable content (agents, commands, skills, conventions, templates) lives under `/src/`.
- **Adapters are generated**: dotfolders (and other environment-specific install artifacts) should be produced from canonical sources, not hand-edited as the primary source.
- **OpenCode output**: `.opencode/` is the current output target for OpenCode adapter artifacts.
- **AntiGravity**: adapter packaging is **TBD**.
- **Role prompts**: per-role free-form is acceptable for now (no shared "must-use" template), but role responsibilities/handoffs must remain clear.
