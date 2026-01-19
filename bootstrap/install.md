Install the OpenSpec workflow into this project by executing the steps below.

# Rules
- Speak in a concise tone. Comment as you work.
- Do not use shell commands to communicate—write responses as plain text.
- Before beginning, print a concise numbered list of the steps and your planned actions.
- Do **NOT** use symlinks for any files or directories.


# Step 1 - Install or Upgrade OpenSpec

```bash
npm install -g @fission-ai/openspec@latest
```

Then check if the `openspec/` directory exists in the destination project:
- **If `openspec/` does NOT exist:** run `openspec init` to initialize OpenSpec.
- **If `openspec/` already exists:** run `openspec update` to refresh the OpenSpec configuration.

Run only ONE of these commands, not both. Print the result.

# Step 2 - Initialize .workflow directory

Copy the code conventions, agents, commands, skills, memory/design features into this project:

```bash
mkdir -p .workflow/memory/{anti-patterns,decisions,lessons,patterns} .workflow/designs/

# Copy the code conventions, agents, commands, skills into the project
cp -rf "$CLAPTRAP_PATH"/src/{code-conventions,agents,commands,skills} ".workflow/"
rm -f .workflow/{commands,skills,agents}/{AGENTS,README}.md  # Remove any AGENTS.md and README.md from the .workflow directories as these can confuse the AI harness

# Initialize the memory/design features
cp -f "$CLAPTRAP_PATH"/src/memory/TEMPLATE.md ".workflow/memory/"
cp -n "$CLAPTRAP_PATH"/src/memory/project.md.template ".workflow/memory/project.md"
cp -f "$CLAPTRAP_PATH"/src/designs/TEMPLATE.md ".workflow/designs/"
cp -rf "$CLAPTRAP_PATH"/src/designs/example-feature ".workflow/designs/"
```

Note: `-f` overwrites templates from claptrap, `-n` preserves user-created `project.md`.

If `.workflow/memory/project.md` was newly created (did not exist before), then read the file, analyze the target project, and fill in the document with relevant details. If the file already exists, then skip this step.

# Step 2.5 - Customize Models for Provider

Agent and command files support provider-specific model mappings via a `models:` block in their YAML frontmatter. This step rewrites the `model:` field to match the target provider.

**Frontmatter format:**
```yaml
---
name: Example Agent
description: "..."
model: claude-sonnet-4.5           # default/fallback model
models:                            # provider-specific overrides (optional)
  cursor: anthropic/claude-sonnet-4.5
  github-copilot: claude-sonnet-4.5
  claude: sonnet
  opencode: anthropic/claude-sonnet-4-5
  gemini: gemini-2.5-pro
  codex: gpt-5.1-codex
---
```

**Processing rules:**
1. For each `.md` file in `.workflow/agents/` and `.workflow/commands/`:
2. Parse the YAML frontmatter (between `---` delimiters)
3. If `models:` block exists and contains a key matching `$PROVIDER` (case-insensitive, spaces→hyphens):
   - Replace the `model:` value with the provider-specific value
   - Remove the entire `models:` block from the frontmatter
4. If no matching provider key exists, keep the default `model:` value and remove the `models:` block
5. Write the modified file back

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
model: sonnet
---
```

Process all files in `.workflow/agents/` and `.workflow/commands/` directories. Print a summary showing each file and its resolved model.

# Step 3 - Setup `.gitignore`

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

# Step 4 - Setup Environments (AI Adapter)

Get the user's environment from the `$PROVIDER` environment variable and the destination directory from the `$PROVIDER_DIR` environment variable (e.g. `Cursor` and `.cursor`). Print both to the console before proceeding.

Run the following commands, applying provider-specific exceptions listed below:

```bash
mkdir -p "${PROVIDER_DIR}"
ln -sfn ../.workflow/{agents,commands,skills} "${PROVIDER_DIR}/"
```

Note: This overwrites files from claptrap (allowing upgrades) but preserves any user-created files in these directories.

## Exceptions

### OpenCode

- Destination directories are singular: `.opencode/command/`, `.opencode/skill/`, `.opencode/agent/`
```bash
ln -sfn ../.workflow/agents   .opencode/agent
ln -sfn ../.workflow/commands .opencode/command
ln -sfn ../.workflow/skills   .opencode/skill
```

### Github Copilot

- Agent files: rename `<ROLE>.md` → `<ROLE>.agent.md`
- Command files: rename `<COMMAND>.md` → `<COMMAND>.prompt.md` and put in `.github/prompts/` (not `.github/commands/`)
- Skill files: no changes

# Step 5 - Update AGENTS.md with the Project Guidelines

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

# Step 6 - Install MCP Servers and Tools

## ripgrep

Ensure ripgrep is installed (https://github.com/BurntSushi/ripgrep#installation) and on the PATH.

## Serena MCP

Check if Serena MCP is installed and configured for the current environment. If not installed, print the following prompt for the user to copy into another window:

```
Install and configure Serena MCP for my environment.

Environment: [PROVIDER from Step 5]
OS: [detect and insert OS]

Instructions: https://oraios.github.io/serena/02-usage/030_clients.html

Notes:
- If uvx is not found, use the full path (e.g. ~/.local/bin/uvx)
```

# Step 7 - Verify

Review the instructions above and verify all steps were executed correctly. If any steps were not executed correctly, redo them. Explain mistakes and corrections.

Common mistakes:
- Skill directories are missing (e.g. `.github/skills/spawn-subagent/` directory is missing)
- `.workflow/code-conventions/` directory is missing or incomplete
- Files inside the provider's `.agents/` or `.commands/` directories (e.g. `.github/agents/developer.md`) are symlink-ed instead of copied
