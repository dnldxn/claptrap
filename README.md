# Claptrap

## Skills

```bash
npx skills list -g      # List global skills
npx skills update       # Update skills
skills remove --global  # Interactive skill removal

# General skills
npx skills add https://github.com/forrestchang/andrej-karpathy-skills --skill karpathy-guidelines  # General AI agent guidelines from Andrej Karpathy
npx skills add https://github.com/anthropics/skills --skill skill-creator
npx skills add https://github.com/obra/episodic-memory --skill remembering-conversations

# Workflow-specific skills
npx skills add https://github.com/obra/superpowers --skill using-superpowers
npx skills add https://github.com/obra/superpowers --skill brainstorming
npx skills add https://github.com/obra/superpowers --skill writing-plans
npx skills add https://github.com/obra/superpowers --skill subagent-driven-development
npx skills add https://github.com/obra/superpowers --skill using-git-worktrees
npx skills add https://github.com/trailofbits/skills --skill ask-questions-if-underspecified

# Domain-specific skills (as needed)
npx skills add https://github.com/dammyjay93/interface-design --skill interface-design
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
npx skills add https://github.com/github/awesome-copilot --skill create-agentsmd
npx skills add https://github.com/wshobson/agents --skill dbt-transformation-patterns
npx skills add https://github.com/softaworks/agent-toolkit --skill mermaid-diagrams

# Custom workflow skills
npx skills add https://github.com/dnldxn/claptrap/skills --skill ct-grill-me
npx skills add https://github.com/dnldxn/claptrap/skills --skill ct-writing-plans
npx skills add https://github.com/dnldxn/claptrap/skills --skill ct-implement
npx skills add https://github.com/dnldxn/claptrap/skills --skill ct-close-branch

npx skills add https://github.com/dnldxn/claptrap/skills/githhub-projects --skill gh-grill-me
npx skills add https://github.com/dnldxn/claptrap/skills/githhub-projects --skill gh-writing-plans
npx skills add https://github.com/dnldxn/claptrap/skills/githhub-projects --skill gh-implement


# Custom domain skills (as needed)
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-code-conventions
npx skills add https://github.com/dnldxn/claptrap/skills --skill snowflake
npx skills add https://github.com/dnldxn/claptrap/skills --skill jupyter-notebooks
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
```

### Claptrap Workflow

`claptrap-workflow` and `claptrap-next` are deprecated and archived under `skills/_archive/`. New work uses direct `ct-*` skills.

| Step | Skill | Output |
| --- | --- | --- |
| Design | `ct-grill-me` | `.planning/specs/YYYY-MM-DD-<topic>-design.md` |
| Plan | `ct-writing-plans` | `.planning/plans/YYYY-MM-DD-<topic>-plan.md` |
| Implement | `ct-implement` | Feature-branch work in the current workspace |
| Close | `ct-close-branch` | Verified squash merge, optional tag/delete/push |

Branch rules:

- `ct-implement` creates or reuses `feature/<topic>` in the current workspace. It does not create worktrees.
- If the plan specifies `M##-slug`, the branch is `feature/M##-slug`.
- `ct-close-branch` runs verification, asks before squash merge, asks before deleting the branch, and asks before pushing.
- If the branch is `feature/M##-slug`, closeout creates tag `milestone/M##-slug` after approval.

## Commands

```bash
mkdir -p ~/.config/opencode/commands
ln -s "$PWD/commands" ~/.config/opencode/commands/claptrap
```

Manually add the following to `~/.claude/CLAUDE.md` and `~/.agents/AGENTS.md`, under any existing text:

```markdown
# Skill Instructions

Follow these guidelines for using Skills for any project work:
- Always invoke the `karpathy-guidelines` and `ask-questions-if-underspecified` Skills before doing any work
- For claptrap workflow work, use `ct-grill-me` -> `ct-writing-plans` -> `ct-implement` -> `ct-close-branch`
- Do not use `claptrap-workflow` or `claptrap-next`; both are deprecated
- If the plan or implementation work involves creating or modifying any UI elements, also invoke the `frontend-design` skill
- If the plan or implementation work involves creating or modifying any web elements, also invoke the `web-design-guidelines` skill
- If you cannot find a Skill, stop and ask for help instead of guessing.
```

## Plugins

- https://github.com/ephraimduncan/opencode-cursor
