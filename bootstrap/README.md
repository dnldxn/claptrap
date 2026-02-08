# Claptrap Bootstrap

Install AI agent workflows into your project.

## Quick Start

```bash
cd /path/to/your/project
python ~/projects/claptrap/bootstrap/install.py ~/projects/claptrap
```

## What It Does

The installer sets up your project with:

1. **OpenSpec** - Change proposal workflow (installed/upgraded automatically)
2. **Provider config** - Agents, commands, and skills for your AI tool
3. **Workflow directory** - Code conventions and memories
4. **Tool checks** - Verifies ripgrep and Serena MCP are available

## Supported Providers

| Provider | Config Directory |
|----------|------------------|
| Cursor | `.cursor/` |
| GitHub Copilot | `.github/` |
| OpenCode | `.opencode/` |
| Claude | `.claude/` |
| Codex | `.codex/` |
| Gemini | `.gemini/` |

## Installation

Run from your target project directory:

```bash
cd /path/to/your/project
python /path/to/claptrap/bootstrap/install.py /path/to/claptrap
```

Example:

```bash
cd ~/my-project
python ~/projects/claptrap/bootstrap/install.py ~/projects/claptrap
```

The installer will:
- Prompt you to select your AI provider
- Install or upgrade OpenSpec (shows version changes)
- Create `.claptrap/` with conventions
- Copy agents/commands/skills to your provider's directory
- Update `.gitignore` with appropriate entries
- Add claptrap instructions to `AGENTS.md`
- Check for ripgrep and Serena MCP

## Directory Structure After Install

```
your-project/
├── .cursor/              # (or .github/, .claude/, etc.)
│   ├── agents/
│   ├── commands/
│   └── skills/
├── .claptrap/
│   ├── code-conventions/
│   └── memories.md
├── openspec/             # Created by openspec init
├── AGENTS.md             # Updated with claptrap instructions
└── .gitignore            # Updated with ignore entries
```

## Requirements

- Python 3.10+
- Node.js and npm (for OpenSpec)
- OpenSpec CLI v1.0.2+ (required for `/claptrap-propose` and `/opsx:*` commands)
- Your chosen AI provider's CLI (optional, for MCP checks)

## Re-running the Installer

Safe to run multiple times:
- Existing `memories.md` is preserved
- `AGENTS.md` claptrap section is updated in place
- `.gitignore` entries are only added if missing
- Provider directory files are overwritten with latest versions
