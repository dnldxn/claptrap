This folder contains **command definitions**: structured workflows that agents execute when users invoke slash commands.

## Rules

1. **Read `skills/AGENTS.md`** for the skill registry and loading instructions.

## Available Commands

| Command | Invocation | Purpose |
|---------|------------|---------|
| `claptrap-brainstorm` | `/claptrap-brainstorm <idea>` | Turn ideas into designs through collaborative dialogue |
| `claptrap-propose` | `/claptrap-propose [design-path]` | Generate OpenSpec artifacts (proposal, specs, tasks) from a design |
| `claptrap-review` | `/claptrap-review [change-id]` | Validate artifacts against the source design before implementation |
| `claptrap-refactor` | `/claptrap-refactor <target>` | Refactor code for simplicity and readability |

**Note:** Implementation uses native OpenSpec commands: `/opsx:apply`, `/opsx:verify`, `/opsx:archive`.

## Command Structure

Each command file should include:

- **Frontmatter**: `name` and `description`
- **Overview**: What the command does and its inputs/outputs
- **Skills**: Which skills are required
- **Workflow Steps**: Sequential steps to execute
- **Key Principles**: Important constraints and guidelines
