# Claptrap Installer for OpenCode

Follow every step below carefully in order. Print what you are doing before each action.

## Paths

| Name | Path | Description |
|---|---|---|
| `CLAPTRAP_REPO` | `~/projects/claptrap` | Claptrap git repository |
| `OPENCODE_ROOT` | `~/.config/opencode` | OpenCode user-level config directory |
| `STAGING` | `~/.config/opencode/claptrap` | Where claptrap-managed files are stored |
| `TARGET` | Current working directory | The project being configured |

## Model Alias Map

Source files use short aliases in their `model:` frontmatter field. When copying agents and commands (NOT skills), replace the alias with the OpenCode model ID.

| Alias | OpenCode Model ID |
|---|---|
| `sonnet` | `anthropic/claude-sonnet-4-5` |
| `opus` | `anthropic/claude-opus-4-5` |
| `gpt5-codex` | `openai/gpt-5.1-codex` |
| `haiku` | `anthropic/claude-haiku` |
| `flash` | `google/gemini-3-flash` |
| `flash-preview` | `google/gemini-3-flash-preview` |
| `kimi` | `opencode/kimi-k2.5-free` |

Example: a line `model: sonnet` becomes `model: anthropic/claude-sonnet-4-5`. If an alias has no mapping in this table, delete the entire `model:` line.

## Skip Rules

When scanning source directories for files to install, always skip:
- Files named `AGENTS.md` or `README.md`
- Any file inside a `templates/` directory
- Any file inside an `_archive/` directory

---

## Step 1: Install Global Skills

Run each of these commands. Log each one. Continue even if one fails.

```bash
npx -y skills add --yes --global https://github.com/anthropics/skills --skill skill-creator
npx -y skills add --yes --global https://github.com/anthropics/skills --skill frontend-design
npx -y skills add --yes --global https://github.com/forrestchang/andrej-karpathy-skills --skill karpathy-guidelines
```

---

## Step 2: Workflow Directory Setup

All of these go into `TARGET/.claptrap/` (the current project directory).

### 2a: Code Conventions

1. Create directory `TARGET/.claptrap/code-conventions/`.
2. Copy every `.md` file from `CLAPTRAP_REPO/src/code-conventions/` into it.

Currently this includes: `python.md`, `snowflake.md`.

### 2b: Design Templates

1. Create directory `TARGET/.claptrap/designs/`.
2. Copy `CLAPTRAP_REPO/src/designs/TEMPLATE.md` into it.
3. If `CLAPTRAP_REPO/src/designs/example-feature/` exists, copy the entire directory into `TARGET/.claptrap/designs/example-feature/`.

---

## Step 3: Memory System

### 3a: Memory Files

Only create each file if it does not already exist. Do not overwrite.

**`TARGET/.claptrap/memory_inbox.md`:**

```markdown
# Memory Inbox

Capture learnings here during work sessions. Entries will be reviewed and promoted to `memories.md` periodically.

## Format

\```
## [Date] - [Brief Title]
- **Trigger**: What prompted this learning
- **Action**: What to do differently
- **Context**: When this applies
\```

---

<!-- Add new entries below this line -->
```

**`TARGET/.claptrap/memories.md`:**

```markdown
# Memories

Project memories captured during development. Agents should read this file for context and add new memories when significant decisions, patterns, or lessons emerge.

---
```

### 3b: Enforcement Script

1. Copy `CLAPTRAP_REPO/bootstrap/lib/enforcement.py` to `TARGET/.claptrap/enforcement.py`.
2. Make it executable (`chmod 755`).

### 3c: Enforcement Plugin

OpenCode uses a TypeScript plugin (not JSON hooks like other environments).

1. Create `OPENCODE_ROOT/plugins/` if it doesn't exist.
2. Copy `CLAPTRAP_REPO/src/plugins/claptrap-enforcement.ts` to `OPENCODE_ROOT/plugins/claptrap-enforcement.ts`.

---

## Step 4: Clean Up Old Installation

This removes the previous claptrap installation while leaving any user-created files untouched.

1. For each directory in `OPENCODE_ROOT`: `agents/`, `commands/`, `skills/`:
   - Look at every symlink in that directory.
   - If the symlink's target resolves to a path inside `STAGING` (`OPENCODE_ROOT/claptrap/`), delete the symlink.
   - Do NOT delete regular files or symlinks pointing elsewhere.
2. Delete the entire `STAGING` directory (`OPENCODE_ROOT/claptrap/`).

---

## Step 5: Install Agents

Source: `CLAPTRAP_REPO/src/agents/`
Staging: `STAGING/agents/`
Feature: `OPENCODE_ROOT/agents/`

1. Create both directories (`mkdir -p STAGING/agents OPENCODE_ROOT/agents`)
2. For each `.md` file in the source directory (applying skip rules):
   a. Read the file content.
   b. Apply the model alias map: replace any `model: <alias>` line with `model: <opencode-id>`.
   c. Write the transformed content to `STAGING/agents/<filename>`.
   d. Create a relative symlink: `OPENCODE_ROOT/agents/<filename>` -> `../claptrap/agents/<filename>`.

### Generate Debate Agents

These are generated from a template and written directly to `OPENCODE_ROOT/agents/` (NOT symlinked).

Source template: `CLAPTRAP_REPO/src/agents/templates/debate-agent.md`

1. Read the template file.
2. Extract the list of models from the `debate-models:` block in the frontmatter. This is a YAML list that looks like:
   ```yaml
   debate-models:
      - github-copilot/claude-sonnet-4.5
      - opencode/kimi-k2.5-free
      - openai/gpt-5.2
      - google/gemini-3-flash-preview
   ```
3. Remove the entire `debate-models:` block (the key and all its list items) from the content.
4. For each model in the list, numbered starting at 1:
   - Replace all `{NAME}` with the number (e.g., `1`, `2`, `3`).
   - Replace all `{MODEL}` with the model string (e.g., `opencode/kimi-k2.5-free`).
   - Write the result to `OPENCODE_ROOT/agents/debate-agent-<number>.md`.

---

## Step 6: Install Commands

Source: `CLAPTRAP_REPO/src/commands/`
Staging: `STAGING/commands/`
Feature: `OPENCODE_ROOT/commands/`

Same process as agents (Step 5), without the debate agent generation:

1. Create both directories (`mkdir -p STAGING/commands OPENCODE_ROOT/commands`).
2. For each `.md` file in the source directory (applying skip rules):
   a. Read the file content.
   b. Apply the model alias map.
   c. Write to `STAGING/commands/<filename>`.
   d. Create a relative symlink: `OPENCODE_ROOT/commands/<filename>` -> `../claptrap/commands/<filename>`.

---

## Step 7: Install Skills

Source: `CLAPTRAP_REPO/src/skills/`
Staging: `STAGING/skills/`
Feature: `OPENCODE_ROOT/skills/`

Skills are different from agents and commands in two ways:
- **No model transforms.** Copy file content as-is.
- **Symlink at the directory level**, not the file level. Each skill is a folder (e.g., `memory-capture/`) containing files.

1. Create both directories (`mkdir -p STAGING/skills OPENCODE_ROOT/skills`).
2. For each `.md` file in the source directory (applying skip rules):
   a. Copy the file to `STAGING/skills/`, preserving its relative directory structure. For example, `src/skills/memory-capture/SKILL.md` goes to `STAGING/skills/memory-capture/SKILL.md`.
3. For each skill directory created in staging (e.g., `STAGING/skills/memory-capture/`):
   a. Create a relative symlink: `OPENCODE_ROOT/skills/<skill-name>` -> `../claptrap/skills/<skill-name>`.
   b. Only create the symlink once per skill directory, not per file.

---

## Step 8: Configure .gitignore

Add these entries to `TARGET/.gitignore`. Skip any entry that already exists in the file.

```
.claude/
.codex/
.cursor/
.gemini/
.github/
.opencode/
.claptrap/
.serena/
```

---

## Step 9: Check MCP Servers

This is informational only. For each of these servers, report whether it's configured:
- `serena`
- `context7`
- `snowflake`

```bash
opencode mcp list
```

Look for each server name in the output. Report OK, failed, or not found for each.

---

## Expected Result

```
~/.config/opencode/
  claptrap/                          # Staging (real files live here)
    agents/
      alignment-reviewer.md
      claptrap-explore.md
      code-reviewer.md
      feasibility-reviewer.md
      plan-reviewer.md
      research.md
      ui-designer.md
    commands/
      claptrap-refactor.md
    skills/
      claptrap-code-conventions/SKILL.md
      claptrap-memory/SKILL.md
      claptrap-refactor/SKILL.md
      memory-capture/SKILL.md
      memory-curator/SKILL.md
      snowflake/SKILL.md
      superpowers-pause/SKILL.md
  agents/                            # Symlinks + debate agents
    alignment-reviewer.md           -> ../claptrap/agents/alignment-reviewer.md
    claptrap-explore.md             -> ../claptrap/agents/claptrap-explore.md
    code-reviewer.md                -> ../claptrap/agents/code-reviewer.md
    feasibility-reviewer.md         -> ../claptrap/agents/feasibility-reviewer.md
    plan-reviewer.md                -> ../claptrap/agents/plan-reviewer.md
    research.md                     -> ../claptrap/agents/research.md
    ui-designer.md                  -> ../claptrap/agents/ui-designer.md
    debate-agent-1.md                (generated file, NOT a symlink)
    debate-agent-2.md                (generated file, NOT a symlink)
    debate-agent-3.md                (generated file, NOT a symlink)
    debate-agent-4.md                (generated file, NOT a symlink)
  commands/
    claptrap-refactor.md            -> ../claptrap/commands/claptrap-refactor.md
  skills/
    claptrap-code-conventions       -> ../claptrap/skills/claptrap-code-conventions
    claptrap-memory                 -> ../claptrap/skills/claptrap-memory
    claptrap-refactor               -> ../claptrap/skills/claptrap-refactor
    memory-capture                  -> ../claptrap/skills/memory-capture
    memory-curator                  -> ../claptrap/skills/memory-curator
    snowflake                       -> ../claptrap/skills/snowflake
    superpowers-pause               -> ../claptrap/skills/superpowers-pause
  plugins/
    claptrap-enforcement.ts          (copied file)

<project>/
  .claptrap/
    code-conventions/
      python.md
      snowflake.md
    designs/
      TEMPLATE.md
      example-feature/design.md
    enforcement.py
    memory_inbox.md
    memories.md
  .gitignore                         (updated)
```
