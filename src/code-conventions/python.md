---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions and Guidelines

## Principles
- **Simplicity first:** keep code clear, concise, and elegant.
- **Minimalism:** make surgical changes only; avoid overengineering.
- **Structure:** prefer functions over classes; extract small helpers to reduce duplication.
- **Flow:** avoid deep nesting; return early when possible.
- **Dependencies:** use the standard library first; add third-party packages only if essential and document why.
- **DRY:** Don't Repeat Yourself—extract common functionality into reusable functions.

## Style & Formatting
- Indentation: 4 spaces; line length ≤ 125.
- Naming: `snake_case` (func/vars), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants).
- Imports: group in order → stdlib, third-party, local; remove unused.
- Function variable list should be on one line if it fits within line length; otherwise, break after `(` with each arg on its own line, aligned.
- Keyed function arguments and default values should have a space before and after the equal sign (e.g. `arg = value`)
- Use blank lines to separate logical sections (e.g., between functions, classes, and major code blocks).
- Separate function definitions with two blank lines; methods within a class with one blank line.
- Function Signatures:
    - Single line if it fits within line length; otherwise, break after `(` with each arg on its own line, aligned.
    - Keyed function arguments and default values should have a space before and after the equal sign (e.g. `arg = value`)

## Flow
- Use single-line `if`/`for`/`while`/`else`/`elif`/`try`/`except`/`finally`/`with` when the body is one statement that is less than 75 total characters (e.g., `if not x: return None`, `try: x()`, `except: print('xyz')`, `if code == 0: return True\nelse: return False`).  Otherwise multi-line blocks for longer bodies.
- Use comprehensions where they improve clarity.

## Strings & I/O
- Prefer f-strings; avoid concatenation

## Constants & Config
- Use constants for fixed configuration; use them directly inside functions unless reuse demands parameters.

## Error Handling
- Keep error handling and variable checking to a bare minimum, but still sufficient; explain why in comments when non-obvious.
- Don’t guard required values. Avoid `if var:` for non-optional variables; validate only at external boundaries (prefer EAFP).

## Types
- Prefer inference; avoid deep inline generics.
- Light typing at boundaries (params/returns of public funcs).
- Annotate only public APIs, ambiguous values, or when a short type alias improves clarity.
- Prefer built-ins, e.g., `list[str]`, `dict[str, Any]`.
- Use small `TypeAlias` for repeated shapes.

## Comments
- Comments explain **why**, not what. Prefer readable code over comments.
- Use inline comments sparingly; prefer self-explanatory code.
- Do NOT use docstrings for modules, classes, and functions.
- Function summaries are acceptable for non-trivial functions, but keep them brief and on a single line above the function definition.
- Append comments on the same line for short notes; use full lines for longer explanations.
- Separate primary sections with `#### (x120)\nSection Name\n#### (x120)` headers.

## Data Structures & Performance
- Prefer built-in types (`dict`, `list`, `set`, `tuple`) unless an external one adds real value.
- Avoid premature optimization; only tune if bottlenecks are known.

## Streamlit (if used)
- Streamlit files do not need a `main()` function; code can be at the top level.
- Minimize complicated Streamlit state management (`st.session_state`) as much as possible.
- For UI components, use `width='stretch'` instead of `use_container_width=True`, as the latter is deprecated.
- Keep custom CSS as minimal as possible and scoped to specific components only.
- In st.columns(), call methods on the column objects directly (c1.selectbox(...)) instead of using with c1: blocks, unless a context block is required