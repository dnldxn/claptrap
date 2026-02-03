---
name: "claptrap-spawn-subagent"
description: Spawn subagents with fresh context and bounded scope.
---

# Subagent Spawning

- Subagents spawn in a fresh context; include all necessary background and constraints.
- Spawn the `research` subagent when external documentation would improve accuracy or completeness.
- Spawn the `claptrap-explore-project` subagent when codebase context (existing patterns, dependencies, structure) is required.

**Research subagent prompt template:**
- **Query**: [Specific question to answer]
- **Context**: [Project details, current idea, why research is needed]
- **Constraints**: [Scope, do not modify code, cite sources if available]

**claptrap-explore-project subagent prompt template:**
- **What to find**: [Files, patterns, APIs, conventions]
- **Scope**: [Directories or areas to search]
- **Constraints**: [No changes, summarize findings]