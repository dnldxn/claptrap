# Agentic Development Workflow Design

**Date:** 2026-02-10
**Status:** Draft
**Scope:** Claude Code + OpenCode agentic workflow using ECC + Superpowers brainstorming

## Overview

A complete agentic development workflow that guides features from idea → design → plan → implementation → review → learning. Built on Everything Claude Code (ECC) as the primary foundation with Superpowers brainstorming for ideation. Supports Python (primary), Snowflake SQL, and occasional Go/Rust.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Foundation | ECC-primary | More features, language coverage, learning system |
| Ideation | Superpowers brainstorming | Better conversational design process than ECC's planning |
| Learning | Continuous Learning v2 | Instinct-based with confidence scoring, auto-observation |
| Testing | TDD always | RED-GREEN-REFACTOR enforced via tdd-guide agent |
| Work style | One feature at a time | Simplifies session/context management |
| Config scope | Global (~/.claude/) | Available to all projects, override per-project in CLAUDE.md |
| Naming | Symlinks without prefix | Natural command names, uninstall by checking symlink targets |
| Archival | /done command | Automated verify + learn + checkpoint + archive + tag |

## Workflow Phases

### Phase 1: Ideation — `/brainstorming`

- Agent checks project state (files, docs, commits)
- Asks questions one at a time to refine the idea
- Proposes 2-3 approaches with trade-offs and recommendation
- Presents design in 200-300 word sections, validating each
- Writes design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Commits the design document

### Phase 2: Planning — `/plan`

- Planner agent reads the design document
- Analyzes affected codebase components
- Creates phased implementation plan with exact file paths, dependencies, risks
- Testing strategy per phase

### Phase 3: Implementation — `/tdd`

- TDD guide agent enforces RED-GREEN-REFACTOR
- RED: Write failing test → GREEN: Minimal code to pass → REFACTOR: Clean up
- 80%+ code coverage target
- `/checkpoint create "phase-N-done"` between phases

### Phase 4: Verification — `/verify`

- Build check → type check (mypy) → lint (ruff) → test suite
- Reports pass/fail with coverage percentage
- "Ready for PR: YES/NO" verdict

### Phase 5: Review — `/code-review` + `/python-review`

- Code reviewer: quality, maintainability, patterns
- Python reviewer: PEP 8, type hints, Python idioms
- Actionable findings with fix suggestions

### Phase 6: Completion — `/done` (custom command)

1. `/verify full` — ensure everything passes
2. `/learn` — extract patterns from session
3. `/checkpoint create "feature-complete"`
4. Move design doc to `docs/archive/`
5. Git tag: `feature/<topic>-done`
6. Commit with conventional message

### Ongoing: Learning — `/evolve`

- CL-v2 hooks capture instincts passively every session
- `/learn` for explicit pattern extraction
- `/evolve` periodically (weekly/biweekly) to cluster instincts into skills
- `/instinct-status` to review learned patterns

## Installed Features

### Agents (8)

| Agent | Purpose |
|-------|---------|
| planner | Feature planning and implementation breakdown |
| architect | System design, scalability, technical decisions |
| code-reviewer | Code quality, maintainability review |
| python-reviewer | Python-specific review (PEP 8, type hints) |
| tdd-guide | TDD enforcement, 80%+ coverage |
| refactor-cleaner | Dead code detection and removal |
| doc-updater | Documentation and codemap generation |
| build-error-resolver | Build error fixes with minimal diffs |

### Commands (16+1 custom)

| Command | Phase | Purpose |
|---------|-------|---------|
| `/brainstorming` | 1 | Ideation via conversational design |
| `/plan` | 2 | Implementation plan generation |
| `/tdd` | 3 | Test-driven development loop |
| `/verify` | 4 | Build + lint + test verification |
| `/code-review` | 5 | Code quality review |
| `/python-review` | 5 | Python-specific review |
| `/done` | 6 | Feature completion automation (custom) |
| `/checkpoint` | Any | Named save points with git SHA |
| `/learn` | Any | Manual pattern extraction |
| `/evolve` | Periodic | Cluster instincts into skills |
| `/eval` | Any | Eval-driven development |
| `/instinct-status` | Any | View learned instincts |
| `/instinct-import` | Any | Import instincts from others |
| `/instinct-export` | Any | Export instincts for sharing |
| `/skill-create` | Any | Generate skills from git history |
| `/refactor-clean` | Any | Dead code removal |
| `/test-coverage` | Any | Coverage analysis |

### Skills (11)

| Skill | Purpose |
|-------|---------|
| brainstorming | Conversational design process (Superpowers) |
| continuous-learning-v2 | Instinct-based learning with hooks |
| iterative-retrieval | Progressive context refinement |
| tdd-workflow | TDD methodology reference |
| verification-loop | Continuous verification patterns |
| eval-harness | Evaluation framework |
| coding-standards | Language-agnostic best practices |
| python-patterns | Python idioms and patterns |
| python-testing | pytest and TDD for Python |
| strategic-compact | Manual compaction suggestions |
| backend-patterns | API, database, caching patterns |

### Rules (9)

| Rule | Source | Purpose |
|------|--------|---------|
| coding-style.md | ECC common | Immutability, naming, file org |
| git-workflow.md | ECC common | Conventional commits, PR process |
| testing.md | ECC common | TDD requirements, 80% coverage |
| performance.md | ECC common | Context management, model selection |
| patterns.md | ECC common | Design patterns, SOLID |
| agents.md | ECC common | When to delegate to subagents |
| python-coding-style.md | ECC python | PEP 8, ruff, mypy |
| python-testing.md | ECC python | pytest, fixtures, coverage |
| python-patterns.md | ECC python | Python design patterns |

### Hooks

| Event | Script | Purpose |
|-------|--------|---------|
| SessionStart | session-start.js | Load previous context + learned skills |
| SessionEnd | session-end.js | Save session state |
| SessionEnd | evaluate-session.js | Extract patterns for CL-v2 |
| PreCompact | pre-compact.js | Save state before compaction |
| PreToolUse | observe.sh pre | CL-v2 observation (all tool calls) |
| PostToolUse | observe.sh post | CL-v2 observation (all tool calls) |
| PreToolUse:Edit/Write | suggest-compact.sh | Strategic compaction suggestions |
| PostToolUse:Bash | remind-git-push.js | Warn before git push |

## Context & Memory Architecture

### Three Memory Layers

| Layer | Location | Purpose |
|-------|----------|---------|
| Claude auto-memory | `~/.claude/projects/*/memory/MEMORY.md` | Per-project notes, auto-managed |
| CL-v2 instincts | `~/.claude/homunculus/instincts/` | Learned behaviors with confidence |
| Learned skills | `~/.claude/skills/learned/` | Explicitly extracted patterns |

### Context Management

- `strategic-compact` skill suggests when to `/compact` at logical boundaries
- `pre-compact.js` hook preserves state before auto-compaction
- `session-start.js` hook loads previous context on new sessions
- `/checkpoint` for explicit state management between phases

## Installation

### Method: Symlinks without prefix

- `install.py` creates symlinks from `~/.claude/{agents,skills,commands,rules}/` → project source files
- No `ct-` prefix; natural command names (`/plan`, not `/ct-plan`)
- Uninstall: remove symlinks whose targets resolve to the project directory
- Supports both Claude Code (`~/.claude/`) and OpenCode (`~/.config/opencode/`)

### Directory Structure

```
~/.claude/
├── agents/          → symlinks to ECC agent .md files
├── skills/          → symlinks to ECC/Superpowers skill dirs
├── commands/        → symlinks to ECC command .md files + custom done.md
├── rules/           → symlinks to ECC rule .md files
├── hooks/hooks.json → hook configuration
├── homunculus/      → CL-v2 learning data
│   ├── instincts/
│   └── evolved/
├── evals/           → eval definitions
├── sessions/        → session state files
└── checkpoints.log  → checkpoint log
```

### MCP Servers

Already configured: `serena`, `context7`
Optional additions: `github` (if using GitHub regularly), `sequential-thinking`

## Cross-Session Workflow Example

```
Session 1: /brainstorming → design doc
  └─ CL-v2 hooks capture instincts
  └─ /checkpoint create "design-ready"

Session 2: /plan → implementation plan
  └─ CL-v2 hooks capture instincts
  └─ /checkpoint create "plan-ready"

Session 3: /tdd → Phase 1-2 implementation
  └─ /learn (if notable solutions)
  └─ /checkpoint create "phase-2-done"

Session 4: /tdd → Phase 3 + /verify + /code-review + /python-review
  └─ /done → archive, tag, commit

Every 1-2 weeks: /evolve → cluster instincts into skills
```

## Excluded Features

| Feature | Why excluded |
|---------|-------------|
| /multi-* commands | Overkill for one-feature-at-a-time work |
| /orchestrate | Manual control preferred initially |
| /e2e | Playwright/browser testing not relevant |
| /security, security rules | Per user preference |
| Django/Spring Boot skills | Not relevant |
| Supabase/Vercel/Railway MCPs | Not relevant |
| TypeScript/frontend rules | Not relevant |
| /setup-pm, /pm2 | Package manager/PM2 not relevant |

## Next Steps

1. Update `bootstrap/config.yml` with full feature list
2. Update `bootstrap/install.py` to remove ct- prefix, add symlink-target-based uninstall
3. Create custom `/done` command
4. Configure hooks in `~/.claude/settings.json`
5. Initialize CL-v2 directory structure
6. Test the full workflow on a small feature
