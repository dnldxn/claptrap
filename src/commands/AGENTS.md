This folder contains **command definitions**: structured workflows that agents execute when users invoke slash commands.

## Rules

1. **Read `skills/AGENTS.md`** for the skill registry and loading instructions.

## Available Commands

| Command | Purpose |
|---------|---------|
| `brainstorm` | Turn ideas into designs through collaborative dialogue |
| `propose-change` | Create OpenSpec change proposals from designs |
| `implement-change` | Implement an approved OpenSpec change |
| `code-review` | Review changes for correctness, safety, and spec alignment |
| `archive-change` | Archive a completed change and capture lessons learned |
| `finish-openspec-change` | Mark tasks complete and archive (shortcut) |

## Command Structure

Each command file should include:

- **Frontmatter**: `name` and `description`
- **Overview**: What the command does and its inputs/outputs
- **Skills**: Which skills are required
- **Workflow Steps**: Sequential steps to execute
- **Key Principles**: Important constraints and guidelines
