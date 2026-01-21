# src/

This directory contains **installable content** that gets symlinked or copied into target projects via `install.sh`.

## Contents

| Directory | Purpose |
|-----------|---------|
| `agents/` | Provider-neutral agent definitions (proposer, developer, reviewer, etc.) |
| `commands/` | Slash command workflows (`/brainstorm`, `/propose`, etc.) |
| `skills/` | Reusable playbooks for common operations (memory, spawning subagents) |
| `code-conventions/` | Language-specific style guides |
| `memory/` | Templates for project memory system |
| `designs/` | Design document templates and examples |

## Usage

From the target project, run claptrap’s installer to copy this content into `.workflow/` and wire up the provider directory (`.cursor/`, `.github/`, `.opencode/`, etc.):

```bash
export CLAPTRAP_PATH="$HOME/projects/claptrap"
"$CLAPTRAP_PATH/install.sh"
```

## Note

Files here are written from the **target project's perspective** — relative paths like `skills/memory/SKILL.md` work after installation, not from this repo's root.
