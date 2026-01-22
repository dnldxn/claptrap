# claptrap
Custom AI agents to use with Github Copilot, Claude, Codex, Gemini, etc

This repository contains a set of custom AI agents designed to work with various large language models (LLMs) such as Github Copilot, Claude, Codex, Gemini, and others. These agents are tailored to assist with software development tasks by following specific workflows and principles.

## Agents Overview
The repository includes the following AI agents in `src/agents/`, each with a distinct role in the software development lifecycle:

1. **UI Designer** (`ui-designer.md`): Designs user interfaces based on project requirements.
2. **Plan Reviewer** (`plan-reviewer.md`): Validates proposals and tasks against requirements.
3. **Alignment Reviewer** (`alignment-reviewer.md`): Validates that proposals align with project goals.
4. **Feasibility Reviewer** (`feasibility-reviewer.md`): Assesses technical feasibility and risks.
5. **Code Reviewer** (`code-reviewer.md`): Reviews code changes for correctness and maintainability.
6. **Refactor** (`refactor.md`): Refactors code for simplicity and readability while preserving behavior.
7. **Research** (`research.md`): Researches docs and writes concise developer references.

For the full workflow and how agents fit together, see `src/agents/AGENTS.md`.


## Installation

Run the bootstrap installer from your target project directory:

```bash
python3 /path/to/claptrap/bootstrap/install.py
```

Or create a shell alias for convenience:

```bash
alias claptrap-install='python3 "$HOME/projects/claptrap/bootstrap/install.py"'
```

See `bootstrap/README.md` for detailed installation options and environment-specific setup.


## Usage

```bash
/brainstorm
/propose <design-path>
/implement-change <change-name>
/archive-change <change-name>
/finish-openspec-change
```

## Designs

Design exploration documents live in `src/designs/`. Use `src/designs/TEMPLATE.md` and
store new designs at `src/designs/<feature-slug>/design.md` (kebab-case feature slug).

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

The repository includes a lightweight memory system to capture and retain project decisions, patterns, anti-patterns, and lessons learned. See `src/skills/memory/SKILL.md` for usage details.

## Old / Deprecated / Reference

```bash
cd $PROJECT_PATH

# Set your agent CLI command
export AGENT_CLI="claude -p"  # Claude Code
export AGENT_CLI="copilot --prompt"  # GitHub Copilot CLI
export AGENT_CLI="codex exec"  # OpenAI Codex CLI
export AGENT_CLI="agent --model 'gpt-5.2-high' -p"  # Cursor CLI
```
