Install the OpenSpec workflow into this project by executing the steps below.

# Rules
- Be concise. Comment as you work.
- Do not use shell commands to communicate—write responses as plain text.
- Before beginning, print a numbered list of steps and planned actions.
- Do **NOT** use symlinks for any files or directories.

# Step 1 - Install or Upgrade OpenSpec

```bash
npm install -g @fission-ai/openspec@latest
openspec init --help                        # Check if OpenSpec is installed and list available providers
openspec init --tools <PROVIDER_NAME>       # Install OpenSpec for a new provider (pick one)
openspec update                             # OR upgrade existing OpenSpec
```

# Step 2 - Initialize .workflow Directory

```bash
mkdir -p .workflow/{code-conventions,designs}

cp -rf "$CLAPTRAP_PATH"/src/code-conventions/* .workflow/code-conventions/
cp -f "$CLAPTRAP_PATH"/src/designs/TEMPLATE.md .workflow/designs/
cp -rf "$CLAPTRAP_PATH"/src/designs/example-feature .workflow/designs/

# Create memories.md if it doesn't exist
if [ ! -f .workflow/memories.md ]; then
  cat > .workflow/memories.md << 'EOF'
# Memories

Project memories captured during development. Agents should read this file for context and add new memories when significant decisions, patterns, or lessons emerge.

---
EOF
fi
```

# Step 3 - Copy Agents, Commands, Skills to Provider Directory

Read `$PROVIDER` and `$PROVIDER_DIR` environment variables. Print both before proceeding.

## Default provider commands (see exceptions in the sections below)

```bash
mkdir -p "${PROVIDER_DIR}"/{agents,commands,skills}
cp -rf "$CLAPTRAP_PATH"/src/agents/* "${PROVIDER_DIR}/agents/"
cp -rf "$CLAPTRAP_PATH"/src/commands/* "${PROVIDER_DIR}/commands/"
cp -rf "$CLAPTRAP_PATH"/src/skills/* "${PROVIDER_DIR}/skills/"

# Remove any AGENTS.md or README.md files from the provider directories as these can confuse the AI harness
rm -f "${PROVIDER_DIR}"/{agents,commands,skills}/{AGENTS,README}.md
```

## OpenCode

OpenCode uses singular directory names for agents, commands, and skills.  Adjust the default provider commands above to use `.opencode/{agent,command,skill}` instead of `{PROVIDER_DIR}/{agents,prompts,skills}`.

## Github Copilot

Rename files and directories as follows:

- **Agent files**: rename `<ROLE>.md` → `<ROLE>.agent.md` (e.g. `developer.md` → `developer.agent.md`)
- **Command files**: rename `<COMMAND>.md` → `<COMMAND>.prompt.md` and put in `.github/prompts/` (not `.github/commands/`)
- **Skill files**: no changes

# Step 4 - Customize Models

Rewrite `model:` in each agent or command Markdown file's frontmatter based on the `models:` block, then remove the `models:` block.

**Directions:**
1. Parse YAML frontmatter in each `.md` file in the provider's agents/commands directories
2. If `models:` contains a key matching `$PROVIDER` (lowercase, spaces→hyphens): replace `model:` with that value
3. Otherwise keep default `model:` value
4. Remove `models:` block entirely
5. Print summary of each file and its resolved model

**Provider key mapping:**
| $PROVIDER       | Frontmatter key   |
|-----------------|-------------------|
| Cursor          | cursor            |
| Github Copilot  | github-copilot    |
| OpenCode        | opencode          |
| Claude          | claude            |
| Codex           | codex             |
| Gemini          | gemini            |

**Example transformation** (for `$PROVIDER=Claude`):

Before:
```yaml
---
name: Code Reviewer
... other frontmatter fields ...
model: github-copilot/claude-sonnet-4.5
models:
  cursor: anthropic/claude-sonnet-4.5
  claude: sonnet
  gemini: gemini-2.5-pro
---
```

After:
```yaml
---
name: Code Reviewer
... other frontmatter fields ...
model: sonnet
---
```

# Step 5 - Setup .gitignore

Open or create `.gitignore` and add the following lines if not already present:
```
.claude/
.codex/
.cursor/
.gemini/
.github/
.opencode/
.workflow/
.serena/
```

# Step 6 - Update AGENTS.md

Update the project's root `AGENTS.md` with the contents in the **AGENTS.md Contents** section below.

- Do NOT modify text between `<!-- OPENSPEC:START -->` and `<!-- OPENSPEC:END -->` markers (auto-generated).
- Add or replace the content below/after the OpenSpec section. Apply exactly as written.
- Do not modify any other existing content in the `AGENTS.md` file.  Only insert and/or replace the content between the `<!-- CLAPTRAP:START -->` and `<!-- CLAPTRAP:END -->` markers.

**AGENTS.md Contents**
```md
<!-- CLAPTRAP:START -->

# Core Principles
- **Simple over Clever**: Always favor the simplest solution that meets requirements. Avoid over-engineering.
- **Minimal Complexity**: Reduce moving parts, dependencies, and abstractions to the essential minimum.
- **Code Quality**: Write maintainable, self-documenting code; follow DRY principles for significant duplications (don't obsess over minor repetition)
- **Minimal Error Handling**: Handle only external failures; trust internal code
- **Conciseness**: Make the minimum necessary changes to achieve the goal.
- **Confident**: Make clear recommendations rather than presenting multiple options
- **Trust your own code**: Save error handling for external boundaries

# Project Rules
- If anything is unclear, ask the user for clarification until satisfied. Do not proceed until you have a clear understanding of the requirements.
- Instructions that are directly provided should supersede any other instructions loaded later.

# Project Code Conventions / Style Guides
You are **strictly required** to read and adhere to the project code conventions in the `.workflow/code-conventions/` directory.

- For Python code, the conventions are in `.workflow/code-conventions/python.md`.
- For Snowflake SQL code (including SQL in Python files), the conventions are in `.workflow/code-conventions/snowflake.md`.

<!-- CLAPTRAP:END -->
```

# Step 7 - Install MCP Servers and Tools

**ripgrep (rg)**: Ensure installed and on PATH (https://github.com/BurntSushi/ripgrep#installation)

**Serena MCP**: Check if configured (e.g. `claude mcp list`). If not, print this prompt for the user:

```
Install and configure Serena MCP for my environment.
Environment: $PROVIDER
OS: [detect]
Instructions: https://oraios.github.io/serena/02-usage/030_clients.html
Note: If uvx not found, use full path (e.g. ~/.local/bin/uvx)
```

# Step 8 - Verify

Confirm all steps completed correctly. Common issues:
- Missing skill directories (e.g. `.github/skills/spawn-subagent/`)
- Missing/incomplete `.workflow/code-conventions/`
- Files symlinked instead of copied
- AGENTS.md or README.md still in provider directories
