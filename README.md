# Claptrap

## Skills

```bash
npx skills list -g      # List global skills
npx skills update       # Update skills
skills remove --global  # Interactive skill removal

# General skills
npx skills add https://github.com/forrestchang/andrej-karpathy-skills --skill karpathy-guidelines  # General AI agent guidelines from Andrej Karpathy
npx skills add https://github.com/anthropics/skills --skill skill-creator

# Workflow-specific skills
npx skills add https://github.com/obra/superpowers --skill using-superpowers
npx skills add https://github.com/obra/superpowers --skill brainstorming
npx skills add https://github.com/trailofbits/skills --skill ask-questions-if-underspecified

# Domain-specific skills (as needed)
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/wshobson/agents --skill dbt-transformation-patterns

# Custom skills (as needed)
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-code-conventions
npx skills add https://github.com/dnldxn/claptrap/skills --skill snowflake
npx skills add https://github.com/dnldxn/claptrap/skills --skill jupyter-notebooks
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
```

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

### Opencode Cursor
- https://github.com/Nomadcxx/opencode-cursor
