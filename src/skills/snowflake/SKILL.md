---
name: snowflake
description: Run Snowflake database SQL queries.
---

# Snowflake Skill

## What this skill does

Execute SQL queries against Snowflake databases using the Snowflake MCP Server.

## When to activate

Trigger this skill when asked to query, retrieve, or explore data in Snowflake.

## Data Dictionary

The data dictionary (`.claptrap/data_dictionary.md`) tracks tables you've queried, their purpose, and relevant columns.

### Before querying

**REQUIRED**: You MUST load `.claptrap/data_dictionary.md` before executing any SQL query. Do not skip this step.

1. Read the data dictionary file
2. Check if your target table is already documented
3. Use documented column names and descriptions to inform your query

### After encountering a new table

Whenever you encounter a table not already in the data dictionary — whether it was explicitly requested, discovered via `SHOW TABLES`, referenced in a join, or needed to satisfy a query — add a **stub entry** immediately. Do this for every new table, not just the ones you end up querying.

A stub entry contains only:
- Fully-qualified table name
- Date the entry was added
- Status of `not profiled`
- Whether the table was accessible (`yes` or `no`)

**Do NOT stop to profile the table for the data dictionary.** Do not add column details, descriptions, or type information to the dictionary entry. A separate profiling agent will fill those in later. Your job is to register the table with a stub and keep moving. You may still run `DESCRIBE TABLE` to understand schema for your own query writing — just don't record the results in the data dictionary.

If a query fails because the table does not exist or you lack permissions, still add the stub entry with `Accessible: no`.

### Data dictionary format

```markdown
# Data Dictionary

Tables queried during development. Check here before writing queries.

---

## ANALYTICS_DB.CORE.USERS
Date Added: 2025-06-15
Status: profiled
Accessible: yes
Description: User account records with profile and status information.

| Column | Type | Description |
|--------|------|-------------|
| USER_ID | NUMBER | Primary key |
| EMAIL | VARCHAR | User email address |
| CREATED_AT | TIMESTAMP_NTZ | Account creation timestamp |
| STATUS | VARCHAR | Account status (active, suspended, deleted) |

---

## ANALYTICS_DB.EVENTS.PAGE_VIEWS
Date Added: 2025-07-02
Status: not profiled
Accessible: yes

---
```

### Format rules

- **Heading**: `## <DATABASE>.<SCHEMA>.<TABLE>` (fully-qualified, uppercase)
- **Date Added**: Date the entry was first created (`YYYY-MM-DD`)
- **Status**: `not profiled` (stub) or `profiled` (fully documented by profiling agent)
- **Accessible**: `yes` if the table was reachable, `no` if access failed or the table was not found
- **Description**: One line explaining the table's purpose (only present when `profiled`)
- **Columns table**: Only present when `profiled`; include only columns that have been used or inspected
- **Separator**: `---` between entries
- **Ordering**: Alphabetical by fully-qualified name

### Stub entry template

When adding a new table, use exactly this format:

```markdown
## <DATABASE>.<SCHEMA>.<TABLE>
Date Added: <YYYY-MM-DD>
Status: not profiled
Accessible: <yes|no>
```

### Updating existing entries

- **Do NOT upgrade a stub to profiled.** Only a profiling agent should change status from `not profiled` to `profiled` and add description/columns.
- When you use new columns from an already-profiled table, add them to that table's column list rather than creating a duplicate entry.
- If a previously accessible table becomes inaccessible, update `Accessible` to `no`.

## Instructions

1. Use the Snowflake MCP Server tools to execute queries
2. `LIMIT` clauses are **REQUIRED** when exploring unfamiliar tables.  Tables may be large and you need to see a sample of the data to understand it.
3. Use `DESCRIBE TABLE` or `SHOW COLUMNS IN TABLE` to discover schema before querying
4. For semantic views, use the dedicated semantic view tools (`describe_semantic_view`, `query_semantic_view`, etc.)
