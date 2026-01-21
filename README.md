# claptrap
Custom AI agents to use with Github Copilot, Claude, Codex, Gemini, etc

This repository contains a set of custom AI agents designed to work with various large language models (LLMs) such as Github Copilot, Claude, Codex, Gemini, and others. These agents are tailored to assist with software development tasks by following specific workflows and principles.

## Agents Overview
The repository includes the following AI agents, each with a distinct role in the software development lifecycle:

1. **Proposer**: Creates change proposals, task checklists, and spec deltas.
2. **Plan Reviewer**: Validates proposals and tasks against requirements.
3. **Developer**: Implements tasks and fixes review findings.
4. **Code Reviewer**: Reviews code changes for correctness and maintainability.
5. **UI Designer**: Designs user interfaces based on project requirements.
6. **Refactor**: Refactors code for simplicity and readability while preserving behavior.
7. **Research Docs**: Researches docs and writes concise developer references.

For the full workflow and how agents fit together, see `src/agents/AGENTS.md`.


## Installation

```bash
export CLAPTRAP_PATH="$HOME/projects/claptrap"
chmod +x "$CLAPTRAP_PATH/install.sh"
"$CLAPTRAP_PATH/install.sh"
```


## Usage

```bash
/brainstorm
/propose <design-path>
/implement-change <change-name>
/code-review <change-name>
/archive-change <change-name>
/finish-openspec-change
```

## Designs

After installation, design exploration documents live in `.workflow/designs/`. Use `.workflow/designs/TEMPLATE.md` and
store new designs at `.workflow/designs/<feature-slug>/design.md` (kebab-case feature slug).

## OpenSpec Commands

```bash
openspec list                      # List changes
openspec create <name>             # Create change
openspec validate <name>           # Validate change
openspec show <name>               # Show details
openspec archive <name> --yes      # Archive completed change
openspec update                    # Update integration
```

## Memory System

The repository includes a lightweight memory system for capturing project context, decisions, patterns, anti-patterns, and lessons learned. See `src/skills/memory/SKILL.md` for usage details. The template is at `src/memory/project.md.template`.

## Old / Deprecated / Reference

```bash
cd $PROJECT_PATH

# Set your agent CLI command
export AGENT_CLI="claude -p"  # Claude Code
export AGENT_CLI="copilot --prompt"  # GitHub Copilot CLI
export AGENT_CLI="codex exec"  # OpenAI Codex CLI
export AGENT_CLI="agent --model 'gpt-5.2-high' -p"  # Cursor CLI
```
