# Claude Code AI Development Environment

Research findings from https://code.claude.com/docs

---

## 1. Custom Subagents, Slash Commands, and Skills

Claude Code supports all three customization mechanisms:

### Directory Structure

```
~/.claude/                     # User-level (all projects)
├── agents/                    # Custom subagents
├── skills/                    # Custom skills
├── commands/                  # Custom slash commands
└── output-styles/             # Custom output styles

.claude/                       # Project-level (team-shared)
├── agents/
├── skills/
├── commands/
├── settings.json              # Project settings
└── settings.local.json        # Local overrides (gitignored)

my-plugin/                     # Plugin structure
├── .claude-plugin/
│   └── plugin.json            # Required manifest
├── agents/
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── commands/
│   └── hello.md
├── hooks/
│   └── hooks.json
├── .mcp.json                  # MCP servers
└── .lsp.json                  # LSP servers
```

### Priority Order
1. `--agents` CLI flag (highest)
2. `.claude/agents/` (project)
3. `~/.claude/agents/` (user)
4. Plugin's `agents/` directory (lowest)

---

## 2. Frontmatter Syntax

### Subagent Frontmatter (`.claude/agents/name.md`)

```yaml
---
name: code-reviewer           # Required: lowercase, hyphens
description: Reviews code     # Required: when to use this agent
tools: Read, Glob, Grep       # Optional: allowed tools (comma-separated)
disallowedTools: Write, Edit  # Optional: denied tools
model: sonnet                 # Optional: sonnet|opus|haiku|inherit (default: sonnet)
permissionMode: default       # Optional: default|acceptEdits|dontAsk|bypassPermissions|plan
skills: [skill-name]          # Optional: skills to load
hooks:                        # Optional: lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
---

System prompt content goes here...
```

### Skill Frontmatter (`.claude/skills/name/SKILL.md`)

```yaml
---
name: my-skill                          # Required: lowercase, hyphens, max 64 chars
description: What this skill does       # Required: max 1024 chars
allowed-tools: Read, Grep, Glob         # Optional: restrict tools
model: claude-sonnet-4-20250514         # Optional: override model
context: fork                           # Optional: run in isolated context
agent: general-purpose                  # Optional: agent for forked context
user-invocable: true                    # Optional: show in slash menu (default: true)
hooks:                                  # Optional: lifecycle hooks
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
---

Skill instructions here...
```

### Slash Command Frontmatter (`.claude/commands/name.md`)

```yaml
---
description: Brief description of command  # Required
---

Command instructions here...
Use $ARGUMENTS for all arguments.
Use $1, $2 for positional parameters.
```

### Output Style Frontmatter (`~/.claude/output-styles/name.md`)

```yaml
---
name: My Custom Style                    # Optional: inherits from filename
description: What this style does        # Optional: shown in /output-style UI
keep-coding-instructions: false          # Optional: keep default coding prompt (default: false)
---

Custom style instructions...
```

---

## 3. Available Models

### Model Aliases (Recommended)
```yaml
model: sonnet      # Latest Sonnet (default for subagents)
model: opus        # Latest Opus (most capable)
model: haiku       # Latest Haiku (fast, cheap)
model: inherit     # Use parent conversation's model
```

### Full Model IDs
```yaml
model: claude-sonnet-4-20250514
model: claude-sonnet-4-5-20250929
model: claude-opus-4-5-20251101
```

### CLI Model Specification
```bash
claude -p --model sonnet "query"
claude -p --model opus "query"
claude -p --model claude-sonnet-4-5-20250929 "query"
```

### Settings Configuration
```json
{
  "model": "claude-sonnet-4-5-20250929"
}
```

---

## 4. Triggering Subagents from Agent Files

### Automatic Delegation
Claude automatically delegates based on task and subagent `description` field.

### In System Prompt / Instructions
```
Use the code-reviewer agent to analyze this code.
Have the test-runner subagent fix failing tests.
Continue that code review and analyze the authorization logic.
```

### Skills Field (Load Skills into Subagent)
```yaml
---
name: code-reviewer
description: Review code for quality
skills: pr-review, security-check   # These skills are loaded into this agent
---
```

---

## 5. Triggering Agents from Slash Commands

### In Command Content
```markdown
---
description: Review code changes
---

Use the code-reviewer agent to review the changes described below:
$ARGUMENTS
```

### Reference Skills
Skills are model-invoked automatically when their description matches the request.
Include trigger keywords in skill descriptions.

### Explicit Agent Request
```markdown
---
description: Run full test suite
---

Have the test-runner subagent run all tests and fix any failures found in $ARGUMENTS.
```

---

## 6. Available Tools

### Tool List

| Tool | Description | Permission |
|------|-------------|------------|
| `Read` | Read file contents | No |
| `Write` | Create/overwrite files | Yes |
| `Edit` | Make targeted edits | Yes |
| `Glob` | Find files by pattern | No |
| `Grep` | Search patterns in files | No |
| `Bash` | Execute shell commands | Yes |
| `WebFetch` | Fetch content from URLs | Yes |
| `WebSearch` | Perform web searches | Yes |
| `Task` | Run subagents | No |
| `Skill` | Execute slash commands | Yes |
| `AskUserQuestion` | Ask multiple-choice questions | No |
| `NotebookEdit` | Modify Jupyter notebooks | Yes |

### Syntax in Frontmatter

**Allowlist:**
```yaml
tools: Read, Grep, Glob, Bash
```

**YAML List Format:**
```yaml
allowed-tools:
  - Read
  - Grep
  - Glob
```

**Denylist:**
```yaml
disallowedTools: Write, Edit
```

### Permission Rules (settings.json)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Bash(git commit:*)"
    ],
    "ask": [
      "Bash(git push:*)"
    ],
    "deny": [
      "Bash(curl:*)",
      "Read(./.env)",
      "WebFetch"
    ]
  }
}
```

### Pattern Matching

| Pattern | Effect |
|---------|--------|
| `Tool` | Match all uses |
| `Tool(exact)` | Exact match |
| `Tool(prefix:*)` | Prefix matching |
| `Tool(*wildcard*)` | Glob matching |

---

## 7. Non-Interactive CLI

### Basic Syntax
```bash
claude -p "query"
claude --print "query"
```

### Model Specification
```bash
claude -p --model sonnet "query"
claude -p --model opus "query"
claude -p --model claude-sonnet-4-5-20250929 "query"
```

### Agent Specification
```bash
claude -p --agent my-custom-agent "query"
```

### Inline Agent Definition (JSON)
```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### System Prompt Customization
```bash
# Replace system prompt
claude -p --system-prompt "You are a Python expert" "query"
claude -p --system-prompt-file ./prompt.txt "query"

# Append to default prompt
claude -p --append-system-prompt "Always use TypeScript" "query"
claude -p --append-system-prompt-file ./extra.txt "query"
```

### Output Formatting
```bash
claude -p --output-format text "query"      # Default
claude -p --output-format json "query"
claude -p --output-format stream-json "query"
```

### Tool Control
```bash
claude -p --tools "Bash,Edit,Read" "query"
claude -p --tools "" "query"                 # Disable all
claude -p --tools "default" "query"          # Enable all
claude -p --allowedTools "Bash,Read,Edit" "query"  # Auto-approve
```

### Permission Modes
```bash
claude -p --permission-mode plan "query"
claude -p --dangerously-skip-permissions "query"
```

### Processing Options
```bash
claude -p --max-turns 3 "query"
claude -p --max-budget-usd 5.00 "query"
claude -p --json-schema '{"type":"object",...}' "query"
claude -p --no-session-persistence "query"
claude -p --fallback-model sonnet "query"
```

### Session Management
```bash
claude --continue                           # Continue most recent
claude --resume <session_id>                # Resume specific session
```

### Input Handling
```bash
cat file.txt | claude -p "explain this"
claude -p --input-format stream-json "query"
```

### Full Example
```bash
claude -p \
  --model opus \
  --append-system-prompt "Focus on security" \
  --allowedTools "Read,Grep,Glob" \
  --output-format json \
  --max-turns 5 \
  "Review this codebase for vulnerabilities" | jq '.result'
```

---

## 8. Additional Features

### Extended Thinking
- **Default**: Enabled, up to 31,999 tokens for reasoning
- **Toggle**: `Option+T` (macOS) / `Alt+T` (Windows/Linux)
- **View**: `Ctrl+O` (verbose mode)
- **Configure**: `MAX_THINKING_TOKENS` environment variable

```json
{
  "alwaysThinkingEnabled": true
}
```

### Plan Mode (Read-Only Analysis)
```bash
claude --permission-mode plan
```
- Toggle in session: `Shift+Tab`

### MCP (Model Context Protocol)

Connect to external tools and data sources through MCP servers.  See `bootstrap/mcp_setup.md` for instructions on how to install and configure various MCP Servers in each environment.

**Managing MCP Servers:**
```bash
claude mcp list
claude mcp get github
claude mcp remove github
```

### LSP Servers (`.lsp.json`)
```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

### Hooks

Hooks allow custom scripts to run at lifecycle points. They can observe, modify, or block agent actions.

#### Hook Events

| Event | Timing | Use Cases |
|-------|--------|-----------|
| `SessionStart` | When a session begins | Initialize environment, load context |
| `SessionEnd` | When a session ends | Cleanup, save state, capture learnings |
| `PreToolUse` | Before a tool executes | Validate inputs, block dangerous operations |
| `PostToolUse` | After a tool completes | Lint fixes, log changes, trigger side effects |
| `PermissionRequest` | When permission is requested | Custom approval logic |
| `UserPromptSubmit` | When user submits a prompt | Preprocess input, inject context |
| `Notification` | On agent notifications | Custom alerting |
| `Stop` | When agent stops | Capture session state |
| `SubagentStop` | When a subagent stops | Aggregate subagent results |
| `PreCompact` | Before context compaction | Preserve important context |

#### Hook Configuration

**In `~/.claude/settings.json` or `.claude/settings.json`:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "npm run lint:fix $FILE" }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "./scripts/capture-learnings.sh" }
        ]
      }
    ]
  }
}
```

**In agent/skill frontmatter:**
```yaml
---
name: my-agent
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "./scripts/post-edit.sh $FILE"
---
```

#### Blocking Actions

Hooks can block operations by returning a non-zero exit code or outputting specific JSON:

```bash
#!/bin/bash
# Example: Block writes to sensitive files
if [[ "$FILE" == *".env"* ]]; then
  echo '{"permissionDecision": "deny", "reason": "Cannot modify .env files"}'
  exit 2
fi
```

**Exit codes:**
- `0`: Allow (continue execution)
- `2`: Deny (block the action)
- Other: Allow but log warning

#### Environment Variables in Hooks

| Variable | Description |
|----------|-------------|
| `$FILE` | File path (for file operations) |
| `$TOOL_INPUT` | Tool input as JSON |
| `$CLAUDE_SESSION_ID` | Current session ID |
| `$TOOL_NAME` | Name of the tool being used |

### Output Styles
- **Built-in**: `Default`, `Explanatory`, `Learning`
- **Switch**: `/output-style [style]`
- **Custom**: Create in `~/.claude/output-styles/` or `.claude/output-styles/`

### Built-in Subagents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| `Explore` | Haiku | Read-only | Fast codebase exploration |
| `Plan` | Inherited | Read-only | Research during plan mode |
| `general-purpose` | Inherited | All | Complex multi-step tasks |
| `Bash` | Inherited | Bash | Terminal commands |

### String Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed to skill/command |
| `$1`, `$2`, etc. | Positional parameters |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `$FILE` | File path (in hooks) |
| `$TOOL_INPUT` | Tool input JSON (in hooks) |

### Image Support
- Drag-drop, paste (`Ctrl+V`), or file path
- Use for screenshots, UI mockups, diagrams

### File References
- Single file: `@src/utils/auth.js`
- Directory: `@src/components`
- MCP resources: `@github:repos/owner/repo/issues`

### Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Standard permission prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny prompts (allowed tools work) |
| `bypassPermissions` | Skip all checks |
| `plan` | Read-only exploration |

### Configuration Files

| File | Scope |
|------|-------|
| `~/.claude/settings.json` | User (all projects) |
| `.claude/settings.json` | Project (team-shared) |
| `.claude/settings.local.json` | Local project (gitignored) |
| `~/.claude.json` | Preferences, OAuth, MCP servers |
| `CLAUDE.md` / `.claude/CLAUDE.md` | Memory/instructions |

### Environment Variables
```bash
ANTHROPIC_API_KEY              # API authentication
ANTHROPIC_MODEL                # Override default model
MAX_THINKING_TOKENS            # Limit thinking budget
DISABLE_TELEMETRY=1            # Opt out of analytics
DISABLE_AUTOUPDATER=1          # Disable auto-updates
BASH_DEFAULT_TIMEOUT_MS        # Bash timeout
HTTP_PROXY / HTTPS_PROXY       # Proxy configuration
```

---

## Quick Reference

### Create a Subagent
```bash
mkdir -p .claude/agents
cat > .claude/agents/reviewer.md << 'EOF'
---
name: reviewer
description: Reviews code for quality and security
tools: Read, Grep, Glob
model: sonnet
---

You are a code reviewer. Analyze code for quality, security, and best practices.
EOF
```

### Create a Skill
```bash
mkdir -p .claude/skills/commit-helper
cat > .claude/skills/commit-helper/SKILL.md << 'EOF'
---
name: commit-helper
description: Generates commit messages from staged changes
allowed-tools: Bash, Read
---

# Commit Helper

1. Run `git diff --staged` to see changes
2. Generate a commit message with summary and description
EOF
```

### Create a Slash Command
```bash
mkdir -p .claude/commands
cat > .claude/commands/review.md << 'EOF'
---
description: Review code in specified files
---

Review the following files for quality and security issues:
$ARGUMENTS
EOF
```
