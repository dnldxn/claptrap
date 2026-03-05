---
name: "claptrap-code-conventions"
description: Load project-specific code style guidelines for a given language. Use before writing or reviewing code to ensure adherence to project standards.
---

# Code Conventions Skill

Load and adhere to the appropriate code style/conventions file for the language being used.

# Core Principles
- **Simple over Clever**: Always favor the simplest solution that meets requirements. Avoid over-engineering.
- **Minimal Complexity**: Reduce moving parts, dependencies, and abstractions to the essential minimum.
- **Code Quality**: Write maintainable, self-documenting code; follow DRY principles for significant duplications (don't obsess over minor repetition)
- **Minimal Error Handling**: Only handle failures at the external boundaries; trust internal code
- **Conciseness**: Make the minimum necessary changes to achieve the goal.
- **Confident**: Make clear recommendations rather than presenting multiple options

## Usage

Determine the primary coding language for the current task.  When writing or reviewing code, load the corresponding conventions using the mapping below.  These conventions do not need to be loaded when simply reading files.  Do NOT load all files, only the one(s) relevant to the language(s) being used.

| Language | File |
|---|---|
| Python  | `references/python.md` |
| Snowflake SQL (including SQL strings embedded in other languages) | `references/snowflake.md` |

## Rules

- Adherence is **strictly required** when a conventions file exists for the language
- Load **only** the file for the language being used (not all files)
- If a task involves multiple languages, load each relevant file separately
- Conventions override general best practices when they conflict
- If unable to find a conventions file that should exist, **STOP and ask** where to find it (don't guess)
