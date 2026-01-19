# Antigravity (Google)

> Documentation for Google Antigravity IDE customization, syntax, models, tools, and features.
> Source: https://antigravity.google/docs
> 
> **Note**: Antigravity is a new "agent-first" AI IDE announced November 18, 2025. Some features are in preview/experimental stages. Official documentation is limited; many details are community-reported.

---

## 1. Custom Subagents, Slash Commands, Skills

### Supported Features

| Feature | Supported | Description |
|---------|-----------|-------------|
| **Skills** | ✅ Yes | Self-contained directories with `SKILL.md` following Claude Code standard |
| **Workflows** | ✅ Yes | Saved prompt sequences triggered via slash commands |
| **Rules** | ✅ Yes | Global or workspace-level behavior instructions |
| **Slash Commands** | ✅ Yes | Trigger workflows via `/` commands |
| **Subagents** | ⚠️ Limited | Agent Manager for multiple agents; no built-in nested agent spawning |

### Directory Structure

```
~/.gemini/
├── GEMINI.md                        # Global user rules/instructions
└── antigravity/
    ├── skills/                      # Global user skills
    │   └── <skill-name>/
    │       └── SKILL.md
    └── brain/                       # Artifacts storage (internal)
        └── <PROJECT_ID>/
            ├── Tasks.md
            ├── ImplementationPlan.md
            └── Walkthrough.md

<workspace-root>/
├── GEMINI.md                        # Workspace-level rules (or AGENTS.md)
├── .agent/
│   ├── skills/                      # Workspace skills
│   │   └── <skill-name>/
│   │       ├── SKILL.md             # Required: skill definition
│   │       ├── scripts/             # Optional: executable scripts
│   │       ├── references/          # Optional: docs, schemas
│   │       └── assets/              # Optional: templates, resources
│   ├── workflows/                   # Workspace workflows
│   │   └── <workflow-name>/
│   └── rules/                       # Workspace rules
│       └── *.md
└── specs/                           # Specification files (optional)
    └── *.md
```

### Skills Location

| Scope | Location |
|-------|----------|
| Workspace | `<workspace-root>/.agent/skills/<skill-name>/` |
| Global/User | `~/.gemini/antigravity/skills/<skill-name>/` |

### Workflows Location

| Scope | Location |
|-------|----------|
| Workspace | `<workspace-root>/.agent/workflows/<workflow-name>/` |

### Rules Location

| Scope | Location |
|-------|----------|
| Global | `~/.gemini/GEMINI.md` |
| Workspace | `<workspace-root>/GEMINI.md` or `<workspace-root>/.agent/rules/*.md` |
| Alternative | `AGENTS.md`, `CLAUDE.md` in workspace root |

---

## 2. Frontmatter & File Syntax

### Skills (SKILL.md)

Skills use **YAML frontmatter** in Markdown (following Claude Code standard):

```markdown
---
name: api-testing
description: |
  Specialized in testing REST APIs and validating responses.
  Use when user asks to test, validate, or audit API endpoints.
---

# API Testing Skill

Instructions for the agent when this skill is activated.

## Scope

Define what this skill covers and doesn't cover.

## Procedures

1. Step one
2. Step two
3. Step three

## Resources

Reference files in `scripts/`, `references/`, or `assets/` subdirectories.
```

#### Required Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier (lowercase, alphanumeric, dashes). Defaults to folder name if omitted |
| `description` | string | **Required** — What the skill does and when to use it. Used for semantic matching |

#### Skill Directory Structure

```
<skill-name>/
├── SKILL.md           # Required: frontmatter + instructions
├── scripts/           # Optional: executable scripts, tools
├── references/        # Optional: docs, schemas, examples, templates
└── assets/            # Optional: images, binaries, resources
```

### Workflows

Workflows are defined similarly to skills, stored in `.agent/workflows/`:

```markdown
---
name: feature-spec
description: |
  Interview user to create a detailed feature specification.
---

# Feature Specification Workflow

Guide the user through defining:

1. **Problem Statement**: What problem does this solve?
2. **User Stories**: Who are the users?
3. **Requirements**: Functional and non-functional
4. **Acceptance Criteria**: How do we know it's done?

Output a structured spec document.
```

### Rules (GEMINI.md / AGENTS.md)

Rules are **plain Markdown files** without required frontmatter:

```markdown
# Project Rules

This is a TypeScript monorepo using pnpm.

## Coding Standards

- Use strict TypeScript
- Follow ESLint configuration
- Write tests for all new functions

## Architecture

- Follow clean architecture patterns
- Keep components small and focused
- Use dependency injection

## Constraints

- Never modify files in `vendor/`
- Always run tests before committing
```

### How Rules Are Injected

Rules from `GEMINI.md` are injected into the system prompt with special tags:

```xml
<user_rules>
The following are user-defined rules that you MUST ALWAYS FOLLOW WITHOUT ANY EXCEPTION.
<MEMORY[user_global]>
- Global user rules from ~/.gemini/GEMINI.md
</MEMORY[user_global]>
<MEMORY[GEMINI.md]>
- Workspace rules from project GEMINI.md
</MEMORY[GEMINI.md]>
</user_rules>
```

---

## 3. Available Models & Model Specification

### Available Models

| Model | Description |
|-------|-------------|
| `gemini-3-pro` | Gemini 3 Pro (primary/default) |
| `gemini-3-flash` | Gemini 3 Flash (faster, lighter) |
| `claude-sonnet-4.5` | Claude Sonnet 4.5 (Anthropic) |
| `gpt-oss` | Open-source GPT models |

### Model Specification

#### Via UI

Model selection is done through the Antigravity interface:
- Settings menu
- Agent configuration panel
- Per-conversation selection

#### In Skills/Workflows

**Not documented** — Skills and workflows don't have a documented field for specifying which model to use. Model selection appears to be session/UI-based.

### Agent Modes

| Mode | Description |
|------|-------------|
| **Planning Mode** | Agent creates detailed plan and task list before implementation |
| **Fast Mode** | Agent jumps directly to implementation |

Switch modes via the agent side panel or settings.

---

## 4. Triggering Skills, Workflows & Slash Commands

### Triggering Workflows

```bash
# Slash command syntax
/workflow-name

# With file reference
/spec @specs/my-feature.md

# Examples
/feature-spec
/code-review @src/main.ts
```

### Triggering Skills

Skills are triggered in two ways:

1. **Automatic/Semantic**: Agent matches user prompt to skill `description` and activates automatically
2. **Explicit**: Ask the agent directly: "Use the api-testing skill to test this endpoint"

```
# Ask agent to use a skill
Use the api-testing skill to validate the /users endpoint

# Or reference explicitly
@skill:api-testing test the authentication flow
```

### Managing Skills

```bash
# List available skills (via chat)
What skills do you have available?

# Enable a specific skill
Use skill <skill-name> for this task
```

**Note**: Automatic skill matching is reported to be inconsistent. Explicitly requesting skills often works better.

---

## 5. Triggering Subagents from Skills

### Agent Manager

Antigravity includes an **Agent Manager** view ("Mission Control") for coordinating multiple agents:

- Run multiple agents in parallel
- Monitor agent progress
- Coordinate handoffs between agents

### Subagent Limitations

**Not officially supported** — Antigravity doesn't have built-in syntax for spawning subagents from within skills or workflows. Community workarounds include:

- Using external CLIs (like Gemini CLI) via terminal
- Scripting multiple agent sessions externally
- Using Agent Manager for manual coordination

---

## 6. Available Tools & Surfaces

### Built-in Surfaces

Agents can operate across three integrated surfaces:

| Surface | Capabilities |
|---------|--------------|
| **Editor** | Read/write files, code navigation, inline completions |
| **Terminal** | Execute shell commands, run scripts, manage processes |
| **Browser** | Navigate web pages, take screenshots, record interactions |

### Artifacts

Agents generate verifiable artifacts:

| Artifact Type | Description |
|---------------|-------------|
| Task Lists | Structured todo items (`Tasks.md`) |
| Implementation Plans | Detailed plans (`ImplementationPlan.md`) |
| Walkthroughs | Step-by-step guides (`Walkthrough.md`) |
| Screenshots | Browser/UI captures |
| Browser Recordings | Recorded browser sessions for testing |
| Code Diffs | Changes made by the agent |

### Artifact Storage

Artifacts are stored in:
```
~/.gemini/antigravity/brain/<PROJECT_ID>/
├── Tasks.md
├── ImplementationPlan.md
├── Walkthrough.md
└── assets/
    └── screenshots/
```

### Knowledge Base

Antigravity includes a knowledge base ("Knowledge Items") that:
- Extracts information from interactions
- Persists context across sessions
- Informs future agent responses

**Note**: Knowledge Items feature is reported to be inconsistent — may require manual prompting to use stored knowledge.

### Tool Specification in Skills

Tools are not explicitly specified in skill frontmatter. Skills can reference scripts in their directory:

```markdown
## Procedures

1. Run the audit script: `scripts/audit.js`
2. Validate response against schema in `references/api-schema.json`
```

---

## 7. Non-Interactive CLI Syntax

### CLI Support

**Not documented** — Antigravity is primarily a GUI application. There is no publicly documented CLI or headless mode for:
- Running agents non-interactively
- Scripting agent tasks
- CI/CD integration

### Workarounds

Users report using workarounds for automation:
- Invoking Gemini CLI from Antigravity's terminal
- External scripting with API calls
- Using the terminal surface for command execution

### Desktop Application

Antigravity is available as a desktop application for:
- Windows
- macOS
- Linux

---

## 8. Additional Features

### Import from Other Editors

Import settings, extensions, and keybindings from:
- VS Code
- Cursor

### Autonomy & Permissions

Configure agent autonomy levels:
- File modification permissions
- Terminal command execution
- Browser interaction scope

### Rules via UI

Access via: **Customizations → Rules** in the top-right menu

- Add global rules
- Add workspace-specific rules
- Toggle rule activation

### Workflows via UI

Access via: **Customizations → Workflows**

- Create saved prompt sequences
- Define workflow parameters
- Trigger via slash commands

### Views

| View | Description |
|------|-------------|
| **Editor View** | Code editing, completions, inline commands |
| **Manager View** | "Mission Control" for multiple agents |

### Rate Limits

- Free preview with generous limits
- Paid users: quotas reset every ~5 hours
- Free users: weekly quotas

---

## Quick Reference

### Command Cheatsheet

```bash
# In Antigravity chat

# Trigger a workflow
/workflow-name
/spec @specs/feature.md

# Reference files
@filename.ts
@src/components/

# Ask to use a skill
Use the <skill-name> skill to...

# Switch modes (via UI or ask)
Switch to planning mode
Use fast mode for this task
```

### File Locations Summary

| Purpose | Location |
|---------|----------|
| Global rules | `~/.gemini/GEMINI.md` |
| Workspace rules | `GEMINI.md`, `AGENTS.md`, or `.agent/rules/` |
| Global skills | `~/.gemini/antigravity/skills/` |
| Workspace skills | `.agent/skills/` |
| Workflows | `.agent/workflows/` |
| Artifacts/Brain | `~/.gemini/antigravity/brain/<PROJECT_ID>/` |

### Skill Template (SKILL.md)

```markdown
---
name: skill-name
description: |
  Clear description of what this skill does
  and when it should be activated.
---

# Skill Name

## Purpose

What this skill accomplishes.

## Scope

What's in and out of scope.

## Procedures

1. First step
2. Second step
3. Third step

## Resources

- `scripts/helper.sh` - Helper script
- `references/schema.json` - API schema
```

---

## Comparison Notes

### vs. Gemini CLI
- Antigravity: GUI-focused IDE with integrated surfaces
- Gemini CLI: Full command-line interface
- Skills: Both use similar `SKILL.md` format with YAML frontmatter

### vs. GitHub Copilot
- Antigravity: Skills in `.agent/skills/`
- Copilot: Agents in `.github/agents/`
- Both support rules via `GEMINI.md` / `AGENTS.md`

### vs. Cursor
- Antigravity: Skills + Workflows + Rules
- Cursor: Commands + Rules (MDC format)
- Antigravity has Agent Manager for multi-agent coordination

### Limitations

- No documented CLI/headless mode
- No explicit model specification in skills
- Skills/Workflows may not activate automatically (require explicit requests)
- Knowledge Items feature inconsistent
- Limited documentation (product in preview)

---

## References

- [The Verge: Google Antigravity Announcement](https://www.theverge.com/news/822833/google-antigravity-ide-coding-agent-gemini-3-pro)
- [Google Codelabs: Getting Started with Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity)
- [Medium: Tutorial - Getting Started with Antigravity Skills](https://medium.com/google-cloud/tutorial-getting-started-with-antigravity-skills-864041811e0d)
