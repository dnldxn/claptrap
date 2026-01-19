# OpenAI Codex CLI Research

**Repository**: [openai/codex](https://github.com/openai/codex)  
**Status**: Active development (Rust)  
**Documentation**: [developers.openai.com/codex](https://developers.openai.com/codex)  
**Authentication**: OAuth via ChatGPT Plus/Pro subscription or API key

---

## 1. Custom Agents, Slash Commands/Prompts, and Skills

### Agents (AGENTS.md)

Codex supports project-specific instructions via **`AGENTS.md`** files placed in your repository. These are not "subagents" but persistent context for the main Codex agent.

**Location**: Project root or subdirectories (e.g., `./AGENTS.md`, `./src/AGENTS.md`)

**Usage**:
- Generate a scaffold with the `/init` slash command
- Plain markdown with instructions, conventions, and guidance
- Codex automatically reads `AGENTS.md` when working in that directory

### Slash Commands

**Built-in Slash Commands**:
| Command | Purpose |
|---------|---------|
| `/model` | Switch models mid-session |
| `/approvals` | Change approval mode (Auto/Read-only/Full Access) |
| `/status` | View token usage and configuration |
| `/compact` | Summarize long conversations to free tokens |
| `/diff` | Show Git differences |
| `/mention` | Add a file to conversation context |
| `/new` | Start a fresh conversation |
| `/resume` | Resume a saved conversation |
| `/fork` | Branch a saved conversation |
| `/init` | Generate AGENTS.md scaffold |
| `/review` | Run code review on diff |
| `/mcp` | List MCP tools |
| `/feedback` | Submit feedback |
| `/logout` | Sign out |
| `/quit`, `/exit` | Exit the CLI |

### Custom Prompts (Slash Command Extensions)

Custom prompts behave like reusable slash commands.

**Directory**: `~/.codex/prompts/`

**File Format**: Markdown files with YAML frontmatter

```yaml
---
description: Short description shown in popup
argument-hint: KEY=<value>
---
Your prompt instructions here with $1, $2, $ARGUMENTS or $NAMED_PLACEHOLDER
```

**Frontmatter Options**:
| Key | Purpose |
|-----|---------|
| `description:` | Displayed under command name in popup |
| `argument-hint:` | Documents expected parameters |

**Placeholder Syntax**:
| Placeholder | Meaning |
|-------------|---------|
| `$1` through `$9` | Positional arguments |
| `$ARGUMENTS` | All arguments combined |
| `$NAMED` | Named placeholders (e.g., `$FILE`, `$TICKET_ID`) |
| `$$` | Literal dollar sign |

**Invocation Syntax**:
```bash
/prompts:<name>
/prompts:<name> ARG1="value" ARG2="another value"
```

**Example** (`~/.codex/prompts/draftpr.md`):
```yaml
---
description: Draft a pull request description
argument-hint: FILES=<files> PR_TITLE=<title>
---
Create a pull request for $FILES with title "$PR_TITLE".
Summarize changes and explain the motivation.
```

Invoke with: `/prompts:draftpr FILES="src/lib/api.ts" PR_TITLE="Add API retry logic"`

### Skills

Skills extend Codex with reusable capabilities via a `SKILL.md` file.

**Directory Structure**:
```
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
└── assets/           # Optional: templates, resources
```

**Skill Locations** (in precedence order):
| Scope | Path |
|-------|------|
| Repo (highest) | `$CWD/.codex/skills/` |
| Repo (parent) | `$CWD/../.codex/skills/` |
| Repo (root) | `$REPO_ROOT/.codex/skills/` |
| User | `~/.codex/skills/` |
| Admin | `/etc/codex/skills/` |

**SKILL.md Frontmatter**:
```yaml
---
name: skill-name
description: Description that helps Codex select the skill
metadata:
  short-description: Optional user-facing description
---
Skill instructions for the Codex agent to follow when using this skill.
```

**Required Fields**:
| Field | Purpose |
|-------|---------|
| `name` | Skill identifier |
| `description` | Helps Codex match skill to tasks |

**Optional Fields**:
| Field | Purpose |
|-------|---------|
| `metadata.short-description` | User-facing description |

**Invoking Skills**:
- Type `$` to mention a skill
- Use `/skills` slash command
- Codex can invoke implicitly when task matches description

**Enable/Disable Skills** (in `~/.codex/config.toml`):
```toml
[[skills.config]]
path = "/path/to/skill"
enabled = false
```

**Built-in Skills**:
- `$skill-creator` - Create new skills
- `$skill-installer` - Install skills from GitHub

---

## 2. Available Models

### Model Families

| Model ID | Description |
|----------|-------------|
| `gpt-5.2` | Latest general agentic model |
| `gpt-5.1-codex-max` | Long-horizon, agentic coding (high capability) |
| `gpt-5.1-codex` | Recommended for real-world engineering |
| `gpt-5.1-codex-mini` | Smaller, cost-effective coding |
| `gpt-5.1` | General agentic tasks |
| `gpt-5-codex` | Previous generation coding model |
| `gpt-5` | Previous general model |

**Default**: `gpt-5-codex` on macOS/Linux, `gpt-5` on Windows

### Specifying Model in config.toml

```toml
model = "gpt-5.2"
```

### Specifying Model via CLI

```bash
codex -m gpt-5.1-codex-mini
codex --model gpt-5.1-codex
```

### Specifying Model Mid-Session

Use `/model` slash command and select from popup.

### Reasoning Configuration

```toml
model_reasoning_effort = "medium"    # minimal | low | medium | high | xhigh
model_reasoning_summary = "auto"     # auto | concise | detailed | none
model_verbosity = "medium"           # low | medium | high
```

---

## 3. Available Tools

### Built-in Tools

Codex provides built-in tools for file operations, search, execution, and web access:

| Tool | Purpose |
|------|---------|
| `shell` | Run shell commands (sandboxed) |
| `web_search` | Search the web (requires opt-in) |
| `apply_patch` | Apply file patches |

### Web Search Tool

Enable in `~/.codex/config.toml`:
```toml
[features]
web_search_request = true

[sandbox_workspace_write]
network_access = true
```

Or use CLI flag: `codex --search`

### MCP (Model Context Protocol) Tools

MCP tools are prefixed: `mcp__<server-name>__<tool-name>`

**MCP Server Configuration** (in `~/.codex/config.toml`):
```toml
[mcp_servers.myserver]
command = "npx"
args = ["-y", "@example/mcp-server"]
enabled = true
enabled_tools = ["tool1", "tool2"]    # Optional allowlist
disabled_tools = ["tool3"]            # Optional blocklist
startup_timeout_sec = 10
tool_timeout_sec = 60

# For HTTP servers:
[mcp_servers.httpserver]
url = "https://mcp.example.com"
bearer_token_env_var = "MCP_TOKEN"
```

**MCP CLI Commands**:
```bash
codex mcp           # Manage MCP servers
codex mcp-server    # Run Codex as an MCP server
```

---

## 4. CLI Syntax and Arguments

### Interactive Mode

```bash
codex                              # Launch TUI
codex "your prompt"               # Launch with initial prompt
codex -m gpt-5.1-codex "prompt"   # Specify model
codex -i image.png "explain this" # Include image
codex --search "find docs on X"   # Enable web search
codex --full-auto                  # Low-friction automation mode
```

### Non-Interactive Mode (`codex exec`)

```bash
codex exec "your prompt"                      # Run non-interactively
codex e "your prompt"                         # Short alias
codex exec --model gpt-5.1-codex "prompt"    # With specific model
codex exec --full-auto "fix the bugs"        # Full auto mode
codex exec --json "prompt"                   # Output as JSONL
codex exec -o output.txt "prompt"            # Save last message to file
cat prompt.txt | codex exec -                # Read prompt from stdin
```

**`codex exec` Flags**:
| Flag | Values | Purpose |
|------|--------|---------|
| `-m, --model` | string | Override model |
| `--full-auto` | boolean | Low-friction mode |
| `--yolo` | boolean | Bypass approvals and sandbox (DANGEROUS) |
| `-s, --sandbox` | `read-only | workspace-write | danger-full-access` | Sandbox policy |
| `-a, --ask-for-approval` | `untrusted | on-failure | on-request | never` | Approval policy |
| `-i, --image` | path(s) | Attach images |
| `--json` | boolean | Output JSONL events |
| `-o, --output-last-message` | path | Save final message to file |
| `-C, --cd` | path | Set working directory |
| `--skip-git-repo-check` | boolean | Allow running outside Git repo |

### Resume Sessions

```bash
codex resume                           # Interactive picker
codex resume --last                   # Resume most recent
codex resume <SESSION_ID>             # Resume specific session
codex exec resume --last "continue"   # Resume in non-interactive mode
```

### Other Commands

```bash
codex login                           # Authenticate
codex logout                          # Remove credentials
codex completion bash                 # Generate shell completions
codex cloud                           # Browse/execute cloud tasks
codex cloud exec --env ENV_ID "task"  # Submit cloud task
codex apply <TASK_ID>                 # Apply diff from cloud task
codex sandbox                         # Run commands in sandbox
```

### Global Flags

| Flag | Values | Purpose |
|------|--------|---------|
| `-m, --model` | string | Override default model |
| `-p, --profile` | string | Configuration profile |
| `-c, --config` | `key=value` | Override config values |
| `-C, --cd` | path | Set working directory |
| `--add-dir` | path | Grant write access to additional directories |
| `-s, --sandbox` | `read-only | workspace-write | danger-full-access` | Sandbox policy |
| `-a, --ask-for-approval` | `untrusted | on-failure | on-request | never` | Approval policy |
| `--full-auto` | boolean | Shortcut for `-a on-request -s workspace-write` |
| `--search` | boolean | Enable web search |
| `--oss` | boolean | Use local OSS model provider (Ollama/LMStudio) |
| `-i, --image` | path(s) | Attach images to prompt |
| `--enable` | feature | Enable feature flag |
| `--disable` | feature | Disable feature flag |

---

## 5. Configuration

### Configuration File

**Location**: `~/.codex/config.toml`

**Key Settings**:
```toml
# Model
model = "gpt-5.1-codex"
model_reasoning_effort = "medium"
model_reasoning_summary = "auto"
model_verbosity = "medium"

# Approval and Sandbox
approval_policy = "on-failure"    # untrusted | on-failure | on-request | never
sandbox_mode = "workspace-write"  # read-only | workspace-write | danger-full-access

# Features
[features]
web_search_request = true
shell_tool = true

# Sandbox settings
[sandbox_workspace_write]
network_access = true
writable_roots = ["/additional/path"]

# MCP servers
[mcp_servers.example]
command = "npx"
args = ["-y", "@example/server"]
enabled = true

# Skills
[[skills.config]]
path = "/path/to/skill"
enabled = false

# Profiles
[profiles.fast]
model = "gpt-5.1-codex-mini"

[profiles.thorough]
model = "gpt-5.1-codex-max"
```

### Configuration Precedence

CLI flags (`-c key=value`) > Project config > User config (`~/.codex/config.toml`)

### Using Profiles

```bash
codex -p fast "quick task"
codex --profile thorough "complex analysis"
```

---

## 6. Additional Features

### Session History

- Sessions saved in `~/.codex/sessions/`
- Resume with `/resume` or `codex resume`
- Fork sessions with `/fork`

### Code Review

- Use `/review` for in-session code review
- Review against base branch, uncommitted changes, or specific commits

### Image Inputs

```bash
codex -i screenshot.png "explain this error"
codex --image img1.png,img2.png "compare these"
```

### Sandboxing

| Mode | Behavior |
|------|----------|
| `read-only` | Read files only, no writes or commands |
| `workspace-write` | Write within workspace, controlled network |
| `danger-full-access` | Full system access (use with caution) |

### Approval Modes

| Mode | Behavior |
|------|----------|
| `untrusted` | Approve everything |
| `on-failure` | Approve failed commands (default) |
| `on-request` | Approve only when explicitly requested |
| `never` | Never ask for approval |

### Tips and Shortcuts

| Shortcut | Action |
|----------|--------|
| `@` | Fuzzy file search in composer |
| `!command` | Run local shell command |
| `Esc` (2x) | Edit previous message |
| `Ctrl+G` | Open external editor for prompt |
| `Ctrl+C` | Cancel / exit |

---

## 7. Summary: Key Customization Locations

| Customization | Location | Format |
|---------------|----------|--------|
| Config | `~/.codex/config.toml` | TOML |
| Custom Prompts | `~/.codex/prompts/*.md` | Markdown + YAML frontmatter |
| Skills (User) | `~/.codex/skills/<name>/SKILL.md` | Markdown + YAML frontmatter |
| Skills (Project) | `.codex/skills/<name>/SKILL.md` | Markdown + YAML frontmatter |
| Agent Instructions | `AGENTS.md` in project root | Plain Markdown |
| Sessions | `~/.codex/sessions/` | Internal format |

---

## References

- [OpenAI Codex Documentation](https://developers.openai.com/codex)
- [OpenAI Codex Repository](https://github.com/openai/codex)
- [Skills Repository](https://github.com/openai/skills)
- [Agent Skills Specification](https://agentskills.io/specification)
