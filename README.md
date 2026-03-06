# Claptrap

## Setup

```bash
npx skills list -g      # List global skills
npx skills update       # Update skills
skills remove --global  # Interactive skill removal

# General skills
npx skills add https://github.com/forrestchang/andrej-karpathy-skills --skill karpathy-guidelines
npx skills add https://github.com/anthropics/skills --skill skill-creator

# Workflow-specific skills
npx skills add https://github.com/obra/superpowers --skill using-superpowers
npx skills add https://github.com/obra/superpowers --skill brainstorming

# Domain-specific skills (as needed)
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/wshobson/agents --skill dbt-transformation-patterns
npx skills add https://github.com/personamanagmentlayer/pcl --skill snowflake-expert
```

## External Tools

### agentchattr
https://github.com/bcurts/agentchattr

```bash
cd ~/apps
git clone https://github.com/bcurts/agentchattr.git
cd <PROJECT_ROOT>
~/projects/claptrap/scripts/start_agentchattr.sh
```

### Everything Claude Code
- https://github.com/affaan-m/everything-claude-code

### Opencode Cursor
- https://github.com/Nomadcxx/opencode-cursor
