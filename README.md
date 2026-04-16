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

# Custom skills (as needed)
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-workflow
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-code-conventions
npx skills add https://github.com/dnldxn/claptrap/skills --skill snowflake
npx skills add https://github.com/dnldxn/claptrap/skills --skill jupyter-notebooks
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
```

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
- If the plan or implementation work involves creating or modifying any UI elements, also invoke the `frontend-design` skill
- If the plan or implementation work involves creating or modifying any web elements, also invoke the `web-design-guidelines` skill
- If you cannot find a Skill, stop and ask for help instead of guessing.
```

## Plugins

- https://github.com/ephraimduncan/opencode-cursor

## External Tools

### agentchattr
https://github.com/bcurts/agentchattr

```bash
cd ~/apps
git clone https://github.com/bcurts/agentchattr.git
cd <PROJECT_ROOT>
~/projects/claptrap/scripts/start_agentchattr.sh

~/apps/agentchattr-orig/macos-linux/start.sh

python ~/apps/agentchattr-orig/wrapper.py claude --no-restart
python ~/apps/agentchattr-orig/wrapper.py codex --no-restart
```

### Everything Claude Code
- https://github.com/affaan-m/everything-claude-code
