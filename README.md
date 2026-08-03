# Claptrap

Claptrap is a personal AI-agent configuration toolkit. The repository keeps reusable Skills and workflow files; the installer currently installs only the OpenCode continuous-learning system described below.

## Install

```bash
python bootstrap/install.py
```

The stdlib-only installer creates repo-owned symlinks under `~/.config/opencode` for:

- `claptrap/instructions.md` — continuous-learning instructions;
- `claptrap/plugin.ts` — event logging, notifications, status, and weekly gardener scheduling;
- `agents/claptrap/ct-gardener.md` — the complete weekly managed-Skill review; and
- `commands/claptrap/` — `/ct-learn-skill`, `/ct-run-gardener`, and `/ct-status`.

The installer removes stale symlinks only when they resolve into this repository. It refuses to replace non-repo files or directories. It also sweeps the old provider locations for repo-owned links. Existing repository Skills (`dd-*`, dagu, snowflake, jupyter-notebooks, and others) remain in this repository but are no longer installed by this script. Install `jupyter-notebooks` separately with `npx skills add` when needed.

After installation, merge these entries into the existing arrays in `~/.config/opencode/opencode.json` (the installer warns but does not edit that file):

```jsonc
{
  "instructions": ["./claptrap/instructions.md"],
  "plugin": ["./claptrap/plugin.ts"]
}
```

The gardener agent uses `9router/skill-gardener`. Add a `skill-gardener` model entry to `provider.9router.models` in the same config before running it.

## Continuous learning

Normal work is guided to load plausible Skills, recall relevant Mnemosyne memories, and store only durable, verified learning. `/ct-learn-skill` performs an explicit learning pass in the current session. `/ct-run-gardener` starts the detached weekly review, and `/ct-status` reports activity from the JSONL event log and managed-Skill directories.

Claptrap records only safe metadata such as event type, Skill name, tool name, project path, and timestamps. It does not log prompts, model responses, Skill contents, Mnemosyne arguments, or memory contents.

## Managed-Skill boundary

The gardener may modify a Skill only when all three markers are present:

1. the file is under a `skills/claptrap/` or `skills-archive/claptrap/` root;
2. its immediate directory starts with `ct-`; and
3. its frontmatter contains `metadata.managed-by: ct-gardener`.

Unmanaged Skills are read-only to the gardener. Archiving is always a move from `skills/claptrap/` to `skills-archive/claptrap/` in the same scope; it is never a permanent delete.

## Skills

```bash
npx skills list -g
npx skills update
skills remove --global

# General skills
npx skills add https://github.com/forrestchang/andrej-karpathy-skills --skill karpathy-guidelines
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

# Claptrap workflow skills
npx skills add https://github.com/dnldxn/claptrap/skills --skill dd-grill-me
npx skills add https://github.com/dnldxn/claptrap/skills --skill dd-writing-plans
npx skills add https://github.com/dnldxn/claptrap/skills --skill dd-implement

# Custom domain skills (as needed)
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-code-conventions
npx skills add https://github.com/dnldxn/claptrap/skills --skill snowflake
npx skills add https://github.com/dnldxn/claptrap/skills --skill dagu
npx skills add https://github.com/dnldxn/claptrap/skills --skill jupyter-notebooks
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
```

## Claptrap workflow

All work is done on the `main` branch and does not use Git worktrees. The workflow is a three-step process:

| Step | Skill | Description |
| --- | --- | --- |
| Design | `dd-grill-me` | Interviews the user until a shared understanding is reached. Offers to save the spec to a Github Issue or local planning file |
| Plan | `dd-writing-plans` | Generates one or more detailed implementation plans from the spec.  Offers to save the plan/s as Github sub-Issues of the spec Issue or to local planning file/s |
| Implement | `dd-implement` | Implements a plan from a Github Issue or local planning file |

`ct-implement` stays on the current branch when invoked through this workflow. The close skill handles verification and asks before any merge, deletion, or push.

## Commands

- `/ct-learn-skill` — preserve verified learning from the current work;
- `/ct-run-gardener` — start the detached complete weekly review; and
- `/ct-status` — show Skill, Mnemosyne, and gardener activity.
