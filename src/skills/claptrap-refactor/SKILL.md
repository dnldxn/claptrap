---
name: "claptrap-refactor"
description: Refactor code for simplicity and readability while preserving behavior. Use when asked to simplify, clean up, refactor, or apply clean code principles. Also use when writing new code that should follow clean code standards.
---

# Refactor Skill

Simplify and clarify code without changing behavior. Preserve output, side effects, and public APIs. Apply clean code principles to new and existing code.

## Core Principles

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility - each function/class does ONE thing |
| **DRY** | Don't Repeat Yourself - extract duplicates, reuse |
| **KISS** | Keep It Simple - simplest solution that works |
| **YAGNI** | You Aren't Gonna Need It - don't build unused features |
| **Boy Scout** | Leave code cleaner than you found it |

Additional principles:
- **Simple**: Strive for the simplest and leanest possible solution that meets requirements.
- **Readability**: Code should be easy to read and understand at a glance.
- **Conciseness**: Reduce code size without sacrificing other principles.
- **Minimal Error Handling**: Include error handling only where failures are likely or consequences are severe.

## Rules

You **MUST**:

- Strictly adhere to coding conventions specified in the project's code conventions (e.g., `.claptrap/code-conventions/`).
  - If unable to find the corresponding style guide, STOP and ask where to find it (don't guess).
- Maintain the same functionality and behavior as the original code; any change in behavior is a failure.
- Do NOT print the full contents of the new code. Summarize changes instead.

## Naming Conventions

| Element | Convention |
|---------|------------|
| **Variables** | Reveal intent: `user_count` not `n` |
| **Functions** | Verb + noun: `get_user_by_id()` not `user()` |
| **Booleans** | Question form: `is_active`, `has_permission`, `can_edit` |
| **Constants** | SCREAMING_SNAKE: `MAX_RETRY_COUNT` |

If you need a comment to explain a name, rename it instead.

## Function Rules

| Rule | Description |
|------|-------------|
| **Small** | Max 20 lines, ideally 5-10 |
| **One Thing** | Does one thing, does it well |
| **One Level** | One level of abstraction per function |
| **Few Args** | Max 3 arguments, prefer 0-2 |
| **No Side Effects** | Don't mutate inputs unexpectedly |

## Code Structure

| Pattern | Apply |
|---------|-------|
| **Guard Clauses** | Early returns for edge cases |
| **Flat > Nested** | Avoid deep nesting (max 2 levels) |
| **Composition** | Small functions composed together |
| **Colocation** | Keep related code close |

## Guidelines

### Code Elimination

- Keep error handling and variable checking to a **bare minimum**; do not handle cases where the variable is likely to have a value
- Delete unused functions, variables, imports, dependencies. Remove redundant or dead code.
- Remove dead code paths and unreachable branches
- Combine repeated snippets into helper functions; eliminate duplicate logic through extraction/consolidation
- Strip unnecessary abstractions and over-engineering
- Purge commented-out code and debug statements

### Simplification

- Replace complex patterns with simpler alternatives
- Inline single-use functions and variables
- Flatten nested conditionals and loops
- Use built-in language features over custom implementations
- Apply consistent formatting and naming
- Use descriptive function and variable names

### Documentation Cleanup

- Use short comments and/or newlines to break big code blocks into smaller sections; prefer self-explanatory code to comments
- Remove outdated comments and documentation
- Delete auto-generated boilerplate
- Simplify verbose explanations
- Remove redundant inline comments
- Update stale references and links

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Comment every line | Delete obvious comments |
| Helper for one-liner | Inline the code |
| Factory for 2 objects | Direct instantiation |
| utils.ts with 1 function | Put code where used |
| Deep nesting | Guard clauses |
| Magic numbers | Named constants |
| God functions | Split by responsibility |

## Self-Correction Checklist

Once finished, review the refactored code:

- Have I maintained the same functionality and behavior?
- Does the code follow the project's coding conventions?
- Could any function be simpler?
- Is every piece of error handling truly necessary?
- Are comments adding value or just taking space?
- Is the code easy to read and understand at a glance?
- Are there opportunities to use common functions or abstractions?
- Is the code free of redundancy and dead code?

## Final Step

Suggest further simplifications that might be more aggressive, if any. These can include changes in behavior or user experience if it will significantly simplify the code. If none, respond with "No further improvements suggested." If you suggest further updates, provide a brief rationale for each, then ask the user if they would like to apply them.
