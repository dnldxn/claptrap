# Gemini CLI

**Documentation**: [geminicli.com/docs](https://geminicli.com/docs/)

## Overview

Gemini CLI is Google's agentic coding CLI. It supports custom commands, experimental skills, and context files via `GEMINI.md`.

---

## Directory Structure

```
~/.gemini/
├── commands/                    # User-level custom commands
│   └── *.toml
├── skills/                      # User-level skills
│   └── <skill-name>/
│       └── SKILL.md
├── settings.json                # Global settings
└── GEMINI.md                    # Global context/memory file

<project-root>/
├── .gemini/
│   ├── commands/                # Project-level custom commands
│   │   └── *.toml
│   ├── skills/                  # Project-level skills
│   │   └── <skill-name>/
│   │       └── SKILL.md
│   └── settings.json            # Project settings
└── GEMINI.md                    # Project context/memory file
```

## Supported Features

| Feature | Supported | Description |
|---------|-----------|-------------|
| **Custom Slash Commands** | Yes | Reusable prompt templates defined in `.toml` files |
| **Agent Skills** | Experimental | Self-contained directories with `SKILL.md` and optional scripts/assets |
| **Subagents** | Workaround | Not built-in; simulate via `run_shell_command` launching Gemini CLI non-interactively |

---

## Custom Commands

Custom commands use **TOML v1** format.

**Locations**:
- **User-level**: `~/.gemini/commands/`
- **Project-level**: `<project-root>/.gemini/commands/`
- Project commands override user commands with the same name
- Subdirectories create namespaced commands (e.g., `commands/git/commit.toml` → `/git:commit`)

**File Format**:

```toml
# Required field
prompt = """
Your prompt text here.
Can be multiline.
"""

# Optional field
description = "Brief description shown in /help"
```

**Special Placeholders**:

| Placeholder | Description |
|-------------|-------------|
| `{{args}}` | Inject user arguments (raw outside shell blocks, escaped inside) |
| `!{command}` | Execute shell command and embed output |
| `@{path/to/file}` | Embed file content or directory listing |

**Example**:

```toml
# ~/.gemini/commands/git/commit.toml
description = "Generate a Git commit message based on staged changes"
prompt = """
Please generate a Conventional Commit message based on the following git diff:

```diff
!{git diff --staged}
```

Focus on being concise and following conventional commit format.
"""
```

**Triggering Commands**:

```bash
/test                    # Basic command
/git:commit              # Namespaced command
/git:commit --amend      # With arguments
```

## Skills

Skills use **YAML frontmatter** in Markdown.

**Locations**:
- **User-level**: `~/.gemini/skills/`
- **Project-level**: `.gemini/skills/`

**Directory Structure**:

```
<skill-name>/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Optional: executable scripts
├── references/        # Optional: docs, schemas, examples
└── assets/            # Optional: templates, binaries
```

**SKILL.md Format**:

```markdown
---
name: my-skill-name
description: |
  What this skill does and when Gemini should activate it.
  Be specific about trigger conditions.
---

# Skill Instructions

Your detailed instructions for the agent when this skill is active.

## Procedures

1. Step one
2. Step two

## Resources

Reference files in `scripts/`, `references/`, or `assets/` subdirectories.
```

**Required Frontmatter Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier (lowercase, alphanumeric, dashes only) |
| `description` | string | What the skill does and when to use it |

**Triggering Skills**:

Skills are **automatically activated** when:
1. User request matches the skill's `description`
2. Gemini determines the skill is relevant via `activate_skill` tool
3. User confirms activation (unless auto-approved)

**Manual Skill Management**:

```bash
/skills                      # List all skills
/skills enable <skill-name>  # Enable skill
/skills disable <skill-name> # Disable skill
```

## Context Files (GEMINI.md)

Plain Markdown files (no frontmatter) loaded hierarchically:
- `~/.gemini/GEMINI.md` (global)
- Project root and parent directories
- Subdirectories under current working directory

Can include other files via `@other-file.md` syntax.

---

## Available Models

| Model | Description |
|-------|-------------|
| `gemini-2.5-pro` | Gemini 2.5 Pro |
| `gemini-2.5-flash` | Gemini 2.5 Flash |
| `gemini-2.5-flash-lite` | Gemini 2.5 Flash Lite |
| `gemini-3-pro-preview` | Gemini 3 Pro (preview, requires preview features enabled) |
| `gemini-3-flash-preview` | Gemini 3 Flash (preview, requires preview features enabled) |

**Specifying Model**:

```bash
gemini --model gemini-2.5-flash    # CLI flag
gemini -m gemini-2.5-pro           # Short form
/model                             # Interactive selection
```

Custom commands and skills inherit the session's active model. To use a specific model in a command, spawn a subagent with `-m` flag via shell injection.

## Available Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `read_many_files` | Read multiple files at once |
| `list_directory` | List directory contents |
| `glob` | Find files matching patterns |
| `search_file_content` | Search for content in files |
| `replace` | Replace content in files |
| `run_shell_command` | Execute shell commands |
| `web_fetch` | Fetch content from URLs |
| `google_web_search` | Search the web |
| `save_memory` | Save information to memory |
| `write_todos` | Create/manage todo items |
| `activate_skill` | Activate an agent skill |

**Tool Syntax in Custom Commands**:

```toml
# Shell command injection
prompt = """
Here's the current git status:
!{git status}
"""

# File content injection
prompt = """
Review this file:
@{src/main.ts}
"""

# Directory listing injection
prompt = """
Here are the files in src/:
@{src/}
"""
```

**Specifying Allowed Tools**:

```bash
gemini -p "prompt" --allowed-tools read_file,write_file,run_shell_command
```

---

## CLI Syntax

**Interactive Mode**:

```bash
gemini                   # Launch interactive mode
/model                   # Change model mid-session
```

**Non-Interactive Mode**:

```bash
gemini --prompt "Your prompt here"    # Using --prompt flag
gemini -p "Your prompt here"          # Short form
echo "Your prompt here" | gemini      # Piping input
cat prompt.txt | gemini               # From file
```

**CLI Arguments**:

| Flag | Short | Description |
|------|-------|-------------|
| `--prompt` | `-p` | Prompt text for non-interactive mode |
| `--model` | `-m` | Specify model (e.g., `gemini-2.5-flash`) |
| `--allowed-tools` | | Comma-separated list of allowed tools |
| `--output-format` | | Output format: `text`, `json`, `stream-json` |
| `--sandbox` | | Run in sandbox mode |
| `--include-directories` | | Include additional directories in context |

**Full Example**:

```bash
gemini \
  --prompt "Summarize the main functionality of this codebase" \
  --model gemini-2.5-pro \
  --output-format json \
  --allowed-tools read_file,list_directory,search_file_content
```

## Spawning Subagents

Gemini CLI does not have built-in subagent support. Use shell injection to spawn subagents:

```toml
description = "Delegate a focused task to a subagent"
prompt = """
I need you to perform a specific subtask. Here's the result from a focused analysis:

!{gemini -p "Analyze only the security aspects of this code: @{src/auth.ts}" -m gemini-2.5-flash --allowed-tools read_file}

Based on this analysis, provide recommendations.
"""
```

---

## Configuration

**Location**: `~/.gemini/settings.json` or `<project>/.gemini/settings.json`

```json
{
  "model": {
    "name": "gemini-2.5-flash"
  },
  "features": {
    "skills": true,
    "preview": true
  },
  "tools": {
    "allowedTools": ["read_file", "write_file"]
  }
}
```

**Context Override**:

```bash
export GEMINI_SYSTEM_MD=".gemini/custom-system.md"
gemini -p "Your prompt"
```

## Session Management

```bash
/chat save my-session     # Save current session
/chat list                # List saved sessions
/chat resume my-session   # Resume a session
```

## Checkpointing

Automatic snapshots before file modifications:

```bash
/restore                  # Restore to previous checkpoint
```

## Memory Commands

```bash
/memory show              # Show current memory
/memory refresh           # Refresh memory
/memory add               # Add to memory
```

## Security Features

- **Sandbox mode**: Isolate tool execution
- **Trusted folders**: Configure which directories allow tool access
- **`.geminiignore`**: Exclude files from context and tool access

## MCP Server Support

Integration with Model Context Protocol servers for extended capabilities.

---

## Quick Reference

### Command Cheatsheet

```bash
# Interactive mode
gemini

# Non-interactive with specific model
gemini -p "prompt" -m gemini-2.5-flash

# With allowed tools
gemini -p "prompt" --allowed-tools read_file,write_file

# JSON output
gemini -p "prompt" --output-format json

# Custom commands (in interactive mode)
/git:commit
/test --verbose

# Skills management
/skills
/skills enable my-skill

# Model selection
/model

# Memory/context
/memory show
```

### File Locations Summary

| Purpose | Location |
|---------|----------|
| User commands | `~/.gemini/commands/` |
| Project commands | `.gemini/commands/` |
| User skills | `~/.gemini/skills/` |
| Project skills | `.gemini/skills/` |
| Global context | `~/.gemini/GEMINI.md` |
| Project context | `GEMINI.md` |
| Settings | `~/.gemini/settings.json` or `.gemini/settings.json` |
