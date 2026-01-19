# Superpowers

**Repository**: [obra/superpowers](https://github.com/obra/superpowers)
**License**: MIT
**Author**: Jesse Vincent (@obra)
**Current Version**: v4.0.3

---

## Overview

**Superpowers** is a comprehensive software development workflow framework designed for coding agents. Built on a set of composable "skills," it guides AI assistants through structured development processes from initial ideation through implementation, testing, and code review.

> "A complete software development workflow for your coding agents, built on top of a set of composable 'skills.'"

The framework emphasizes **Test-Driven Development (TDD)**, systematic processes over ad-hoc approaches, and verification-based validation. Skills trigger automatically based on context—no special user intervention required beyond initial setup.

---

## Capabilities & Features

### Seven-Stage Workflow

Superpowers guides agents through a structured development lifecycle:

| Stage | Description |
|-------|-------------|
| **1. Brainstorming** | Refines rough ideas through Socratic questioning, explores alternatives, presents designs in sections for validation |
| **2. Git Worktree Management** | Creates isolated development branches/workspaces before implementation begins |
| **3. Plan Writing** | Breaks tasks into 2-5 minute chunks with exact specifications and verification criteria |
| **4. Execution** | Dispatches subagents or batch processes with two-stage review checkpoints |
| **5. Test-Driven Development** | Enforces RED-GREEN-REFACTOR cycles; tests must be written before implementation |
| **6. Code Review** | Severity-based issue reporting with blockers for critical problems; validates against original plan |
| **7. Branch Completion** | Merge/PR decision workflows with cleanup |

### Skills Library (14 Core Skills)

| Skill | Purpose |
|-------|---------|
| **Brainstorming** | Interactive ideation and design refinement |
| **Writing Plans** | Creating detailed development strategies |
| **Executing Plans** | Implementing strategies and action items |
| **Subagent-Driven Development** | Coordinating subsidiary agents for task completion |
| **Dispatching Parallel Agents** | Running multiple agents simultaneously |
| **Test-Driven Development** | Writing tests first with anti-patterns reference |
| **Systematic Debugging** | 4-phase root cause analysis with verification |
| **Requesting Code Review** | Initiating peer review processes |
| **Receiving Code Review** | Accepting and responding to feedback |
| **Verification Before Completion** | Quality assurance validation steps |
| **Using Git Worktrees** | Managing multiple working trees in Git |
| **Finishing a Development Branch** | Branch completion and cleanup |
| **Using Superpowers** | Core orchestration and skill coordination |
| **Writing Skills** | Framework for creating custom skills |

### Architecture

```
superpowers/
├── skills/       # Composable workflow modules (14 skills)
├── commands/     # CLI interfaces
├── agents/       # Subagent coordination
├── hooks/        # Integration points
├── lib/          # Core utilities
└── tests/        # Quality assurance
```

### Key Design Principles

1. **Test-First Methodology**: Tests are written before implementation code, always
2. **Systematic Over Ad-Hoc**: Structured processes over intuition-based development
3. **Simplicity as Design Goal**: Complexity reduction is explicit
4. **Evidence-Based Verification**: Verify with evidence, never assume success
5. **Executable Flowcharts**: Complex skills use graphviz/dot diagrams as primary instructions

---

## Platform Compatibility

Superpowers supports multiple AI coding platforms:

| Platform | Installation Method | Status |
|----------|---------------------|--------|
| **Claude Code** | Plugin marketplace | ✅ Full support |
| **Codex** | Manual setup via remote instructions | ✅ Supported |
| **OpenCode** | Remote installation guide | ✅ Supported |
| **Cursor IDE** | PR in progress (#271) | 🚧 In development |
| **GitHub Copilot Agent Mode** | PR open (#218) | 🚧 In development |
| **Continue** | PR in progress (#302) | 🚧 In development |
| **Antigravity** | PR in progress (#192) | 🚧 In development |

### Installation Examples

**Claude Code:**
```bash
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**OpenCode/Codex:**
Manual configuration via remote instruction URLs (see repository for details).

---

## Popularity

| Metric | Value |
|--------|-------|
| **GitHub Stars** | 29,600+ |
| **Forks** | 2,200+ |
| **Contributors** | 13 active |
| **Commits** | 233+ on main |
| **Open Issues** | 64 |
| **Open PRs** | 22 |
| **License** | MIT |

This is one of the most popular AI coding workflow frameworks, significantly ahead of alternatives like oh-my-opencode (9k stars) and claude-flow (~500 stars).

---

## Alignment with Personal Workflow Goals

Based on the goals in `GOALS.md`:

### ✅ Goals That Superpowers SUPPORTS

| Goal | How It's Supported |
|------|-------------------|
| **Specialized sub-agents** | Core feature—subagent-driven development with parallel agent dispatching. Agents are initialized with fresh context via dedicated skills. |
| **Easy to extend and customize** | Custom skills via `writing-skills` framework. Skills are composable and can be added to the skills directory following documented patterns. |
| **Based on popular, actively developed tools** | 29.6k stars, 13 active contributors, frequent updates (v4.0.3 recent). One of the most popular frameworks in this space. |
| **Not overly complex** | Philosophy explicitly emphasizes simplicity as a design goal. Skills are self-contained and trigger automatically. |
| **Opinionated** | Strong opinions on TDD, systematic debugging, and verification-before-completion. Enforces specific workflows. |
| **Free and open source** | MIT licensed. |
| **Fresh context for sub-agents** | Subagent-driven development explicitly provides relevant details to sub-agents with clean context windows. |

### ✅ Goals That Are WELL Supported

| Goal | Assessment |
|------|------------|
| **Provider/model agnostic** | Works with Claude Code, Codex, OpenCode. Cursor, Continue, and Copilot support in active development. The skills themselves are model-agnostic—they're workflow patterns, not model-specific code. |
| **IDE/CLI/Environment agnostic** | Multi-platform support with active PRs for additional IDEs. Already supports CLI tools (Claude Code, Codex, OpenCode). |
| **Easy to install** | Plugin marketplace for Claude Code. Manual but documented setup for other platforms. |
| **Easy to maintain and update** | Auto-updates via `/plugin update superpowers`. Active maintainer (Jesse Vincent) with responsive issue handling. |

### ⚠️ Goals That Are PARTIALLY Supported

| Goal | Assessment |
|------|------------|
| **Consume usage from provider subscriptions (Cursor, Copilot, etc.)** | *Depends on platform*: When used with Claude Code, uses your Claude subscription. When used with Codex via API, uses API quota. The skills themselves don't control billing—that's determined by the underlying platform. If Claude Code or Cursor use subscription billing, Superpowers inherits that. |

### ❌ Goals That Are NOT Well Supported

| Goal | Gap |
|------|-----|
| **Automatic memory of project details** | **Not built-in**: No persistent memory system that learns from completed tasks or maintains lessons learned. The framework focuses on per-task workflows, not cross-session project memory. You'd need to implement this separately (e.g., via CLAUDE.md files, external memory systems). |

### Summary Table

| Goal | Support Level |
|------|---------------|
| Provider/model agnostic | ✅ Yes |
| IDE/CLI/Environment agnostic | ✅ Yes (with more in development) |
| Consume subscription usage (not API) | ⚠️ Platform-dependent |
| Easy to install | ✅ Yes |
| Easy to extend/customize | ✅ Yes |
| Easy to maintain/update | ✅ Yes |
| Popular, actively developed base | ✅ Very popular (29.6k stars) |
| Not overly complex | ✅ Explicit design goal |
| Opinionated | ✅ Strongly opinionated |
| Free and open source | ✅ MIT |
| Specialized sub-agents | ✅ Core feature |
| Fresh context for sub-agents | ✅ Built-in |
| Automatic project memory | ❌ Not built-in |

---

## Future Features / Roadmap

No explicit roadmap document exists, but development direction can be inferred from **open PRs and recent commits**:

### Active Development (Open PRs)

| Feature | PR | Progress |
|---------|-----|----------|
| **Cursor IDE integration** | #271 | 5/9 tasks complete |
| **Continue integration** | #302 | 6/9 tasks complete |
| **GitHub Copilot Agent Mode** | #218 | Open |
| **Antigravity IDE integration** | #192 | 7/9 tasks complete |
| **Factory Droid CLI support** | #139 | 6/9 tasks complete |
| **Skill integration system** (artifacts & tasks) | #300 | In progress |
| **Git worktrees enhancement** (pre-flight checks, TDD tests) | #288 | In progress |
| **WSL bash handling** (Windows compatibility) | #282 | In progress |
| **GitHub project management skill** | #121 | Draft |

### Recent Development Themes (from commits)

1. **Skill Architecture Refinements**: Consolidating debugging/testing guidance into unified skills
2. **Executable Flowcharts**: Using graphviz/dot diagrams as primary instructions for complex skills
3. **Two-Stage Code Review**: Specification compliance first, then quality assessment
4. **Improved Context Handling**: Better skill invocation when users explicitly request skills
5. **Cross-Platform Stability**: Windows/WSL compatibility, PowerShell support improvements

### Known Issues Being Addressed

- Windows startup problems after installation
- Model switching breaking skill invocation
- Custom personal skills not discovered with certain environment variables
- Inconsistent file reference syntax across skills

---

## Additional Notes

### Philosophy Alignment

Superpowers' philosophy aligns well with professional development practices:

> "Test-Driven Development — Write tests first, always"
> "Systematic over ad-hoc — Follow structured processes"
> "Simplicity is a feature — Reduce complexity actively"
> "Verification over assumption — Prove with evidence"

### Interesting Design Choices

1. **Automatic Skill Triggering**: Skills activate based on context without explicit user commands. This reduces cognitive load but requires understanding which skills exist.

2. **Two-Stage Validation**: Code review has explicit phases—specification compliance followed by quality assessment. This separation catches different types of issues.

3. **Executable Flowcharts**: Complex skills use graphviz/dot diagrams as authoritative instructions. This prevents Claude from taking shortcuts by reading workflow summaries.

4. **2-5 Minute Task Chunks**: Plans break work into small, verifiable units. This aligns with incremental development and makes verification practical.

5. **Subagent Fresh Context**: Sub-agents receive relevant context without parent conversation history. This prevents context pollution and keeps agents focused.

### Comparison to Similar Tools

| Aspect | Superpowers | oh-my-opencode-slim | claude-flow |
|--------|-------------|---------------------|-------------|
| Stars | 29,600+ | 72 | ~500 |
| Platform | Multi-platform | OpenCode only | Claude only |
| Focus | Full workflow | Agent orchestration | Orchestration |
| TDD Emphasis | Core principle | Not emphasized | Not emphasized |
| Skill System | 14 composable skills | Themed agents | Workflow nodes |
| Memory | Not built-in | Not built-in | External |

### When to Use Superpowers

**Use Superpowers if you:**
- Want structured, TDD-focused development workflows
- Use Claude Code, Codex, or OpenCode (or want Cursor/Continue when ready)
- Value opinionated, well-documented practices
- Need subagent coordination with fresh context
- Want a popular, actively maintained framework

**Consider alternatives if you:**
- Need built-in project memory/learning
- Want full control over agent model selection per task
- Prefer less opinionated, more flexible frameworks
- Need platform support that isn't yet available

---

## Conclusion

Superpowers is an excellent fit for the goals in `GOALS.md`. It strongly supports:
- Provider/model agnostic workflows (multi-platform)
- IDE/environment flexibility (with more platforms coming)
- Specialized sub-agents with fresh context
- Easy extension via the skill-writing framework
- An opinionated but not overly complex design

The main gap is **automatic project memory**—Superpowers focuses on per-task workflows, not cross-session learning. This would need to be implemented separately, potentially via CLAUDE.md files, external memory systems, or a complementary tool.

Given its popularity (29.6k stars), active development, and philosophical alignment with professional development practices (TDD, systematic processes, verification), Superpowers is a strong candidate for integration into a personal AI development workflow. The expanding platform support (Cursor, Continue, Copilot in development) makes it increasingly environment-agnostic.
