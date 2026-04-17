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
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-next
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-code-conventions
npx skills add https://github.com/dnldxn/claptrap/skills --skill snowflake
npx skills add https://github.com/dnldxn/claptrap/skills --skill jupyter-notebooks
npx skills add https://github.com/dnldxn/claptrap/skills --skill claptrap-refactor
```

### `claptrap-next` (workflow router)

Use this skill when you want to **advance a claptrap workflow** in a *target* project and need to know **what to do next** from the current `.planning/ROADMAP.md` state.

It:

1. Reads `.planning/ROADMAP.md` (or treats the workflow as not started if the file is missing).
2. Parses the **Current Position** block: milestone (`M##-slug`), phase (`P##-slug` and “X of Y”), and **Status**.
3. If status is **In progress**, checks the active milestone workspace with `git status` to see if it is **dirty** or **clean** (unfinished execution vs ready to complete the phase). The workspace may be the current checkout or `.worktrees/M##-slug/`.
4. Maps status (and workspace state) to **1–3 recommended next actions** (for example: plan, execute, resume execution, complete phase, complete milestone, brainstorm a new milestone).
5. After you choose an action, loads the matching **sub-skill** and passes fresh `M##-slug` / `P##-slug` from the ROADMAP:

| Action | Sub-skill |
| --- | --- |
| Brainstorm new milestone | `claptrap-brainstorm` |
| Plan / resume planning | `claptrap-plan` |
| Execute / resume execution | `claptrap-execute` |
| Complete phase (including “complete anyway” when dirty) | `claptrap-complete-phase` |
| Complete milestone / archive | `claptrap-complete-milestone` |

**Pitfalls the skill guards against:** re-read the ROADMAP after `complete-phase` (the phase pointer moves automatically); never pass stale slugs; keep using the milestone workspace selected during brainstorming; always inspect the active workspace before offering “complete phase” while status is **In progress**.

### Git Workspace Lifecycle

Branches, worktrees, and commits are scoped to the **milestone**, never to individual phases. Here is what happens in git at each workflow step:

| Step | Branch / Worktree Action | Commit Offered |
| --- | --- | --- |
| `ct-brainstorm` | Asks whether to create a dedicated workspace. If yes: create branch `feature/M##-slug` off the default branch and worktree `.worktrees/M##-slug/`. If no: stay in the current checkout. | `brainstorm: M##-slug` |
| `ct-plan` | No new branch or worktree. Planning happens in the resolved milestone workspace. | `plan: P##-slug` |
| `ct-execute` | No new per-phase branch. Code and doc changes happen in the milestone workspace. Execution commits are made by the `subagent-driven-development` skill as the plan progresses. | (per plan task) |
| `ct-complete-phase` | No merging. Branch and worktree stay open until the milestone completes. | `docs: P##-slug complete` |
| `ct-complete-milestone` | 1. Offer to commit any uncommitted changes in the milestone workspace. 2. If a dedicated worktree is in use, offer a **squash merge** of `feature/M##-slug` into the default branch, then tag the result `milestone/M##-slug`, then offer to remove `.worktrees/M##-slug/` and delete `feature/M##-slug`. 3. If no dedicated worktree, tag the current commit `milestone/M##-slug` in place. | milestone completion commit + squash merge commit |

**Workspace resolution:** Before any read/write during plan, execute, complete-phase, or complete-milestone, the milestone workspace root is resolved: if `.worktrees/M##-slug/.planning/milestones/M##-slug/` exists, that worktree is used; otherwise the current repo root is used. All work for a milestone stays in that single workspace until the milestone is complete.

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
- For a project that uses claptrap planning (`.planning/ROADMAP.md`), invoke the `claptrap-next` skill when you need to decide the next workflow step or which claptrap sub-skill to run
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
