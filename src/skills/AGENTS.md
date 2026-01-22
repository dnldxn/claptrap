This folder contains **portable "Skills"**: small, reusable playbooks agents can invoke to perform common operations consistently across environments.

## How to use skills

- **Pick the smallest skill that fits** the task and follow its `SKILL.md` as the source-of-truth.
- **Don't wait for the user to ask** if a skill should be used; decide proactively.
- **Keep outputs provider- and environment-agnostic** unless the skill explicitly calls out adapter-specific behavior.
- **If you are unable to load a required skill**, ask for help and STOP.

## Skill Registry

### `memory`
- **Path**: `skills/memory/SKILL.md`
- **Purpose**: Read/write/update/delete project memory entries (decisions, patterns, anti-patterns, lessons).
- **Use when**: You observe a reusable decision/lesson/pattern worth capturing, or need to recall prior choices.

### `openspec`
- **Path**: `skills/openspec/SKILL.md`
- **Purpose**: Draft/apply/archive OpenSpec change proposals and enforce following `openspec/AGENTS.md`.
- **Use when**: Work involves proposals/specs/plans, implementing an OpenSpec change, or archiving a change.

### `design-to-proposal`
- **Path**: `skills/design-to-proposal/SKILL.md`
- **Purpose**: Create OpenSpec proposals from an existing design, then run alignment + feasibility review.
- **Use when**: You have a design and want to produce one or more reviewed OpenSpec proposals.

### `spawn-subagent`
- **Path**: `skills/spawn-subagent/SKILL.md`
- **Purpose**: Spawn a subagent with fresh context and bounded scope, then integrate results back.
- **Use when**: You need parallel research/exploration/specialized review without polluting the main thread.

### `gemini`
- **Path**: `skills/gemini/SKILL.md`
- **Purpose**: Use the Google Gemini CLI to analyze code, review plans, and process large contexts (>200k tokens).
- **Use when**: Comprehensive code reviews across multiple files, plan reviews, big context analysis, or multi-file pattern analysis.

### `frontend-design`
- **Path**: `skills/frontend-design/SKILL.md`
- **Purpose**: Create distinctive, production-grade frontend interfaces with bold aesthetics.
- **Use when**: Building components, pages, or applications that require visually striking, memorable design with intentional aesthetic direction.
