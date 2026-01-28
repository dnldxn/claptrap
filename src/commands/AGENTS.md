This folder contains **command definitions**: structured workflows that agents execute when users invoke slash commands.

## Rules

1. **Read `skills/AGENTS.md`** for the skill registry and loading instructions.

## Available Commands

| Command | Purpose |
|---------|---------|
| `archive-change` | Archive a completed change and capture lessons learned |
| `brainstorm` | Turn ideas into designs through collaborative dialogue |
| `finish-openspec-change` | Mark tasks complete and archive (shortcut) |
| `implement-change` | Implement an approved OpenSpec change |
| `propose` | Create OpenSpec change proposals from designs |
| `refactor` | Refactor code for simplicity and readability |

## Command Structure

Each command file should include:

- **Frontmatter**: `name` and `description`
- **Overview**: What the command does and its inputs/outputs
- **Skills**: Which skills are required
- **Workflow Steps**: Sequential steps to execute
- **Key Principles**: Important constraints and guidelines
