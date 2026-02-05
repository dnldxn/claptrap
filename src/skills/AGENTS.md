This folder contains **portable "Skills"**: small, reusable playbooks agents can invoke to perform common operations consistently across environments.

## How to use skills

- **Pick the smallest skill that fits** the task and follow its `SKILL.md` as the source-of-truth.
- **Don't wait for the user to ask** if a skill should be used; decide proactively.
- **Keep outputs provider- and environment-agnostic** unless the skill explicitly calls out adapter-specific behavior.
- **If you are unable to load a required skill**, ask for help and STOP.

## Skill Registry

### `claptrap-brainstorming`
- **Path**: `skills/claptrap-brainstorming/SKILL.md`
- **Purpose**: Turn raw ideas into clear, validated design documents through bounded dialogue.
- **Use when**: Starting a new feature, exploring requirements, or when `/claptrap-brainstorm` is invoked.
- **Templates**: `templates/design.md`

### `claptrap-propose`
- **Path**: `skills/claptrap-propose/SKILL.md`
- **Purpose**: Convert an approved design into OpenSpec artifacts (proposal, specs, tasks) with alignment + feasibility review.
- **Use when**: A design is ready to be formalized, or when `/claptrap-propose` is invoked.
- **Templates**: `templates/proposal-hints.md`, `templates/spec-hints.md`, `templates/tasks-hints.md`

### `claptrap-memory`
- **Path**: `skills/claptrap-memory/SKILL.md`
- **Purpose**: Read/write/update/delete project memory entries (decisions, patterns, anti-patterns, lessons).
- **Use when**: You observe a reusable decision/lesson/pattern worth capturing, or need to recall prior choices.

### `memory-capture`
- **Path**: `skills/memory-capture/SKILL.md`
- **Purpose**: Capture candidate learnings to inbox during work sessions (high recall).
- **Use when**: You discover non-obvious decisions, gotchas, patterns, or lessons worth potentially keeping.

### `memory-curator`
- **Path**: `skills/memory-curator/SKILL.md`
- **Purpose**: Score inbox candidates and promote quality entries to durable memory (high precision).
- **Use when**: Session end, or periodically when inbox has accumulated candidates.

### `claptrap-spawn-subagent`
- **Path**: `skills/claptrap-spawn-subagent/SKILL.md`
- **Purpose**: Spawn a subagent with fresh context and bounded scope, then integrate results back.
- **Use when**: You need parallel research/exploration/specialized review without polluting the main thread.

### `claptrap-refactor`
- **Path**: `skills/claptrap-refactor/SKILL.md`
- **Purpose**: Refactor code for simplicity and readability while preserving behavior.
- **Use when**: Asked to simplify, clean up, or refactor code without changing its functionality.

## Other Skills

### `claptrap-code-conventions`
- **Path**: `skills/claptrap-code-conventions/SKILL.md`
- **Purpose**: Load project-specific code style guidelines for a given language.
- **Use when**: Writing or reviewing code to ensure adherence to project standards.

### `claptrap-code-review`
- **Path**: `skills/claptrap-code-review/SKILL.md`
- **Purpose**: Generic methodology for reviewing code changes against requirements, specs, or proposals.
- **Use when**: You need to review code changes and produce structured, actionable feedback.

### `snowflake`
- **Path**: `skills/snowflake/SKILL.md`
- **Purpose**: Execute SQL queries against Snowflake databases and maintain a data dictionary of queried tables.
- **Use when**: Querying, retrieving, or exploring data in Snowflake.
