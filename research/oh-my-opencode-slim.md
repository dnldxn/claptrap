# oh-my-opencode-slim

**Repository**: [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim)  
**License**: MIT  
**Parent Project**: [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) by @code-yeongyu

---

## Overview

**oh-my-opencode-slim** is a lightweight, token-efficient fork of Oh My OpenCode—a powerful agent orchestration plugin for the [OpenCode CLI](https://opencode.ai). The slim version focuses on reducing token consumption while preserving core orchestration capabilities.

> "Slimmed and cleaned oh-my-opencode, consumes much less tokens."

The plugin transforms OpenCode into a manager capable of delegating complex tasks to specialized sub-agents, running searches in the background, and managing multi-step workflows.

**Note**: The plugin is tuned for **Antigravity** model routing. Other providers work, but you'll get the best experience with Antigravity subscription.

---

## Capabilities & Features

### Specialized Agents ("The Pantheon")

oh-my-opencode-slim includes a themed set of specialized agents:

| Agent | Role | Model |
|-------|------|-------|
| **The Orchestrator** (Sisyphus) | Default task manager; delegates to specialists, handles planning | `google/claude-opus-4-5-thinking` |
| **The Explorer** (Pathfinder) | Codebase reconnaissance; regex search, AST matching, file discovery | `cerebras/zai-glm-4.6` |
| **The Oracle** | Strategic advisor; root cause analysis, architecture review, debugging | `openai/gpt-5.2-codex` |
| **The Librarian** | External knowledge retrieval; docs, GitHub search, best practices | `google/gemini-3-flash` |
| **The Designer** | UI/UX implementation; CSS/Tailwind, micro-animations, responsive design | `google/gemini-3-flash` |
| **The Scribe** | Documentation; README crafting, API docs, inline comments | `google/gemini-3-flash` |
| **The Visionary** | Image/visual analysis; screenshots, wireframes, diagrams, PDFs | `google/gemini-3-flash` |
| **The Minimalist** | Code simplification; YAGNI enforcement, complexity reduction | `google/claude-opus-4-5-thinking` |

### Tools & Capabilities

**Background Tasks**
- `background_task`: Launch agents in new sessions (sync or async)
- `background_output`: Fetch results by task ID
- `background_cancel`: Abort running tasks

**LSP Integration**
- `lsp_goto_definition`: Jump to symbol definition
- `lsp_find_references`: Find all usages across workspace
- `lsp_diagnostics`: Get errors/warnings from language server
- `lsp_rename`: Rename symbols across all files

**Code Search**
- `grep`: Fast content search using ripgrep
- `ast_grep_search`: AST-aware pattern matching (25 languages)
- `ast_grep_replace`: AST-aware refactoring with dry-run support

**MCP Servers** (built-in, enabled by default)
| MCP | Purpose | URL |
|-----|---------|-----|
| websearch | Real-time web search via Exa AI | `https://mcp.exa.ai/mcp` |
| context7 | Official library documentation | `https://mcp.context7.com/mcp` |
| grep_app | GitHub code search via grep.app | `https://mcp.grep.app` |

MCPs can be disabled via configuration.

### Configuration

Configuration files (JSON):
- **User Global**: `~/.config/opencode/oh-my-opencode-slim.json`
- **Project Local**: `./.opencode/oh-my-opencode-slim.json`

Features can be toggled:
```json
{
  "disabled_agents": ["multimodal-looker", "code-simplicity-reviewer"],
  "disabled_mcps": ["websearch", "grep_app"]
}
```

---

## Popularity

| Metric | oh-my-opencode (parent) | oh-my-opencode-slim |
|--------|-------------------------|---------------------|
| Stars | 9,000+ | 72 |
| Forks | 600+ | 5 |
| Contributors | 31+ | 1 (fork maintainer) |
| Releases | 85+ | 19 commits |

The slim version is a niche fork aimed at users who want reduced token overhead. The parent project has significant traction in the OpenCode ecosystem.

---

## Alignment with Personal Workflow Goals

Based on the goals in `GOALS.md`:

### ✅ Goals That oh-my-opencode-slim SUPPORTS

| Goal | How It's Supported |
|------|-------------------|
| **Specialized sub-agents** | Core strength—The Pantheon includes dedicated agents for research (Librarian), code exploration (Explorer), review (Minimalist), design (Designer), etc. Each agent can be launched in a background task with fresh context. |
| **Easy to extend and customize** | Supports custom agents, skills, and commands via `.opencode/` configuration. Agents can be enabled/disabled. Skills are added via `SKILL.md` files. |
| **Easy to install** | Interactive installer: `bunx oh-my-opencode-slim install` with TUI or non-interactive flags. |
| **Based on popular, actively developed tools** | Built on OpenCode, a well-maintained CLI. Parent project (oh-my-opencode) has frequent updates and 85+ releases. |
| **Free and open source** | MIT licensed. |

### ⚠️ Goals That Are PARTIALLY Supported

| Goal | Assessment |
|------|------------|
| **Provider/model agnostic** | *Partial*: Supports multiple providers (OpenAI, Anthropic via Google, Cerebras), but the agents are pre-configured with specific model preferences. Tuned for Antigravity subscription which provides model routing. You can configure models, but default setup favors specific providers. |
| **IDE/CLI/Environment agnostic** | *Partial*: Only works with **OpenCode CLI**—it's a plugin specifically for that tool. Does not work directly with Cursor, VS Code, or other IDEs. OpenCode itself is CLI-based. |
| **Opinionated but not overly complex** | *Partial*: The Pantheon provides opinionated defaults, but the full feature set (hooks, MCPs, LSP, background tasks) can add complexity. The "slim" version reduces this somewhat. |

### ❌ Goals That Are NOT Well Supported

| Goal | Gap |
|------|-----|
| **Consume usage from provider subscriptions (Cursor, Copilot, etc.)** | **Major gap**: oh-my-opencode-slim uses per-request API usage, not IDE subscription quotas. Requires API keys for Antigravity, OpenAI, etc. This does not integrate with Cursor Pro, GitHub Copilot, or Claude Max subscriptions. |
| **Automatic memory of project details** | **Not built-in**: There's no persistent memory system that learns from completed tasks or maintains lessons learned. Session recovery exists (hooks), but not long-term project memory. You'd need to implement this separately. |
| **Easy to maintain and update** | *Risk*: The slim fork has a single maintainer and may lag behind the parent project. Depending on a fork introduces maintenance risk. |

### Summary Table

| Goal | Support Level |
|------|---------------|
| Provider/model agnostic | ⚠️ Partial |
| IDE/CLI/Environment agnostic | ❌ OpenCode-only |
| Consume subscription usage (not API) | ❌ Uses API keys |
| Easy to install | ✅ Yes |
| Easy to extend/customize | ✅ Yes |
| Easy to maintain/update | ⚠️ Fork risk |
| Popular, actively developed base | ✅ Parent is active |
| Not overly complex | ⚠️ Partial |
| Opinionated | ✅ Yes |
| Free and open source | ✅ MIT |
| Specialized sub-agents | ✅ Core feature |
| Fresh context for sub-agents | ✅ Background tasks |
| Automatic project memory | ❌ Not built-in |

---

## Future Features / Roadmap

**No roadmap or future features are documented** for oh-my-opencode-slim specifically.

The parent project (oh-my-opencode) has **experimental features** that hint at direction:
- **Preemptive compaction**: Automatic context compression
- **Aggressive truncation**: Configurable output limits
- **Auto-resume sessions**: Session recovery improvements
- **Dynamic context pruning (DCP)**: Intelligent context management

Recent releases of the parent (v2.13.0) include:
- Maximum Reasoning Effort Mode
- Improved slash command system
- More flexible MCP disabling
- Performance improvements (parallel startup)

The slim fork would likely inherit these features over time, though it may lag behind the parent project.

---

## Additional Notes

### Installation

```bash
# Interactive
bunx oh-my-opencode-slim install

# Non-interactive
bunx oh-my-opencode-slim install --no-tui --antigravity=yes --openai=yes --cerebras=no
```

### Comparison: Slim vs Full

| Aspect | oh-my-opencode (full) | oh-my-opencode-slim |
|--------|----------------------|---------------------|
| Token usage | Higher | Lower (optimized) |
| Agents | Full Pantheon + extras | Core Pantheon |
| Hooks | 20+ built-in | Reduced set |
| MCPs | All enabled | Configurable |
| Experimental features | All available | May be disabled |

### When to Use Slim

**Use slim if you:**
- Want core agent orchestration without overhead
- Are cost-conscious about token usage
- Need faster responses with less context
- Prefer a lighter-weight setup

**Use full version if you:**
- Need all experimental features
- Want maximum context and reasoning depth
- Require all 20+ hooks
- Need bleeding-edge updates

### Interesting Design Choices

1. **Themed agent naming**: "The Pantheon" with mythological/archetypal names adds character and makes agent roles memorable.

2. **Read-only agents**: Several agents (Oracle, Minimalist, Explorer) are explicitly read-only—they analyze and advise but don't make changes directly. This separation of concerns reduces risk.

3. **Model diversity**: Different agents use different models optimized for their tasks (thinking models for planning, fast models for search/docs).

4. **Antigravity integration**: The `antigravity_quota` tool shows API quota across all Antigravity accounts with progress bars—useful for cost management.

---

## Conclusion

oh-my-opencode-slim is a solid choice for **OpenCode users** who want specialized sub-agents without heavy token overhead. Its agent orchestration model aligns well with the goal of delegating tasks to specialists.

However, it has significant gaps for a provider-agnostic, IDE-agnostic workflow that consumes subscription quotas rather than API usage. It's tied to OpenCode CLI and requires API keys for model providers.

For the goals in `GOALS.md`, consider oh-my-opencode-slim as **inspiration for agent design patterns** (The Pantheon, background tasks, MCP integration) rather than a direct solution, unless OpenCode CLI with API-based usage fits your workflow.
