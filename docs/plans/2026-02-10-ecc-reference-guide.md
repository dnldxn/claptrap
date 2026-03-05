# Everything Claude Code (ECC) — Comprehensive Reference Guide

**Date:** 2026-02-10
**Version:** Based on ECC v1.4.1 (Feb 2026)
**Purpose:** Complete reference for ECC features, how they fit together, and how to use them in an agentic development workflow

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [How Features Fit Together](#how-features-fit-together)
3. [Agents](#agents)
4. [Commands](#commands)
5. [Skills](#skills)
6. [Rules](#rules)
7. [Hooks](#hooks)
8. [Scripts](#scripts)
9. [Contexts](#contexts)
10. [MCP Server Configurations](#mcp-server-configurations)
11. [Continuous Learning System](#continuous-learning-system)
12. [Context & Memory Management](#context--memory-management)
13. [Feature Selection Guide](#feature-selection-guide)

---

## Architecture Overview

ECC is a modular system of markdown-based configuration files that extend Claude Code's capabilities. Each component type serves a specific role:

```
User types a command (e.g., /plan)
    │
    ▼
Command (.md file) provides instructions to Claude
    │
    ▼
Command may invoke an Agent (specialized subagent)
    │
    ▼
Agent uses Skills for domain knowledge & workflows
    │
    ▼
Rules are always active, guiding all behavior
    │
    ▼
Hooks fire automatically on events (tool use, session start/end, compaction)
    │
    ▼
Scripts execute cross-platform (Node.js) for hook implementations
    │
    ▼
Continuous Learning captures patterns → instincts → evolved skills
```

### Key Principles

1. **Rules over Tools** — Rules tell "what" to do; skills tell "how" to do it
2. **Test-First** — TDD is the default (80%+ coverage mandate)
3. **Token Efficiency** — Keep context window usage lean (70-200k max)
4. **Many Small Files** — 200-400 lines typical, high cohesion
5. **Proactive Agents** — Agents activate based on task context without waiting for explicit request
6. **Minimal Diffs** — Changes should be targeted and surgical
7. **Cross-Platform** — All scripts use Node.js for Windows/Mac/Linux compatibility

---

## How Features Fit Together

### Component Relationships

| Component | Discoverable | Invocation | Scope |
|-----------|-------------|------------|-------|
| **Agents** | `~/.claude/agents/*.md` | By name via Task tool | Subagent (isolated context) |
| **Commands** | `~/.claude/commands/*.md` | `/command-name` | Main conversation |
| **Skills** | `~/.claude/skills/*/SKILL.md` | By directory name | Reference material |
| **Rules** | `~/.claude/rules/*.md` | Auto-loaded always | Every session |
| **Hooks** | `~/.claude/hooks/hooks.json` or `settings.json` | Event-triggered | Automatic |
| **Contexts** | `~/.claude/contexts/*.md` | Selectable mode | System prompt |
| **Scripts** | Referenced by hooks | Called by hooks | Background |

### Data Flow Example: Feature Implementation

```
/plan "Add caching layer"
  │
  ├─ Rules (always active): coding-style, testing, patterns
  │
  ├─ Command: plan.md → instructions for planning
  │     └─ Spawns: planner agent (subagent with Opus model)
  │           └─ Uses: Read, Grep, Glob tools
  │           └─ References: coding-standards skill, backend-patterns skill
  │
  ├─ Hooks fire:
  │     ├─ PreToolUse: CL-v2 observe.sh (captures prompt)
  │     ├─ PostToolUse: CL-v2 observe.sh (captures outcome)
  │     └─ PreToolUse:Edit: strategic-compact suggest-compact.sh
  │
  └─ Output: Implementation plan document
```

---

## Agents

Agents are specialized subprocesses with isolated context. Each has a specific domain, limited tools, and uses the Opus model for maximum capability.

### How Agents Work

- Defined as `.md` files with YAML frontmatter (`name`, `description`, `tools`, `model`)
- Spawned via Claude Code's Task tool with `subagent_type`
- Run in isolated context (don't see main conversation)
- Return a single result message to the main conversation
- Can run in background for parallel execution

### Available Agents

#### planner
**Purpose:** Feature planning and implementation breakdown
**Tools:** Read, Grep, Glob (read-only)
**When to use:** Complex features requiring multi-step implementation plans
**Process:** Requirements analysis → Architecture review → Step breakdown → Implementation ordering
**Output:** Phased implementation plan with file paths, dependencies, risks, testing strategy

#### architect
**Purpose:** System design, scalability, technical decision-making
**Tools:** Read, Grep, Glob (read-only)
**When to use:** New system design, architectural decisions, scalability analysis
**Process:** Current state analysis → Requirements gathering → Design proposal → Trade-off analysis
**Output:** Architecture Decision Records (ADRs), design proposals with pros/cons

#### code-reviewer
**Purpose:** Code quality, maintainability, pattern review
**Tools:** Read, Grep, Glob, Bash
**When to use:** Before merging/committing completed features
**Output:** Review report with findings categorized by severity

#### python-reviewer
**Purpose:** Python-specific code review
**Tools:** Read, Grep, Glob, Bash
**When to use:** Python code review focusing on PEP 8, type hints, security, idioms
**Output:** Python-specific findings with suggested fixes

#### tdd-guide
**Purpose:** Test-Driven Development enforcement
**Tools:** Read, Write, Edit, Bash, Grep
**When to use:** All implementation work (enforces RED-GREEN-REFACTOR)
**Targets:** 80%+ code coverage, tests written before implementation

#### build-error-resolver
**Purpose:** Fix build/compilation errors with minimal changes
**Tools:** Read, Write, Edit, Bash, Grep, Glob
**When to use:** Build failures, type errors, compilation issues
**Approach:** Minimal diffs, targeted fixes

#### refactor-cleaner
**Purpose:** Dead code detection and removal
**Tools:** Read, Write, Edit, Bash, Grep, Glob
**When to use:** Code cleanup, removing unused imports/functions/classes
**Tools used:** knip, depcheck, ts-prune (or language equivalents)

#### doc-updater
**Purpose:** Documentation generation and maintenance
**Tools:** Read, Write, Edit, Bash, Grep, Glob
**When to use:** Updating architecture docs, codemaps, README files
**Approach:** AST analysis, dependency graph generation

### Agents NOT included (and why)

| Agent | Why excluded |
|-------|-------------|
| security-reviewer | Security review not in scope |
| database-reviewer | Supabase-specific |
| e2e-runner | Playwright/browser testing not relevant |
| go-reviewer | Add later if Go usage increases |
| go-build-resolver | Add later if Go usage increases |

---

## Commands

Commands are slash-invokable prompts. Each is a `.md` file in `~/.claude/commands/` that provides structured instructions to Claude when invoked.

### How Commands Work

- User types `/command-name [arguments]`
- Claude reads the `.md` file content as instructions
- `$ARGUMENTS` placeholder is replaced with user's arguments
- Commands may reference agents (spawn subagents) or skills (reference knowledge)
- Commands don't execute code directly — they instruct Claude

### Core Workflow Commands

#### /plan [description]
**Phase:** Planning
**Agent:** planner
**Purpose:** Create step-by-step implementation plan from requirements
**Output:** Phased plan with file paths, dependencies, risks, testing strategy
**Usage:** `/plan Add a caching layer for API responses`

#### /tdd [description]
**Phase:** Implementation
**Agent:** tdd-guide
**Purpose:** Implement features using RED-GREEN-REFACTOR methodology
**Process:**
1. RED — Write a failing test for the next requirement
2. GREEN — Write minimal code to pass the test
3. REFACTOR — Clean up code while keeping tests green
4. Repeat until feature is complete
**Usage:** `/tdd Implement the cache invalidation logic`

#### /code-review [scope]
**Phase:** Review
**Agent:** code-reviewer
**Purpose:** Comprehensive code quality and maintainability review
**Checks:** Code style, patterns, error handling, test coverage, complexity
**Usage:** `/code-review` (reviews recent changes)

#### /python-review [scope]
**Phase:** Review
**Agent:** python-reviewer
**Purpose:** Python-specific code review
**Checks:** PEP 8, type hints, Pythonic idioms, security patterns
**Usage:** `/python-review src/cache/`

#### /verify [mode]
**Phase:** Verification
**Purpose:** Run comprehensive verification on codebase state
**Modes:**
- `quick` — Build + types only
- `full` — All checks (default)
- `pre-commit` — Checks relevant for commits
- `pre-pr` — Full checks plus extras
**Output:** Pass/fail report with "Ready for PR: YES/NO"
**Usage:** `/verify full`

#### /checkpoint [action] [name]
**Phase:** Any
**Purpose:** Named save points with git SHA and verification
**Actions:**
- `create <name>` — Create named checkpoint (runs quick verify first)
- `verify <name>` — Compare current state to checkpoint
- `list` — Show all checkpoints
- `clear` — Remove old checkpoints (keeps last 5)
**Usage:** `/checkpoint create "phase-1-done"`

#### /eval [action] [name]
**Phase:** Any
**Purpose:** Define and check formal evaluation criteria for features
**Actions:**
- `define <name>` — Create eval definition with capability + regression criteria
- `check <name>` — Run evals, record PASS/FAIL
- `report <name>` — Generate comprehensive report
- `list` — Show all evals with status
**Usage:** `/eval define cache-layer`

### Learning & Evolution Commands

#### /learn
**Purpose:** Extract reusable patterns from current session
**When:** After solving a non-trivial problem
**Output:** Skill file saved to `~/.claude/skills/learned/[pattern-name].md`
**Process:** Reviews session → Identifies valuable pattern → Drafts skill → Asks confirmation → Saves
**Usage:** `/learn`

#### /evolve [flags]
**Purpose:** Cluster related instincts into higher-level structures
**Evolution types:**
- → **Command**: When instincts describe user-invoked actions
- → **Skill**: When instincts describe auto-triggered behaviors
- → **Agent**: When instincts describe complex multi-step processes
**Flags:**
- `--execute` — Create the evolved structures (default: preview only)
- `--dry-run` — Preview without creating
- `--domain <name>` — Only evolve instincts in specified domain
- `--threshold <n>` — Minimum instincts to form cluster (default: 3)
**Usage:** `/evolve --dry-run`

#### /instinct-status
**Purpose:** Show all learned instincts with confidence scores
**Usage:** `/instinct-status`

#### /instinct-export
**Purpose:** Export your instincts for sharing with others
**Usage:** `/instinct-export`

#### /instinct-import [file]
**Purpose:** Import instincts from others
**Usage:** `/instinct-import shared-instincts.json`

#### /skill-create
**Purpose:** Generate a SKILL.md from git history analysis
**Usage:** `/skill-create`

### Utility Commands

#### /refactor-clean
**Purpose:** Detect and remove dead code, consolidate duplicates
**Agent:** refactor-cleaner
**Usage:** `/refactor-clean src/`

#### /test-coverage
**Purpose:** Analyze code coverage and identify gaps
**Usage:** `/test-coverage`

### Commands NOT included (and why)

| Command | Why excluded |
|---------|-------------|
| /orchestrate | Manual control preferred; add later for automation |
| /multi-plan | Requires Codex+Gemini APIs; designed for frontend+backend split |
| /multi-execute, /multi-backend, /multi-frontend, /multi-workflow | Multi-agent orchestration overkill |
| /e2e | Playwright/browser testing |
| /security | Security review not in scope |
| /go-review, /go-test, /go-build | Add later if Go usage increases |
| /build-fix | TypeScript-focused; adapt for Python if needed |
| /sessions | Lower priority; add later for session management |
| /update-codemaps | Lower priority; add for large codebases |
| /update-docs | Lower priority; add when documentation needs grow |
| /setup-pm, /pm2 | Package manager / PM2 not relevant |

---

## Skills

Skills are knowledge modules that provide domain expertise and workflow patterns. Each skill is a directory containing a `SKILL.md` file with structured guidance.

### How Skills Work

- Located in `~/.claude/skills/[skill-name]/SKILL.md`
- Referenced by agents and commands for domain knowledge
- Can include supporting files (scripts, examples, configs)
- Not directly invokable by users — consumed by Claude's reasoning
- Some skills have hooks that integrate with the automation system

### Included Skills

#### brainstorming (Superpowers)
**Purpose:** Collaborative ideation through natural dialogue
**Process:** Understand idea → Ask questions one at a time → Propose approaches → Present design in sections → Write design doc
**Output:** `docs/plans/YYYY-MM-DD-<topic>-design.md`
**Key:** Multiple choice questions preferred, one question per message, YAGNI ruthlessly

#### continuous-learning-v2
**Purpose:** Instinct-based learning system with confidence scoring
**How:** PreToolUse/PostToolUse hooks capture all activity → Observer agent (Haiku, background) detects patterns → Creates atomic instincts with confidence 0.3-0.9 → `/evolve` clusters into skills/commands/agents
**Data:** `~/.claude/homunculus/`
**Integration:** Requires hooks in settings.json

#### iterative-retrieval
**Purpose:** Progressive context refinement for subagent context problem
**When:** Subagents need context they don't have from the main conversation
**How:** Iteratively retrieves and refines context until sufficient

#### tdd-workflow
**Purpose:** Test-driven development methodology reference
**Content:** RED-GREEN-REFACTOR cycle, test organization, coverage targets, fixture patterns

#### verification-loop
**Purpose:** Continuous verification and evaluation patterns
**Content:** When to verify, what to check, how to interpret results

#### eval-harness
**Purpose:** Evaluation framework for LLM outputs
**Content:** Capability evals, regression evals, pass@k metrics, scoring criteria

#### coding-standards
**Purpose:** Language-agnostic best practices
**Content:** Naming conventions, file organization, error handling, documentation patterns

#### python-patterns
**Purpose:** Python idioms and design patterns
**Content:** Pythonic patterns, dataclasses, context managers, generators, decorators, typing

#### python-testing
**Purpose:** pytest and TDD for Python
**Content:** pytest fixtures, parametrize, mocking, coverage configuration, test organization

#### strategic-compact
**Purpose:** Suggests manual `/compact` at logical workflow boundaries
**How:** Hook counts tool invocations, suggests compaction at threshold (default: 50 calls)
**Best times:** After planning, after debugging, between phases
**Integration:** Requires PreToolUse hook for Edit/Write

#### backend-patterns
**Purpose:** API, database, caching patterns
**Content:** Repository pattern, service layer, middleware, event-driven, CQRS

### Skills NOT included (and why)

| Skill | Why excluded |
|-------|-------------|
| frontend-patterns | Not relevant for Python/SQL |
| django-patterns, django-security, django-tdd, django-verification | Django not used |
| springboot-patterns, springboot-security, springboot-tdd, springboot-verification | Spring Boot not used |
| security-review | Security not in scope |
| clickhouse-io | ClickHouse not used |
| jpa-patterns, java-coding-standards | Java not used |
| nutrient-document-processing | Document processing not relevant |
| golang-patterns, golang-testing | Add later if Go usage increases |
| configure-ecc | One-time setup wizard, not needed after initial config |
| continuous-learning (v1) | Superseded by v2 |

---

## Rules

Rules are always-active guidelines loaded into every Claude session. They shape Claude's behavior without being explicitly invoked.

### How Rules Work

- Located in `~/.claude/rules/*.md`
- Automatically loaded into Claude's system prompt every session
- Cannot be selectively disabled (all rules are always active)
- Should be kept concise to minimize context window usage
- Think of rules as "personality" — persistent behavioral guidelines

### Included Rules

#### coding-style.md (common)
**Content:** Immutability patterns (spread operators, no mutations), naming conventions (camelCase/snake_case by language), file organization (200-400 lines max), import ordering, many small files principle

#### git-workflow.md (common)
**Content:** Conventional commits (`feat:`, `fix:`, `refactor:`, etc.), PR process, branch naming, commit message format, atomic commits

#### testing.md (common)
**Content:** TDD mandate (80%+ coverage), test organization (unit/integration/e2e), naming conventions (`test_should_*`), fixture patterns, flaky test handling

#### performance.md (common)
**Content:** Context window management (don't enable all MCPs), model selection guidance, token optimization, background process recommendations, lazy loading patterns

#### patterns.md (common)
**Content:** SOLID principles, design patterns (repository, service layer, factory), DRY/YAGNI, composition over inheritance, dependency injection

#### agents.md (common)
**Content:** When to delegate to subagents vs handle in main context, agent selection criteria, parallel vs sequential agent execution, handoff document format

#### python-coding-style.md
**Content:** PEP 8, ruff for linting, mypy for type checking, Black for formatting, Python-specific naming (snake_case), docstring conventions

#### python-testing.md
**Content:** pytest as framework, conftest.py patterns, parametrize, fixtures (scope, autouse), coverage configuration, mock patterns

#### python-patterns.md
**Content:** Pythonic patterns, dataclasses over dicts, context managers, generators, type hints (typing module), protocol classes, ABC patterns

### Rules NOT included (and why)

| Rule | Why excluded |
|------|-------------|
| security.md (common + python) | Security not in scope |
| hooks.md (common) | Internal hook architecture reference, not actionable as a rule |
| typescript/* | Not relevant |
| golang/* | Add later if needed |

---

## Hooks

Hooks are event-driven automation that fires on specific Claude Code events. They execute scripts or commands automatically without user intervention.

### How Hooks Work

- Configured in `~/.claude/settings.json` under `"hooks"` key
- Fire on events: PreToolUse, PostToolUse, SessionStart, SessionEnd, PreCompact, Stop
- Can filter with `matcher` patterns (e.g., only fire on Edit tool)
- Execute shell commands or Node.js scripts
- Should exit quickly (non-blocking) or run in background
- Exit code 0 = success, non-zero = error (may block the tool call)

### Recommended Hook Configuration

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{
          "type": "command",
          "command": "node ~/.claude/scripts/hooks/session-start.js"
        }]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [{
          "type": "command",
          "command": "node ~/.claude/scripts/hooks/session-end.js"
        }]
      },
      {
        "hooks": [{
          "type": "command",
          "command": "node ~/.claude/scripts/hooks/evaluate-session.js"
        }]
      }
    ],
    "PreCompact": [
      {
        "hooks": [{
          "type": "command",
          "command": "node ~/.claude/scripts/hooks/pre-compact.js"
        }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh pre"
        }]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/skills/strategic-compact/suggest-compact.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [{
          "type": "command",
          "command": "~/.claude/skills/continuous-learning-v2/hooks/observe.sh post"
        }]
      }
    ]
  }
}
```

### Hook Descriptions

| Event | Script | What it does |
|-------|--------|-------------|
| SessionStart | session-start.js | Finds recent sessions, lists learned skills, reports available aliases |
| SessionEnd | session-end.js | Saves session state to `~/.claude/sessions/` |
| SessionEnd | evaluate-session.js | Extracts learnable patterns from the session |
| PreCompact | pre-compact.js | Logs compaction event, annotates active session file |
| PreToolUse:* | observe.sh pre | CL-v2: records prompt/tool call to observations.jsonl |
| PostToolUse:* | observe.sh post | CL-v2: records tool outcome to observations.jsonl |
| PreToolUse:Edit/Write | suggest-compact.sh | Counts tool calls, suggests `/compact` at threshold |

### Hooks NOT included (and why)

| Hook | Why excluded |
|------|-------------|
| Dev server protection (tmux) | Not relevant for Python workflows |
| Auto-Prettier | Not relevant (use ruff/black instead) |
| TypeScript type check | Not relevant |
| console.log detection | Not relevant |
| Markdown file blocking | Too opinionated |
| Git push reminder | Low value, adds friction |

---

## Scripts

Scripts are cross-platform Node.js utilities that implement hook behavior and provide shared libraries.

### How Scripts Work

- All scripts use Node.js for cross-platform compatibility
- Located in `~/.claude/scripts/` (installed from ECC's `scripts/` directory)
- Shared libraries in `scripts/lib/` provide common utilities
- Hook scripts are in `scripts/hooks/`
- Must exit with code 0 to not block Claude operations

### Key Scripts

#### lib/utils.js
**Purpose:** Cross-platform file, path, and system utilities
**Functions:** getSessionsDir(), getLearnedSkillsDir(), findFiles(), ensureDir(), appendFile(), log()

#### lib/package-manager.js
**Purpose:** Package manager detection (npm/pnpm/yarn/bun)
**Functions:** getPackageManager(), getSelectionPrompt()

#### hooks/session-start.js
**Purpose:** Load context on new session
**Actions:** Find recent sessions, list learned skills, list aliases, detect package manager

#### hooks/session-end.js
**Purpose:** Save state on session end
**Actions:** Write session state to `~/.claude/sessions/`

#### hooks/pre-compact.js
**Purpose:** Preserve state before compaction
**Actions:** Log compaction timestamp, annotate active session file

#### hooks/evaluate-session.js
**Purpose:** Extract patterns from completed sessions
**Actions:** Analyze session for learnable patterns, feed into CL-v2

#### hooks/suggest-compact.sh
**Purpose:** Strategic compaction suggestions
**Actions:** Count tool invocations, suggest `/compact` at configurable threshold (default: 50)

---

## Contexts

Contexts are dynamic system prompt injections that change Claude's behavior mode.

### How Contexts Work

- Located in `~/.claude/contexts/*.md`
- Selected manually by the user to change Claude's "mode"
- Injected into the system prompt alongside rules
- Only one context active at a time

### Available Contexts

| Context | Mode | Behavior changes |
|---------|------|-----------------|
| dev.md | Development | Increased detail, exploratory, implementation-focused |
| review.md | Code Review | Quality focus, security awareness, style enforcement |
| research.md | Research | Deep investigation, reading-focused, minimal edits |

**Note:** Contexts are optional. The workflow works fine without explicitly setting a context — the commands and agents already set appropriate behavior.

---

## MCP Server Configurations

ECC includes pre-configured MCP server definitions in `mcp-configs/mcp-servers.json`. These are templates — copy the ones you need to `~/.claude.json`.

### Relevant Servers

| Server | Command | Purpose | Notes |
|--------|---------|---------|-------|
| context7 | `npx -y @context7/mcp-server` | Live documentation lookup | Already configured |
| github | `npx -y @modelcontextprotocol/server-github` | GitHub PR/issue operations | Needs GITHUB_PERSONAL_ACCESS_TOKEN |
| sequential-thinking | `npx -y @modelcontextprotocol/server-sequential-thinking` | Chain-of-thought reasoning | No API key needed |

### Not Relevant (skip)

| Server | Why skip |
|--------|---------|
| memory | Redundant with CL-v2 + auto-memory |
| supabase | Not using Supabase |
| vercel | Not deploying to Vercel |
| railway | Not deploying to Railway |
| cloudflare-* (4 servers) | Not using Cloudflare |
| clickhouse | Not using ClickHouse |
| magic | UI components, not relevant |
| filesystem | Claude Code already has filesystem access |
| firecrawl | Web scraping — add later if needed |

### Important: Context Window Budget

> "Keep under 10 MCPs enabled to preserve context window." — ECC docs

Each enabled MCP server consumes context tokens just by being available (tool descriptions). With serena + context7 already configured, be selective about adding more.

---

## Continuous Learning System

The Continuous Learning v2 system is ECC's most sophisticated feature. It turns your coding sessions into reusable knowledge through automatic observation and pattern extraction.

### Architecture

```
Session Activity
      │
      │ Hooks capture prompts + tool use (100% reliable)
      ▼
observations.jsonl  (raw session data)
      │
      │ Observer agent reads (background, Haiku model)
      ▼
PATTERN DETECTION
  • User corrections → instinct
  • Error resolutions → instinct
  • Repeated workflows → instinct
      │
      │ Creates/updates
      ▼
instincts/personal/  (atomic learned behaviors)
  • prefer-functional.md (confidence: 0.7)
  • always-test-first.md (confidence: 0.9)
      │
      │ /evolve clusters
      ▼
evolved/  (higher-level structures)
  • commands/new-feature.md
  • skills/testing-workflow.md
  • agents/refactor-specialist.md
```

### Instinct Model

An instinct is a small learned behavior with:
- **Trigger** — When this pattern applies
- **Action** — What to do
- **Confidence** — 0.3 (tentative) to 0.9 (near-certain)
- **Domain** — code-style, testing, git, debugging, workflow, etc.
- **Evidence** — What observations created it

### Confidence Scoring

| Score | Meaning | Behavior |
|-------|---------|----------|
| 0.3 | Tentative | Suggested but not enforced |
| 0.5 | Moderate | Applied when relevant |
| 0.7 | Strong | Auto-approved for application |
| 0.9 | Near-certain | Core behavior |

**Increases when:** Pattern repeatedly observed, user doesn't correct it, other sources agree
**Decreases when:** User corrects behavior, pattern not observed for extended periods, contradicting evidence

### File Structure

```
~/.claude/homunculus/
├── identity.json           # Your profile, technical level
├── observations.jsonl      # Current session observations
├── observations.archive/   # Processed observations
├── instincts/
│   ├── personal/           # Auto-learned instincts
│   └── inherited/          # Imported from others
└── evolved/
    ├── agents/             # Generated specialist agents
    ├── skills/             # Generated skills
    └── commands/           # Generated commands
```

### Configuration

Located in CL-v2 skill's `config.json`:
- `observation.max_file_size_mb`: 10 (archive after this)
- `observation.archive_after_days`: 7
- `instincts.min_confidence`: 0.3
- `instincts.auto_approve_threshold`: 0.7
- `instincts.confidence_decay_rate`: 0.05
- `observer.model`: haiku (cheap, fast)
- `observer.run_interval_minutes`: 5
- `evolution.cluster_threshold`: 3 (minimum instincts to form cluster)

### Evolution Flow

When `/evolve` is run:
1. Reads all instincts from `~/.claude/homunculus/instincts/`
2. Groups by domain similarity, trigger overlap, action sequence
3. For each cluster of 3+ instincts:
   - → **Command** if instincts describe user-invoked actions
   - → **Skill** if instincts describe auto-triggered behaviors
   - → **Agent** if instincts describe complex multi-step processes
4. Preview what would be created
5. `--execute` flag to actually create the files

---

## Context & Memory Management

### Three Memory Layers

| Layer | Location | Managed by | Scope |
|-------|----------|-----------|-------|
| Claude auto-memory | `~/.claude/projects/*/memory/MEMORY.md` | Claude automatically | Per-project, persistent |
| CL-v2 instincts | `~/.claude/homunculus/instincts/` | Hooks + /evolve | Cross-project, persistent |
| Learned skills | `~/.claude/skills/learned/` | /learn command | Cross-project, persistent |

### Context Compaction Strategy

**Problem:** Claude auto-compacts at arbitrary points, often mid-task, losing important context.

**Solution:** The `strategic-compact` skill + hook proactively suggests compaction at logical boundaries:
- After exploration, before execution
- After completing a milestone
- Before major context shifts

**The suggest-compact hook:**
- Counts tool invocations in the session
- At threshold (default: 50 calls), suggests `/compact`
- Reminds every 25 calls after threshold
- You decide whether to compact or continue

### Session State Persistence

**SessionStart hook:** Loads previous session context + learned skills
**SessionEnd hook:** Saves session state for next session
**PreCompact hook:** Saves state before compaction occurs
**Checkpoint command:** Explicit named save points with git SHA

### Best Practices

1. **Compact between phases** — After planning is done, before starting TDD
2. **Don't compact mid-implementation** — Preserve context for related changes
3. **Use checkpoints** — Named save points let you verify progress
4. **Trust the hooks** — CL-v2 captures patterns automatically; you don't need to manually track everything

---

## Feature Selection Guide

### By Language

| Language | Agents | Commands | Skills | Rules |
|----------|--------|----------|--------|-------|
| **Python** | python-reviewer, tdd-guide | /python-review, /tdd | python-patterns, python-testing | python-coding-style, python-testing, python-patterns |
| **Go** | go-reviewer*, go-build-resolver* | /go-review*, /go-test*, /go-build* | golang-patterns*, golang-testing* | golang/* rules* |
| **Rust** | (none specific) | /tdd, /code-review | coding-standards | common rules |
| **SQL** | (none specific) | /code-review | backend-patterns | common rules |

*= not installed by default, add later

### By Workflow Phase

| Phase | Commands | Agents | Skills |
|-------|----------|--------|--------|
| Ideation | /brainstorming | — | brainstorming |
| Planning | /plan | planner, architect | coding-standards |
| Implementation | /tdd | tdd-guide | tdd-workflow, python-patterns |
| Verification | /verify, /eval | — | verification-loop, eval-harness |
| Review | /code-review, /python-review | code-reviewer, python-reviewer | coding-standards |
| Learning | /learn, /evolve | — | continuous-learning-v2 |
| Maintenance | /refactor-clean, /test-coverage | refactor-cleaner | — |

### By Frequency of Use

| Frequency | Features |
|-----------|----------|
| **Every session** | Rules (auto), CL-v2 hooks (auto), /tdd, /verify |
| **Most sessions** | /plan, /checkpoint, /code-review |
| **Feature start** | /brainstorming |
| **Feature end** | /done, /learn |
| **Weekly/biweekly** | /evolve, /instinct-status |
| **Occasionally** | /eval, /refactor-clean, /skill-create, /test-coverage |

---

## Appendix: Features Not Included

### Multi-Agent Orchestration (v1.4)
- `/orchestrate` — Sequential agent chaining (planner → tdd → reviewer)
- `/multi-plan` — Multi-model planning (Claude + Codex + Gemini)
- `/multi-execute`, `/multi-backend`, `/multi-frontend`, `/multi-workflow`
- **Why excluded:** Overkill for one-feature-at-a-time workflow. Manual control preferred initially. /multi-plan requires external model API keys.

### Session Management
- `/sessions` — List, load, alias, info for session history
- **Why excluded:** Lower priority for one-feature-at-a-time work. Add later if needed.

### Documentation Generation
- `/update-codemaps` — Auto-generate architecture documentation
- `/update-docs` — Refresh README and guides from code
- **Why excluded:** Lower priority. Add when documentation needs grow.

### Security
- `/security` command, security-reviewer agent, security rules
- **Why excluded:** Per user preference.

### Language-Specific (not currently used)
- Django skills (4), Spring Boot skills (4), TypeScript rules, JPA patterns
- **Why excluded:** Not using these frameworks.

### E2E Testing
- `/e2e` command, e2e-runner agent
- **Why excluded:** Playwright/browser testing not relevant for Python/SQL.
