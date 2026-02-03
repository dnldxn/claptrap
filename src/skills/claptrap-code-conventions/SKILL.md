---
name: "claptrap-code-conventions"
description: Load project-specific code style guidelines for a given language. Use before writing or reviewing code to ensure adherence to project standards.
---

# Code Conventions Skill

Load and adhere to the appropriate code style/conventions file for the language being used.

## Usage

1. Determine the primary language for the current task
2. Read the corresponding file from `.claptrap/code-conventions/<language>.md`
3. Print the file name and location before applying (e.g., "Using conventions from `.claptrap/code-conventions/python.md`")
4. Apply those conventions when writing or reviewing code

## Language Mapping

| Language | File |
|----------|------|
| Python | `python.md` |
| Snowflake SQL (including SQL embedded in other languages) | `snowflake.md` |

## Rules

- Adherence is **strictly required** when a conventions file exists for the language
- Load **only** the file for the language being used (not all files)
- If a task involves multiple languages, load each relevant file separately
- Conventions override general best practices when they conflict
- If unable to find a conventions file that should exist, **STOP and ask** where to find it (don't guess)
