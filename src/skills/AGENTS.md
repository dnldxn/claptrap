This folder contains **portable "Skills"**: small, reusable playbooks agents can invoke to perform common operations consistently across environments.

## How to use skills

- **Pick the smallest skill that fits** the task and follow its `SKILL.md` as the source-of-truth.
- **Don't wait for the user to ask** if a skill should be used; decide proactively.
- **Keep outputs provider- and environment-agnostic** unless the skill explicitly calls out adapter-specific behavior.
- **If you are unable to load a required skill**, ask for help and STOP.

## Skill Registry

### `code-conventions`
- **Path**: `skills/claptrap:code-conventions/SKILL.md`
- **Purpose**: Load project-specific code style guidelines for a given language.
- **Use when**: Writing or reviewing code to ensure adherence to project standards.

### `code-review`
- **Path**: `skills/claptrap:code-review/SKILL.md`
- **Purpose**: Generic methodology for reviewing code changes against requirements, specs, or proposals.
- **Use when**: You need to review code changes and produce structured, actionable feedback.

### `design-to-proposal`
- **Path**: `skills/design-to-proposal/SKILL.md`
- **Purpose**: Create OpenSpec proposals from an existing design, then run alignment + feasibility review.
- **Use when**: You have a design and want to produce one or more reviewed OpenSpec proposals.

### `memory`
- **Path**: `skills/memory/SKILL.md`
- **Purpose**: Read/write/update/delete project memory entries (decisions, patterns, anti-patterns, lessons).
- **Use when**: You observe a reusable decision/lesson/pattern worth capturing, or need to recall prior choices.

### `openspec-create-proposal`
- **Path**: `skills/openspec-create-proposal/SKILL.md`
- **Purpose**: Convert a well-defined idea into a formal OpenSpec proposal.md document.
- **Use when**: You have a clear idea ready to be formalized into a proposal.

### `refactor`
- **Path**: `skills/refactor/SKILL.md`
- **Purpose**: Refactor code for simplicity and readability while preserving behavior.
- **Use when**: Asked to simplify, clean up, or refactor code without changing its functionality.

### `snowflake`
- **Path**: `skills/snowflake/SKILL.md`
- **Purpose**: Execute SQL queries against Snowflake databases and maintain a data dictionary of queried tables.
- **Use when**: Querying, retrieving, or exploring data in Snowflake.

### `spawn-subagent`
- **Path**: `skills/spawn-subagent/SKILL.md`
- **Purpose**: Spawn a subagent with fresh context and bounded scope, then integrate results back.
- **Use when**: You need parallel research/exploration/specialized review without polluting the main thread.
