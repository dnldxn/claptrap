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

The data dictionary (`.workflow/data_dictionary.md`) tracks tables you've queried, their purpose, and relevant columns.

### Before querying

**REQUIRED**: You MUST load `.workflow/data_dictionary.md` before executing any SQL query. Do not skip this step.

1. Read the data dictionary file
2. Check if your target table is already documented
3. Use documented column names and descriptions to inform your query

### After querying a new table

Update the data dictionary when you query a table not already documented. Add:
- Fully-qualified table name
- Brief description of what the table contains
- Columns you used (with types and descriptions if known)

### Data dictionary format

```markdown
# Data Dictionary

Tables queried during development. Check here before writing queries.

---

## ANALYTICS_DB.CORE.USERS
Description: User account records with profile and status information.

| Column | Type | Description |
|--------|------|-------------|
| USER_ID | NUMBER | Primary key |
| EMAIL | VARCHAR | User email address |
| CREATED_AT | TIMESTAMP_NTZ | Account creation timestamp |
| STATUS | VARCHAR | Account status (active, suspended, deleted) |

---

## ANALYTICS_DB.EVENTS.PAGE_VIEWS
Description: Raw page view events from web tracking.

| Column | Type | Description |
|--------|------|-------------|
| EVENT_ID | VARCHAR | Unique event identifier |
| USER_ID | NUMBER | FK to USERS table |
| PAGE_URL | VARCHAR | Full URL of viewed page |
| TIMESTAMP | TIMESTAMP_NTZ | Event occurrence time |

---
```

### Format rules

- **Heading**: `## <DATABASE>.<SCHEMA>.<TABLE>` (fully-qualified, uppercase)
- **Description**: One line explaining the table's purpose
- **Columns table**: Include only columns you've actually used
- **Separator**: `---` between entries
- **Ordering**: Alphabetical by fully-qualified name

### Updating existing entries

When you use new columns from a documented table, add them to that table's column list rather than creating a duplicate entry.

## Instructions

1. Use the Snowflake MCP Server tools to execute queries
2. Prefer `LIMIT` clauses when exploring unfamiliar tables
3. Use `DESCRIBE TABLE` or `SHOW COLUMNS IN TABLE` to discover schema before querying
4. For semantic views, use the dedicated semantic view tools (`describe_semantic_view`, `query_semantic_view`, etc.)
