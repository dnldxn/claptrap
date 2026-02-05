# GitHub Copilot

> Documentation for GitHub Copilot customization, syntax, models, tools, and CLI usage.
> Source: https://docs.github.com/en/copilot

---

## 1. Custom Subagents, Slash Commands, Skills

### Supported Features

| Feature | Supported | Description |
|---------|-----------|-------------|
| **Custom Agents** | ✅ Yes | Agent profiles defined via `.agent.md` files |
| **Agent Skills** | ✅ Yes | Skill directories with `SKILL.md` files |
| **Custom Instructions** | ✅ Yes | Repository-wide and path-specific instruction files |
| **Slash Commands** | ✅ Built-in | `/agent`, `/model`, `/mcp`, etc. (not user-definable yet) |
| **Subagents** | ⚠️ Limited | Via `handoffs` property in agent profiles |

**Note:** User-level prompts and instructions are managed via VS Code profiles/settings sync and are not stored in local prompt files. Claptrap installs Copilot files at the repo level only (under `.github/`).

### Directory Structure

```
~/.copilot/
├── agents/                      # User-level custom agents
│   └── *.agent.md
├── skills/                      # User-level skills
│   └── <skill-name>/
│       └── SKILL.md
└── mcp-config.json              # MCP server configuration

<repo-root>/
├── .github/
│   ├── agents/                  # Repository-level agents
│   │   └── *.agent.md
│   ├── skills/                  # Repository-level skills
│   │   └── <skill-name>/
│   │       └── SKILL.md
│   ├── instructions/            # Path-specific instructions
│   │   └── *.instructions.md
│   ├── copilot-instructions.md  # Repository-wide instructions
│   └── prompts/                 # Prompt templates (experimental)
│       └── *.prompt.md
├── AGENTS.md                    # Simple agent instructions
├── CLAUDE.md                    # Claude-specific instructions
└── GEMINI.md                    # Gemini-specific instructions

# Organization/Enterprise level
.github-private/
└── agents/                      # Org-wide agents (root level)
    └── *.agent.md
```

### Agent Locations

| Scope | Location |
|-------|----------|
| User-level | `~/.copilot/agents/` |
| Repository | `.github/agents/` |
| Organization/Enterprise | `/agents/` in `.github-private` repo |

---

## 2. Frontmatter & File Syntax

### Custom Agent Profiles (.agent.md)

Agent profiles use **YAML frontmatter** in Markdown:

```markdown
---
name: code-reviewer
description: |
  Expert code reviewer that analyzes code for bugs, security issues,
  and best practices violations.
model: claude-sonnet-4
tools:
  - read
  - edit
  - search
target: vscode
infer: true
---

# Code Reviewer Agent

You are an expert code reviewer. When reviewing code:

1. Check for security vulnerabilities
2. Identify performance issues
3. Suggest improvements for maintainability

## Response Format

Always structure your reviews with:
- **Summary**: Brief overview
- **Issues**: Prioritized list of problems
- **Suggestions**: Recommended improvements
```

#### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Display name (defaults to filename) |
| `description` | string | **Yes** | What the agent does |
| `model` | string | No | AI model to use (IDE-specific) |
| `tools` | array | No | List of allowed tools |
| `target` | string | No | `vscode`, `github-copilot`, or omit for both |
| `infer` | boolean | No | Auto-select based on context |
| `mcp-servers` | object | No | MCP server configuration (org/enterprise) |
| `metadata` | object | No | Custom annotations |
| `handoffs` | array | No | Other agents this agent can delegate to |
| `argument-hint` | string | No | Hint for required arguments |

### Skills (SKILL.md)

```markdown
---
name: api-testing
description: |
  Specialized in testing REST APIs and validating responses.
  Use when user asks to test, validate, or audit API endpoints.
---

# API Testing Skill

Instructions for testing APIs...

## Available Scripts

- `scripts/test-endpoint.sh` - Test a single endpoint
- `scripts/validate-schema.js` - Validate response against schema
```

### Custom Instructions (.instructions.md)

Path-specific instruction files with **YAML frontmatter**:

```markdown
---
applyTo: "**/*.tsx,**/*.jsx"
excludeAgent: code-review
---

# React Component Instructions

When working with React components:

1. Use functional components with hooks
2. Follow the established naming conventions
3. Include PropTypes or TypeScript interfaces
```

#### Instructions Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `applyTo` | string | Glob pattern(s) for matching files (comma-separated) |
| `excludeAgent` | string | Agent to exclude these instructions from |

### Repository-Wide Instructions (copilot-instructions.md)

Plain Markdown file at `.github/copilot-instructions.md`:

```markdown
# Project Instructions for Copilot

This is a TypeScript monorepo using pnpm workspaces.

## Coding Standards

- Use TypeScript strict mode
- Follow ESLint configuration
- Write unit tests for all new functions

## Project Structure

- `packages/core` - Core library
- `packages/cli` - CLI application
- `apps/web` - Web application
```

---

## 3. Available Models & Model Specification

### Available Models

> **Note**: For the complete and current list of supported models, visit:  
> https://docs.github.com/en/copilot/reference/ai-models/supported-models#supported-ai-models-in-copilot

Models vary by subscription, plan, and region. Supported models include:

**Anthropic:**
| Model | Notes |
|-------|-------|
| `claude-opus-4.5` | Latest Opus |
| `claude-opus-4.1` | Closing down: 2026-02-17 |
| `claude-sonnet-4.5` | Latest Sonnet |
| `claude-sonnet-4` | Default for Coding Agent |
| `claude-haiku-4.5` | Latest Haiku |

**OpenAI:**
| Model | Notes |
|-------|-------|
| `gpt-5.2` | Latest GPT-5 |
| `gpt-5.2-codex` | Codex variant |
| `gpt-5.1` | GPT-5.1 |
| `gpt-5.1-codex` | Codex variant |
| `gpt-5.1-codex-max` | High-capacity Codex |
| `gpt-5.1-codex-mini` | Lightweight Codex (public preview) |
| `gpt-5` | Closing down: 2026-02-17 |
| `gpt-5-codex` | Closing down: 2026-02-17 |
| `gpt-5-mini` | Lightweight model |
| `gpt-4.1` | GPT-4.1 |

**Google:**
| Model | Notes |
|-------|-------|
| `gemini-3-pro` | Latest Gemini Pro (public preview) |
| `gemini-3-flash` | Latest Gemini Flash (public preview) |
| `gemini-2.5-pro` | Gemini 2.5 Pro |

**xAI:**
| Model | Notes |
|-------|-------|
| `grok-code-fast-1` | Complimentary access (extension ongoing) |

**Fine-tuned:**
| Model | Notes |
|-------|-------|
| `raptor-mini` | Fine-tuned GPT-5 mini (public preview) |

### Model Specification Syntax

#### In Agent Profile Frontmatter

```yaml
---
name: my-agent
description: My custom agent
model: claude-sonnet-4.5
---
```

#### In CLI Interactive Mode

```bash
# Switch model via slash command
/model claude-sonnet-4.5
```

**Note**: The `model:` property works in IDEs (VS Code, JetBrains, etc.) but may be ignored on GitHub.com.

---

## 4. Triggering Agents & Slash Commands

### Triggering Custom Agents

#### In IDE (VS Code, JetBrains)

1. Open Copilot Chat
2. Use the agent dropdown/selector
3. Choose your custom agent by name

#### Via Slash Command (CLI)

```bash
# Select an agent
/agent code-reviewer

# Or reference in prompt
Use the code-reviewer agent to review this PR
```

#### Via CLI Flag

```bash
copilot --agent=code-reviewer --prompt "Review the changes in src/"
```

### Built-in Slash Commands

| Command | Description |
|---------|-------------|
| `/agent` | Select a custom agent |
| `/agent <name>` | Use specific agent |
| `/model` | Change AI model |
| `/mcp add` | Add MCP server |
| `/delegate` | Delegate to coding agent |

---

## 5. Triggering Subagents from Agent Files

### Using Handoffs

Define agents that can delegate to other agents:

```yaml
---
name: project-manager
description: Coordinates development tasks
handoffs:
  - code-reviewer
  - test-writer
  - documentation-writer
---

# Project Manager Agent

You coordinate development tasks. When appropriate, delegate to:
- **code-reviewer** for code review tasks
- **test-writer** for test creation
- **documentation-writer** for docs updates
```

### From Prompts/Instructions

Reference agents by name in your instructions:

```markdown
When the code review is complete, hand off to the test-writer agent
to create unit tests for the reviewed code.
```

---

## 6. Available Tools & Tool Syntax

### Built-in Tools

| Tool | Aliases | Description |
|------|---------|-------------|
| `read` | | Read file contents |
| `edit` | | Edit/modify files |
| `search` | | Search codebase |
| `execute` | `shell` | Run shell commands |
| `web` | | Web browsing/search |

### Tool Specification in Agent Frontmatter

```yaml
---
name: full-access-agent
description: Agent with all tools
tools:
  - read
  - edit
  - search
  - execute
---
```

```yaml
---
name: read-only-agent
description: Agent with limited tools
tools:
  - read
  - search
---
```

### MCP Server Tools

Reference MCP server tools with qualified names:

```yaml
---
name: database-agent
description: Agent with database access
tools:
  - read
  - search
  - my-mcp-server/query-db
  - my-mcp-server/list-tables
  - another-server/*  # Wildcard for all tools
mcp-servers:
  my-mcp-server:
    url: "http://localhost:3000"
---
```

---

## 7. Non-Interactive CLI Syntax

### Basic CLI Invocation

```bash
# Basic prompt
copilot --prompt "Explain this code"
copilot -p "Explain this code"

# With specific agent
copilot --agent=code-reviewer --prompt "Review src/main.ts"

# Resume session
copilot --resume
```

### CLI Arguments

| Flag | Short | Description |
|------|-------|-------------|
| `--prompt` | `-p` | Prompt text |
| `--agent` | | Specify custom agent by name |
| `--resume` | | Resume previous session |
| `--allow-tool` | | Allow specific tool (e.g., `'shell(git)'`) |
| `--allow-all-tools` | | Allow all tools without prompting |
| `--deny-tool` | | Deny specific tool |

### Tool Permission Flags

```bash
# Allow specific shell commands
copilot -p "Run the tests" --allow-tool 'shell(npm test)'

# Allow all tools
copilot -p "Fix the build" --allow-all-tools

# Deny specific tools
copilot -p "Review code" --deny-tool edit
```

### Full Example

```bash
copilot \
  --agent=code-reviewer \
  --prompt "Review all TypeScript files in src/ for security issues" \
  --allow-tool 'read' \
  --allow-tool 'search'
```

---

## 8. MCP Server Integration

Connect to external tools and data sources through MCP servers.  See `bootstrap/mcp_setup.md` for instructions on how to install and configure various MCP Servers in each environment.

### Managing MCP Tools

Use the `--allow-tool` and `--deny-tool` flags to control MCP server tool access:

```bash
copilot --allow-tool 'My-MCP-Server' # Allow all tools from an MCP server
copilot --allow-tool 'My-MCP-Server(tool_name)' # Allow specific tool from an MCP server
copilot --deny-tool 'My-MCP-Server(tool_name)' # Deny specific tool from an MCP server
```

---

## 9. Additional Features

### Custom Instructions Hierarchy

Instructions are loaded in order of specificity:
1. Repository-wide: `.github/copilot-instructions.md`
2. Path-specific: `.github/instructions/*.instructions.md`
3. Agent-specific: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`

### Copilot Memory

- Stores context per repository
- Remembers decisions and patterns
- Available in public preview

### Hooks

Run custom scripts at lifecycle points:
- Before/after tool execution
- Validation and scanning
- Custom preprocessing

#### Hook Events

| Event | Timing | Use Cases |
|-------|--------|-----------|
| `sessionStart` | When a session begins | Initialize environment, load context |
| `sessionEnd` | When a session ends | Cleanup, save state, capture learnings |
| `userPromptSubmitted` | When user submits a prompt | Preprocess input, inject context |
| `preToolUse` | Before a tool executes | Validate inputs, block dangerous operations |
| `postToolUse` | After a tool completes | Post-processing, lint fixes |
| `errorOccurred` | When an error happens | Error handling, recovery logic |

#### Hook Configuration

Hooks are stored as JSON files in `.github/hooks/*.json` within the repository. Each file must include a `version` field set to `1`.

See: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-hooks

```json
// .github/hooks/my-hooks.json
{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "type": "command",
        "bash": "npm run lint:fix",
        "cwd": "."
      }
    ],
    "sessionEnd": [
      {
        "type": "command",
        "bash": "./scripts/capture-learnings.sh",
        "cwd": "scripts"
      }
    ],
    "preToolUse": [
      {
        "type": "command",
        "bash": "./scripts/security-check.sh",
        "cwd": "scripts",
        "timeoutSec": 15
      }
    ]
  }
}
```

#### Hook Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Must be `"command"` |
| `bash` | Yes (Unix) | Shell command or script path to execute |
| `powershell` | Yes (Windows) | PowerShell command or script path |
| `cwd` | No | Working directory relative to repo root |
| `env` | No | Additional environment variables (`{"KEY": "value"}`) |
| `timeoutSec` | No | Max execution time in seconds (default: 30) |

#### Blocking Actions

Hooks receive JSON input via stdin with context about the action. `preToolUse` hooks can approve or deny operations:

**Exit codes / Response:**
- Exit 0 to allow the operation
- Exit 2 to block — the agent will see the hook's stdout as the reason

#### Performance Notes

- Hooks run synchronously and block agent execution
- Keep execution under 5 seconds when possible
- Use async logging (append to files) over synchronous I/O
- Set appropriate `timeoutSec` to prevent hangs

### Permissions System

- Path permissions for file access
- URL permissions for web access
- Current directory must be trusted

### IDE Integration

Supported in:
- VS Code
- Visual Studio
- JetBrains IDEs
- Eclipse
- Xcode
- Neovim

---

## 10. Quick Reference

### Command Cheatsheet

```bash
# Interactive mode
copilot

# Non-interactive with agent
copilot --agent=my-agent -p "Your prompt"

# Allow tools
copilot -p "Fix bug" --allow-all-tools

# Resume session
copilot --resume

# Slash commands (in interactive mode)
/agent code-reviewer
/model claude-sonnet-4.5
/mcp add server-name
/delegate Create a PR for these changes
```

### File Locations Summary

| Purpose | Location |
|---------|----------|
| User agents | `~/.copilot/agents/` |
| Repo agents | `.github/agents/` |
| Org agents | `.github-private/agents/` |
| User skills | `~/.copilot/skills/` |
| Repo skills | `.github/skills/` |
| Repo instructions | `.github/copilot-instructions.md` |
| Path instructions | `.github/instructions/*.instructions.md` |
| Agent instructions | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` |
| MCP config (user) | `~/.copilot/mcp-config.json` |
| MCP config (project) | `.copilot/mcp-config.json` |
| Hooks | `.github/hooks/*.json` |

### Agent Frontmatter Template

```yaml
---
name: agent-name
description: |
  Clear description of what this agent does
  and when it should be used.
model: claude-sonnet-4
tools:
  - read
  - edit
  - search
target: vscode
infer: true
handoffs:
  - other-agent
---

# Agent Name

Your agent instructions here...
```
