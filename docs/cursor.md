# Cursor

> Documentation for Cursor IDE customization, syntax, models, tools, and CLI usage.
> Source: https://docs.cursor.com

---

## 1. Custom Subagents, Slash Commands, Skills

### Supported Features

| Feature | Supported | Description |
|---------|-----------|-------------|
| **Custom Slash Commands** | ✅ Yes | Reusable prompt templates in `.md` files |
| **Rules** | ✅ Yes | Persistent instructions in `.mdc` files with metadata |
| **Agent Modes** | ✅ Yes | Built-in modes (Agent, Ask, Custom) |
| **Skills** | ⚠️ Beta | Experimental; workaround via rules with `alwaysApply: false` |
| **Background Agents** | ✅ Yes | Asynchronous agents that run in remote environments |
| **Subagents** | ✅ Yes | Custom agents in `.cursor/agents/` and `~/.cursor/agents/` |

### Directory Structure

```
<project-root>/
├── .cursor/
│   ├── agents/                  # Custom agents (subagents)
│   │   └── *.md
│   ├── commands/                # Custom slash commands
│   │   └── *.md
│   └── rules/                   # Project rules
│       └── *.mdc
├── AGENTS.md                    # Simple project-wide instructions
└── environment.json             # Background agent environment config

# User-level (varies by OS)
~/.cursor/
├── agents/                      # Global custom agents
│   └── *.md
├── commands/                    # Global custom commands
│   └── *.md
└── rules/                       # Global user rules
```

### Custom Commands Location

| Scope | Location |
|-------|----------|
| Project | `.cursor/commands/` |
| User/Global | `~/.cursor/commands/` (or via settings) |

### Agents Location

| Scope | Location |
|-------|----------|
| Project | `.cursor/agents/` |
| User/Global | `~/.cursor/agents/` |

### Rules Location

| Scope | Location |
|-------|----------|
| Project | `.cursor/rules/` |
| User | Global settings (plain text) |

---

## 2. Frontmatter & File Syntax

### Custom Slash Commands (.md)

Custom commands are **plain Markdown files** with optional title/description:

```markdown
# Code Review

Review the selected code for:

1. **Security vulnerabilities** - Check for injection, XSS, etc.
2. **Performance issues** - Identify bottlenecks
3. **Best practices** - Suggest improvements

Provide a structured response with severity levels.
```

The filename becomes the command name:
- `.cursor/commands/review-code.md` → `/review-code`
- `.cursor/commands/create-pr.md` → `/create-pr`

**Note**: Unlike other environments, Cursor commands don't have documented YAML frontmatter for metadata like model or tools.

### Rules (.mdc)

Rules use **MDC format** with metadata frontmatter:

```markdown
---
description: TypeScript coding standards for this project
globs:
  - "**/*.ts"
  - "**/*.tsx"
alwaysApply: false
type: Auto Attached
---

# TypeScript Standards

When working with TypeScript files:

1. Use strict mode
2. Prefer interfaces over type aliases for object shapes
3. Use const assertions where appropriate
4. Always include return types on functions

## Naming Conventions

- Components: PascalCase
- Functions: camelCase
- Constants: SCREAMING_SNAKE_CASE
```

#### Rules Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Brief description of the rule |
| `globs` | array | File patterns this rule applies to |
| `alwaysApply` | boolean | Always include in context |
| `type` | string | Rule type (see below) |

#### Rule Types

| Type | Description |
|------|-------------|
| `Always` | Always applied to all contexts |
| `Auto Attached` | Applied when matching files are in context |
| `Agent Requested` | Agent can request activation |
| `Manual` | User must explicitly include via `@ruleName` |

### AGENTS.md

Simple project-wide instructions without frontmatter:

```markdown
# Project Instructions

This is a Next.js 14 application using the App Router.

## Key Conventions

- Use server components by default
- Client components should be in `components/client/`
- API routes are in `app/api/`

## Testing

- Run `npm test` before committing
- Maintain >80% coverage
```

### environment.json (Background Agents)

Configuration for background agent environments:

```json
{
  "build": {
    "install": "npm ci",
    "command": "npm run build"
  },
  "test": {
    "command": "npm test"
  },
  "env": {
    "NODE_ENV": "development"
  }
}
```

---

## 3. Available Models & Model Specification

### Available Models

Cursor supports multiple frontier models (varies by subscription):

| Model | Description |
|-------|-------------|
| `gpt-4o` | GPT-4o |
| `gpt-4-turbo` | GPT-4 Turbo |
| `claude-3.5-sonnet` | Claude 3.5 Sonnet |
| `claude-3-opus` | Claude 3 Opus |
| `gemini-2.5-pro` | Gemini 2.5 Pro |
| `cursor-small` | Cursor's fast model (unlimited) |

### Model Specification

#### Via UI

Model selection is done through:
1. Settings → Models
2. Model dropdown in chat/agent interface
3. Per-conversation model selection

#### In Rules/Commands

**Not supported** — Model cannot be specified in `.mdc` rules or `.md` command files. Model selection is session/UI-based.

#### Via API Keys

Custom model providers can be added in Settings → Models → API Keys.

---

## 4. Triggering Slash Commands

### In Agent/Chat Input

```
# Type / to open command menu
/review-code

# Command with context
/create-pr @current-file
```

### Referencing Rules

```
# Include a rule explicitly
@my-rule-name

# Reference files
@filename.ts

# Reference folders
@src/components/
```

### Built-in Slash Commands

| Command | Description |
|---------|-------------|
| `/summarize` | Summarize the conversation |
| `/edit` | Enter edit mode |
| `/chat` | Switch to chat mode |

---

## 5. Triggering Subagents from Commands

Cursor supports custom agents (subagents) defined in `.cursor/agents/` or `~/.cursor/agents/`.

Commands execute in the **current agent context**. To use a subagent:
1. Select the desired agent in the agent picker
2. Run the command as usual

If a command needs a specific agent, mention it explicitly in the command text and switch to that agent before running.

---

## 6. Available Tools & Tool Syntax

### Built-in Tools by Mode

| Mode | Tools Available |
|------|-----------------|
| **Agent** | All tools enabled |
| **Ask** | Read-only tools (no edits) |
| **Custom** | User-selected tools |

### Tool Categories

#### Search Tools
| Tool | Description |
|------|-------------|
| Search | Semantic search across codebase |
| Search Files | Find files by name |
| Codebase | Index-based codebase search |
| Grep | Text/regex search |
| Read File | Read file contents |
| List Directory | List directory contents |

#### Edit Tools
| Tool | Description |
|------|-------------|
| Edit & Reapply | Edit files with automatic reapplication |
| Delete File | Remove files |

#### Run Tools
| Tool | Description |
|------|-------------|
| Terminal | Execute shell commands |
| Web | Fetch web content |

### MCP Resources

Cursor supports MCP (Model Context Protocol) for external tools:

```json
// In settings or configuration
{
  "mcp": {
    "servers": {
      "my-server": {
        "url": "http://localhost:3000",
        "env": {
          "API_KEY": "${MCP_API_KEY}"
        }
      }
    }
  }
}
```

Environment variable interpolation is supported (`${VAR_NAME}`).

### Tool Specification in Rules/Commands

**Not documented** — Unlike other environments, Cursor doesn't have explicit syntax for specifying allowed tools in command or rule files. Tool availability is controlled by:
- Mode selection (Agent/Ask/Custom)
- Custom mode configuration in settings

---

## 7. Non-Interactive CLI Syntax

### Cursor Agent CLI

Cursor has a CLI component (`cursor-agent`), but documentation is limited.

**Note**: Custom slash commands may **not work** in CLI mode (as of recent reports).

### Known CLI Flags

| Flag | Description |
|------|-------------|
| `-p`, `--prompt` | Prompt text |
| `--print` | Output result to stdout |
| `--resume` | Resume previous session |
| `--output-format` | Output format (`json`, `text`) |

### Example (Limited)

```bash
# Basic usage (may vary)
cursor-agent --prompt "Explain this codebase"
cursor-agent -p "Fix the bug in main.ts" --print
```

### Background Agents (Recommended for Automation)

For automated/non-interactive workflows, use **Background Agents**:

1. Triggered via UI (Ctrl+E or agent pane)
2. Run in isolated cloud environment
3. Can clone repos, make commits, push branches
4. Configured via `environment.json`

---

## 8. Hooks

Cursor provides a comprehensive hooks system for running custom scripts at various lifecycle points.

### Hook Events

| Event | Timing | Use Cases |
|-------|--------|-----------|
| `sessionStart` | When a session begins | Initialize environment, load context |
| `sessionEnd` | When a session ends | Cleanup, save state, capture learnings |
| `preToolUse` | Before any tool executes | Validate inputs, block operations |
| `postToolUse` | After a tool completes | Post-processing, lint fixes |
| `postToolUseFailure` | After a tool fails | Error handling, recovery |
| `subagentStart` | When a subagent starts | Track subagent activity |
| `subagentStop` | When a subagent completes | Aggregate results |
| `beforeShellExecution` | Before shell command runs | Validate commands |
| `afterShellExecution` | After shell command completes | Process output |
| `beforeMCPExecution` | Before MCP tool runs | Validate MCP calls |
| `afterMCPExecution` | After MCP tool completes | Process MCP results |
| `beforeReadFile` | Before reading a file | Access control |
| `afterFileEdit` | After file is modified | Trigger builds, lint |
| `beforeSubmitPrompt` | Before prompt is submitted | Preprocess input |
| `preCompact` | Before context compaction | Preserve important context |
| `stop` | When agent stops | Capture final state |
| `afterAgentResponse` | After agent responds | Post-process response |
| `afterAgentThought` | After agent thinking | Log reasoning |

#### Tab-Specific Hooks

| Event | Timing | Use Cases |
|-------|--------|-----------|
| `beforeTabFileRead` | Before Tab reads a file | Tab-specific access control |
| `afterTabFileEdit` | After Tab edits a file | Tab-specific post-processing |

### Hook Configuration

Hooks are configured in `.cursor/hooks.json` or Cursor settings:

```json
{
  "hooks": {
    "postToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "npm run lint:fix ${FILE}"
      }
    ],
    "sessionEnd": [
      {
        "matcher": "*",
        "command": "./scripts/capture-session.sh"
      }
    ],
    "beforeShellExecution": [
      {
        "matcher": "*",
        "command": "./scripts/validate-command.sh"
      }
    ]
  }
}
```

### Blocking Actions

Hooks can block operations via exit code 2 or permission denial:

```bash
#!/bin/bash
# Example: Block writes to production config
if [[ "$FILE" == *"production"* ]]; then
  echo '{"permission": "deny", "reason": "Cannot modify production files"}'
  exit 2
fi
```

**Exit codes:**
- `0`: Allow (continue execution)
- `2`: Deny (block the action)
- Other: Allow but log warning

### Environment Variables in Hooks

| Variable | Description |
|----------|-------------|
| `${FILE}` | File path being operated on |
| `${TOOL_NAME}` | Name of the tool being used |
| `${TOOL_INPUT}` | Tool input as JSON |
| `${SESSION_ID}` | Current session identifier |

---

## 9. Additional Features

### Agent Modes

| Mode | Description | Tools |
|------|-------------|-------|
| **Agent** | Full capabilities | All tools |
| **Ask** | Read-only Q&A | Search, Read only |
| **Custom** | User-configured | Selected tools |

### Background Agents

Remote agents that run asynchronously:
- Clone GitHub repositories
- Run in isolated environments
- Create branches and commits
- Push changes automatically
- Support for `environment.json` configuration

### Checkpoints

Automatic snapshots of codebase state:
- Created before modifications
- Can restore previous states
- Accessible via agent UI

### Chat Features

| Feature | Description |
|---------|-------------|
| Multiple tabs | Maintain separate conversations |
| History | Browse past conversations |
| Export | Export chat history |
| Summarization | Auto-summarize long contexts |

### Codebase Indexing

- Automatic semantic indexing
- Fast codebase search
- Symbol-aware navigation

### LSP Integration

Full Language Server Protocol support:
- Go-to definition
- Find references
- Hover information
- Diagnostics/linting

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Open chat |
| `Ctrl+K` | Inline edit |
| `Ctrl+E` | Open agent/background agent |
| `Cmd+.` | Quick actions |

---

## Quick Reference

### Command Cheatsheet

```bash
# In Cursor chat/agent input

# Trigger custom command
/review-code

# Include rules
@my-rule

# Reference files
@src/main.ts

# Reference folders
@src/components/

# Built-in commands
/summarize

# Model selection (via UI)
# Use dropdown or settings
```

### File Locations Summary

| Purpose | Location |
|---------|----------|
| Project agents | `.cursor/agents/` |
| User agents | `~/.cursor/agents/` |
| Project commands | `.cursor/commands/` |
| User commands | `~/.cursor/commands/` |
| Project rules | `.cursor/rules/` |
| Project instructions | `AGENTS.md` |
| Background agent config | `environment.json` |

### Rule Template (.mdc)

```markdown
---
description: Brief description of this rule
globs:
  - "**/*.ts"
  - "**/*.tsx"
alwaysApply: false
type: Auto Attached
---

# Rule Title

Your instructions here...

## Section 1

Details...

## Section 2

More details...
```

### Command Template (.md)

```markdown
# Command Name

Clear instructions for what this command should do.

## Steps

1. First step
2. Second step
3. Third step

## Expected Output

Description of expected response format.
```

---

## Comparison Notes

### vs. Gemini CLI
- Cursor: GUI-focused, limited CLI
- Gemini CLI: Full CLI with extensive flags
- Model specification: UI-only in Cursor, CLI flags in Gemini

### vs. GitHub Copilot
- Cursor: Commands in `.md`, Rules in `.mdc`
- Copilot: Agents in `.agent.md` with YAML frontmatter
- Tools: Copilot has explicit tool specification, Cursor uses modes

### Limitations
- No agent frontmatter for model/tools specification
- Limited CLI support for automation
- No subagent spawning mechanism
- Skills feature still in beta
