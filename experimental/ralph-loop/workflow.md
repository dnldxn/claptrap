## AI Agent Software Delivery Workflow (provider/model/IDE agnostic)

This document is a **concrete, ready-to-run** workflow for building small hobby projects with AI agents while staying **provider/model/IDE agnostic** per `AGENTS.md`.

It merges the best ideas from `research.md` into a single runbook:

- **Durable state on disk** (specs + plan/checklist) instead of relying on chat history.
- **Separate planning vs implementation** to reduce “assumption filling”.
- **One task per iteration** to keep changes reviewable and costs bounded.
- **Backpressure** (typecheck/build, plus optional tests) so “done” means something measurable.
- **Explicit review + resolve loop** to catch mistakes without derailing the build loop.

This workflow assumes you have (or can define) a way to:

- run an “agent” in **plan**, **build**, **review**, and **resolve** roles (could be IDE agents, CLI agents, chat assistants with prompt files, etc.)
- run verification commands locally (typecheck/build, plus optional tests)

---

## Guiding decisions (and why)

- **Text-first artifacts**: Specs and plans are markdown files committed in the repo so they work across tools and survive context resets.
  - Why: avoids “requirements trapped in chat”; enables fresh contexts and subagents.
- **Dumb orchestration loop**: you re-run the same prompt file; state is in files.
  - Why: reduces tool-specific orchestration complexity and is easy to port.
- **Hard backpressure by default**: prefer deterministic checks over LLM “vibe testing”.
  - Why: hobby projects still benefit from clear stop conditions; prevents runaway loops.
- **OpenSpec as the default workflow**: keep “plan + spec delta + tasks” co-located in a change folder.
  - Why: it’s simple, reviewable, and portable across tools (files-on-disk are the interface).

---

## What you need in every repo (minimal “agent readiness”)

These are **files and conventions**, not tool-specific configs.

### Required artifacts

- **`AGENTS.md` (repo root)**: operational instructions for agents.
  - **Purpose**: a stable “how to run this project” contract for any tool.
  - **Must include**:
    - install deps
    - typecheck (if applicable)
    - build (if applicable)
  - **Optional (recommended)**:
    - run automated/unit tests (fast + full), if you have them
    - any safety constraints (“no drive-by refactors”, “no secrets”, etc.)
- **`.workflow/.code-conventions/`** (repo-local style guides)
  - **Purpose**: the *source of truth* for coding style and patterns the implementation agents MUST follow.
  - **Rule**: implementation agents MUST read and strictly follow any relevant guides in `.workflow/.code-conventions/` (e.g., `.workflow/.code-conventions/python.md`, `.workflow/.code-conventions/snowflake.md`) before making changes.
- **`openspec/`** (OpenSpec specs + change lifecycle artifacts)
  - **Purpose**: the durable statement of intent (“bones”) plus an explicit, reviewable “change folder” for each feature/fix.
  - **Structure**:
    - `openspec/specs/`: current “living” specifications
    - `openspec/changes/`: active changes containing `proposal.md`, `tasks.md`, and spec deltas
  - **Convenience**: you can add `.workflow/.openspec` as a symlink to `openspec/` for a dot-prefixed alias.

### Optional (recommended) artifacts

- **`DECISIONS.md`**: brief tradeoffs / key architecture choices.
- **`NOTES.md`**: scratchpad (not loaded by default in every run).

---

## Setup (new or existing project)

This repo is intended to live **separately** from your project repos. You “inject” the workflow into a project using **environment variables + symlinks**, then initialize OpenSpec inside the project.

Reference for OpenSpec commands: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)

### Setup steps (do these in every project repo)

1. **Set paths**
   - `CLAPTRAP_PATH`: absolute path to this repo
   - `PROJECT_PATH`: absolute path to the target project repo
2. **Symlink `.workflow/.code-conventions/` and create `.workflow/.prompts/` in the project**
3. **Ensure the project has a project-specific `AGENTS.md`**
4. **Install + initialize OpenSpec in the project**
5. **Create `.workflow/.prompts/` files from the templates in `workflow.md`**
6. **Enable agent tools**
   - Required capabilities: filesystem read/write, terminal exec, repo search (`rg`), optional browser/docs
   - If your environment supports MCP, enable MCP servers that provide those capabilities

### Scripts (copy/paste)

Run this from *anywhere* (it uses `CLAPTRAP_PATH` + `PROJECT_PATH`):

```bash
#!/usr/bin/env bash
# init-project.sh
set -euo pipefail

: "${CLAPTRAP_PATH:?set CLAPTRAP_PATH to the claptrap repo path}"
: "${PROJECT_PATH:?set PROJECT_PATH to the target project repo path}"

cd "$PROJECT_PATH"

# 1) Inject the workflow + conventions (symlinks)
mkdir -p "$PROJECT_PATH/.workflow"
ln -sfn "$CLAPTRAP_PATH/code-conventions" "$PROJECT_PATH/.workflow/.code-conventions"

# 2) Ensure AGENTS.md exists (project-specific commands go here)
if [ ! -f "$PROJECT_PATH/AGENTS.md" ]; then
  cat > "$PROJECT_PATH/AGENTS.md" <<'EOF'
# AGENTS.md
#
# Project-specific runbook for AI agents working in THIS repo.

## Project commands (copy/paste)
- Install: <fill me in>
- Typecheck: <fill me in or "N/A">
- Build: <fill me in or "N/A">
- Tests (optional): <fill me in or "N/A">

## Safety / constraints
- No drive-by refactors.
- No unrelated bugfixes.
- Follow .workflow/.code-conventions/* strictly.
EOF
fi

# 3) Install/upgrade OpenSpec + initialize in this repo
npm install -g @fission-ai/openspec@latest
openspec init
openspec update

# 4) Create prompt files by extracting the fenced blocks from workflow.md
mkdir -p "$PROJECT_PATH/.workflow/.prompts"

extract_prompt () {
  local header="$1" out="$2"
  awk -v h="$header" '
    $0 ~ h {in_h=1}
    in_h && $0 ~ /^```text$/ {in_code=1; next}
    in_code && $0 ~ /^```$/ {exit}
    in_code {print}
  ' "$CLAPTRAP_PATH/workflow.md" > "$out"
}

extract_prompt "^### `\\.workflow/\\.prompts/propose.md`" "$PROJECT_PATH/.workflow/.prompts/propose.md"
extract_prompt "^### `\\.workflow/\\.prompts/apply.md`"   "$PROJECT_PATH/.workflow/.prompts/apply.md"
extract_prompt "^### `\\.workflow/\\.prompts/review.md`"  "$PROJECT_PATH/.workflow/.prompts/review.md"
extract_prompt "^### `\\.workflow/\\.prompts/resolve.md`" "$PROJECT_PATH/.workflow/.prompts/resolve.md"

ln -sfn "$PROJECT_PATH/openspec" "$PROJECT_PATH/.workflow/.openspec"

echo "OpenSpec workflow injected."
echo "- $PROJECT_PATH/.workflow/ (directory)"
echo "- $PROJECT_PATH/.workflow/.code-conventions/ (symlink)"
echo "- $PROJECT_PATH/AGENTS.md"
echo "- $PROJECT_PATH/openspec/ (created by openspec init)"
echo "- $PROJECT_PATH/.workflow/.prompts/*.md"
echo "- $PROJECT_PATH/.workflow/.openspec -> $PROJECT_PATH/openspec (symlink)"
```

To refresh OpenSpec integration in a project (after upgrading tools or switching IDEs), run:

```bash
#!/usr/bin/env bash
# refresh-openspec-workflow.sh
set -euo pipefail

: "${PROJECT_PATH:?set PROJECT_PATH to the target project repo path}"
cd "$PROJECT_PATH"
openspec update
```

---

## Default workflow: OpenSpec

This workflow uses OpenSpec as the default and only track because it provides a consistent, tool-agnostic lifecycle and file structure:

- **Propose**: create a change folder with proposal + tasks + spec deltas
- **Verify/Review**: validate and review the proposal + spec delta before implementing
- **Apply**: implement tasks from `tasks.md`
- **Archive**: merge the change into “living” specs when complete

Reference: [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)

---

## Files created by this workflow (and where they live)

This workflow is intentionally **file-based** so it can be used from any IDE/CLI/provider. Below is the concrete layout it expects you to create in a project repo.

### Required layout (OpenSpec + project run instructions)

```text
project/
  AGENTS.md
  openspec/
    specs/                  # current “living” specs
    changes/                # active changes with proposal/tasks/spec deltas
  .workflow/
    .code-conventions/
      python.md             # if applicable
      snowflake.md          # if applicable
    .openspec -> ../openspec/  # optional symlink
    .prompts/               # optional (portable location for saved prompts)
      propose.md
      apply.md
      review.md
      resolve.md            # optional
      archive.md            # optional
  DECISIONS.md              # optional
  NOTES.md                  # optional
```

- **`AGENTS.md` (required, repo root)**: operational “how to run this repo” instructions (install/build/typecheck/etc.) and safety constraints.
- **`.workflow/.code-conventions/` (required)**: style guides that implementation agents MUST read and follow.
  - **`.workflow/.code-conventions/python.md`**: Python conventions (if the repo contains Python).
  - **`.workflow/.code-conventions/snowflake.md`**: Snowflake SQL conventions (if the repo contains Snowflake SQL).
- **`openspec/specs/` (required)**: the repo’s current “living” specification set.
- **`openspec/changes/<change>/` (created per change)**: a self-contained unit of work with:
  - `proposal.md`: what/why is changing
  - `tasks.md`: implementation checklist (the “plan”)
  - `design.md` (optional): technical decisions (when useful)
  - `specs/**`: spec deltas to review before archiving
- **`DECISIONS.md` (optional)**: short record of key tradeoffs/architecture decisions that future agents should not “re-litigate”.
- **`NOTES.md` (optional)**: scratchpad for non-durable thinking; not meant to be loaded every run.
- **`.workflow/.prompts/*.md` (optional)**: saved prompt text for OpenSpec propose/apply/review/archive roles.
  - Purpose: enables “dumb loops” (`<agent-cli> < .workflow/.prompts/apply.md`) and keeps prompts portable.
  - If your environment uses a different prompt location, treat `.workflow/.prompts/` as the canonical source and copy/symlink as needed.

---

## Phase 1: Clarify requirements (“interview mode”) → write specs

### Step 1.1 — Ask clarifying questions (must happen before planning)

Use this question set as a default. The agent should ask only what’s relevant:

- **Audience / user**: who is this for and what job are they trying to do?
- **Problem statement**: what pain are we solving?
- **Non-goals**: what should we explicitly not build?
- **Constraints**:
  - platform/runtime (web, mobile, CLI; Node/Python/etc)
  - compatibility requirements
  - performance/security expectations (even if “basic”)
- **Acceptance criteria** (observable outcomes):
  - “Given/When/Then” or scenario bullets
  - edge cases (empty states, errors, limits)
- **Verification expectations**:
  - should we add automated/unit tests, or is that overkill for this project?
  - what’s “good enough” coverage for a hobby project?

**Justification**: this is the simplest high-leverage control to prevent assumption-filling and rework.

### Step 1.2 — Create an OpenSpec proposal (spec delta + tasks)

Create a change proposal (the “plan + spec delta”):

- **Via AI slash command** (if your tool supports it):
  - `/openspec:proposal <PROPOSAL>`
- **Or via CLI** (environment dependent):
  - run the equivalent OpenSpec command to scaffold the change folder (example: `openspec proposal "<PROPOSAL>"`)

Then refine the generated `openspec/changes/<change>/specs/**` deltas and `tasks.md` until they match your intent.

**Stop condition**: the user agrees the spec matches intent.

---

## Phase 2: Planning mode (refine proposal/spec delta/tasks)

### Step 2.1 — Planning rules (must be enforced)

- **Plan only**: no code edits.
- **Don’t assume not implemented**: search/read to confirm.
- **Derive optional tests from acceptance criteria** (recommended, but not required for small projects).
- **One task per future iteration**: each task should be independently committable.
- **Cap scope**: hobby projects benefit from small slices; defer “nice to haves”.

**Justification**: planning is where you pay down ambiguity cheaply; implementation is expensive.

### Step 2.2 — Verify & review the OpenSpec change

Use OpenSpec’s review surface:

- `openspec list` — confirm the change exists
- `openspec validate <change>` — validate formatting/structure
- `openspec show <change>` — review proposal, tasks, and spec delta

**Stop condition**: the plan is reviewable, sized, and tied to verification.

---

## Phase 2.5: Plan review (small hobby-project version)

Before writing code, run a quick “plan reviewer” pass.

### Step 2.5.1 — Plan Reviewer checklist

- Does each task map to a spec requirement or acceptance criterion?
- Are tasks small enough to complete in one iteration?
- Are verification steps explicit and realistic?
- Are there hidden dependencies or missing edge cases?
- Is there any risky refactor masquerading as required work?

**Stop condition**: only minor edits remain.

---

## Phase 3: Build loop (one task per iteration)

This is the core engine. Keep it repetitive.

### Step 3.0 — Preconditions

- An OpenSpec change exists in `openspec/changes/<change>/`.
- `openspec/changes/<change>/tasks.md` has at least one incomplete task.
- `AGENTS.md` commands are correct.
- You have a working branch/worktree for the feature (recommended, optional).

### Step 3.1 — Select the next task

Pick the highest-priority incomplete checkbox item from `openspec/changes/<change>/tasks.md`.

### Step 3.2 — Investigate before coding

The agent should:

- search the repo for relevant symbols/paths (e.g., `rg -n "<keyword>" .`)
- read the minimum necessary files
- state a short implementation approach

### Step 3.3 — Implement only what the task requires

Rules:

- minimal diff that achieves the task outcome
- avoid “drive-by refactors”
- follow existing patterns in the codebase

### Step 3.4 — Verify (“backpressure”)

Run the repo’s verification commands from `AGENTS.md`. Minimum set:

- typecheck (if applicable)
- build (if applicable)

Optional (recommended):

- automated/unit tests, if they exist (or if the change is risky enough to justify adding them)

If verification fails:

- fix it within the same iteration (or split into a new task if it’s larger)

### Step 3.5 — Update plan + write a commit

- check off the completed task(s) in `openspec/changes/<change>/tasks.md` (and update the change’s spec delta if you discovered missing requirements)
- commit with a message that maps 1:1 to the task

### Step 3.6 — Repeat until done (with caps)

To avoid runaway loops:

- set a max iteration count (e.g., 3–8 iterations for a hobby feature)
- stop when all tasks are done and verification is green

---

## Phase 4: Code review loop (review → resolve)

Treat review as a separate phase; it catches mistakes without derailing planning/building discipline.

### Step 4.1 — Code Review (what the reviewer must check)

- correctness vs acceptance criteria
- security basics (input validation, auth boundaries, secrets)
- performance footguns (obvious N+1, unbounded loops, huge payloads)
- maintainability (clarity, naming, consistent patterns)
- tests: do they assert outcomes, not implementation details?
- adherence to “no drive-by refactors”

Output format should be stable:

- **Must fix** (blocking)
- **Should fix** (non-blocking)
- **Nice to have**

### Step 4.2 — Resolver pass

- apply only the agreed review fixes
- re-run verification
- update plan/specs if the review reveals missing requirements

Stop condition: review issues closed and verification passes.

---

## Phase 5: Archive and documentation

### Step 5.1 — Ensure the repo’s “truth” matches reality

- update specs to reflect final behavior (if implementation drifted)
- add short notes to `DECISIONS.md` if there were key tradeoffs

Archive the change to merge spec deltas into living specs:

- `/openspec:archive <change>` (if supported)
- or `openspec archive <change> --yes`

---

## “Ready to run” prompt templates (portable)

These are **templates** you can paste into any environment that supports prompt files or saved prompts.
Do not treat the exact wording as magical; the structure is what matters.

### `.workflow/.prompts/propose.md` (OpenSpec Proposal / Planner)

```text
ROLE: Planner (OpenSpec Proposal)

You are in PROPOSAL MODE. Do not implement code.

Rules:
- If the request is ambiguous, ask the USER up to 1–3 targeted clarifying questions, then stop.
- If you have enough information, write a concise proposal.
- Do NOT tell OpenSpec how to format/organize its internal files.
- Do not implement code.
```

### `.workflow/.prompts/apply.md` (OpenSpec Apply / Developer)

```text
ROLE: Developer

You are in APPLY MODE. Implement exactly ONE task from openspec/changes/<change>/tasks.md.

Core principles:
- Simple over clever; make minimal, focused edits.
- No drive-by refactors or unrelated fixes.
- Handle errors primarily at external boundaries (I/O, network, user input).
- Avoid new dependencies unless truly required.
- If something is ambiguous, stop and ask brief clarifying questions (don’t guess).

Before writing or editing code:
- read and follow all relevant docs in .workflow/.code-conventions/ (these are mandatory)

Process:
1) Select the highest priority incomplete task checkbox from tasks.md.
2) Investigate (search/read) before coding. Do not assume.
3) Implement minimal changes for this task only.
4) Run required verification commands from AGENTS.md (typecheck/build; tests optional).
5) Update tasks.md (mark task done; add notes if scope changed).

Stop when:
- the selected task is complete AND verification passes.
```

### `.workflow/.prompts/review.md` (Code Reviewer)

```text
ROLE: Code Reviewer

Review the changes for correctness, safety, performance, and maintainability.

Core principles:
- Simplicity-first: prefer clear working code over complex “best practices”.
- Focus on real issues; skip minor style preferences and theoretical perfectionism.
- Enforce `.workflow/.code-conventions/*` strictly.
- Be specific: file/line oriented, actionable fixes, categorized by priority.
- Tests are optional; recommend them only when risk/complexity justifies.

Check alignment with:
- openspec/specs/* and openspec/changes/<change>/specs/* (the intended behavior)
- .workflow/.code-conventions/* (style/pattern adherence is required)

Output in three sections:
- Must fix
- Should fix
- Nice to have

Do not propose scope expansion unless it is required to meet acceptance criteria.
```

### `.workflow/.prompts/resolve.md` (Resolver)

```text
ROLE: Resolver

Apply ONLY the "Must fix" (and any explicitly approved) review items.

Core principles:
- Make the smallest change that resolves each issue.
- Avoid refactors unless required to fix the issue.
- Follow `.workflow/.code-conventions/*` strictly.
- Ask brief clarifying questions if a review item is ambiguous.

Run verification from AGENTS.md.
Update tasks.md if task status changes.
```

---

## Example “dumb loop” commands (CLI-agnostic)

These are patterns you can translate to your tool of choice:

```bash
# Propose loop (run until the OpenSpec change is approved)
while true; do
  <agent-cli> < .workflow/.prompts/propose.md
  # stop manually when proposal/spec delta/tasks look good
done
```

```bash
# Apply loop (one task per iteration)
while true; do
  <agent-cli> < .workflow/.prompts/apply.md
  # stop manually when tasks.md has no remaining tasks
done
```

**Justification**: loops are powerful, but the workflow stays portable because the “state” is the files.

---

## Optional: subagents (as a pattern)

If your environment supports subagents, use them for:

- repo-wide search + reading lots of files
- audit/checklist review
- log/stack-trace triage
- alternative design proposals (2–3 independent approaches)

**Contract**: subagents return **reports with file paths**, not code changes.

---

## Questions (to tailor this for your repos)

1. **Default project type**: are your hobby projects mostly **Node/TS**, **Python**, or something else?
2. **Backpressure**: do you already have a single command like `make verify` / `just verify` / `npm test` that you want agents to treat as the default?
3. **Commit style**: should the workflow assume “commit per task” always, or do you prefer “commit per feature” with checkpoints?

