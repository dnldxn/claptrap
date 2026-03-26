---
name: snowflake
description: "Deep-dive Snowflake reference loader for topic-specific platform knowledge. Use whenever working with Snowflake features like Dynamic Tables, Streams, Tasks, Iceberg Tables, Data Sharing, Hybrid Tables, Cortex AI, Alerts, Notebooks, or any other Snowflake-specific capability where you need authoritative guidance beyond general SQL knowledge. Triggers on Snowflake DDL/DML patterns, Snowflake object types, or when the user asks about Snowflake platform behavior, best practices, limitations, or migration patterns."
---

# Snowflake Reference Loader

Load topic-specific Snowflake reference documents to get deep, curated knowledge about the platform feature you're working with. Each reference file compiles information from official Snowflake documentation, community best practices, and third-party sources into a single authoritative guide.

## When to Use

This skill is for **deep platform knowledge** about specific Snowflake features. Use it when you need to understand behavior, limitations, syntax nuances, or best practices that go beyond what you'd know from general SQL experience.

Examples of when to load a reference:
- Writing or debugging a Dynamic Table definition
- Setting up Streams and Tasks for CDC pipelines
- Configuring Iceberg Tables or external tables
- Working with Cortex AI functions
- Designing data sharing or replication
- Troubleshooting Snowflake-specific behavior

Do NOT use this skill for:
- Basic SQL that works the same across any database
- General Snowflake connection/authentication setup
- dbt-on-Snowflake workflows (use the `snowflake-dbt` skill instead)

## How to Load References

1. Identify the Snowflake feature central to the current task
2. Find the matching reference file in the topic index below
3. Load **only** the reference(s) relevant to the work at hand -- do not load all files
4. If a task spans multiple features, load each relevant reference separately

**Announce at start:** "Loading the [Topic] Snowflake reference from [File]."

## Topic Index

| Topic | File | Covers | Last Updated |
|-------|------|--------|--------------|
| Optimization: Overview | `references/optimization-overview.md` | Cost model, optimization decision framework, diagnostic toolkit (ACCOUNT_USAGE views, system functions, query profile signals), standard diagnostic queries, routing guide to sub-topics | 2026-03-26 |
| Optimization: Query Performance | `references/optimization-query-performance.md` | Slow query identification (QUERY_HISTORY, AGGREGATE_QUERY_HISTORY, query tags), query profile diagnosis, query tuning techniques (filter pushdown, spill reduction, join optimization, FLATTEN optimization, compilation time), caching (result/metadata/warehouse), common anti-patterns | 2026-03-26 |
| Optimization: Compute & Warehouses | `references/optimization-compute.md` | Warehouse sizing & right-sizing, Gen 1 vs Gen 2 (differences, when to use each, identifying candidates, migration), multi-cluster warehouses, auto-suspend & auto-resume tuning, workload isolation, resource monitors | 2026-03-26 |
| Optimization: Data Access | `references/optimization-data-access.md` | Feature selection matrix, clustering keys (when/what/monitoring/cost), SOS (predicates, cost estimation, column-level enablement), QAS (candidate identification, scale factor tuning, cost monitoring), Materialized Views (optimization patterns, automatic query rewrite, cost monitoring), Dynamic Tables (TARGET_LAG tuning, incremental vs full refresh, immutability constraints, cost monitoring), feature cost comparison | 2026-03-26 |
| Streams | `references/streams.md` | CREATE/ALTER/DROP STREAM, SHOW/DESCRIBE STREAMS, standard vs append-only vs insert-only types, stream metadata columns (ACTION, ISUPDATE, ROW_ID), offset mechanics & consumption, repeatable-read isolation, SHOW_INITIAL_ROWS, staleness & data retention extension, SYSTEM$STREAM_HAS_DATA, CHANGES clause, streams on tables/views/dynamic tables/external tables/directory tables/Iceberg tables/event tables, view stream requirements & join behavior, security & privileges, cost model | 2026-03-26 |
| Dynamic Tables | `references/dynamic-tables.md` | When to use DTs vs Tasks/MVs/Streams, CREATE/ALTER/DROP syntax, TARGET_LAG (time-based & DOWNSTREAM), REFRESH_MODE (INCREMENTAL/FULL/AUTO), SCHEDULER (ENABLE/DISABLE for external orchestrators), INITIALIZATION_WAREHOUSE, IMMUTABLE WHERE & BACKFILL, CREATE OR ALTER, incremental refresh operator support & optimization (joins, GROUP BY, window functions, QUALIFY), snapshot isolation, staleness, cost model (compute + cloud services + storage), monitoring (refresh history, lag, graph), pipeline design best practices, anti-patterns, security & privileges | 2026-03-26 |
| Tasks | `references/tasks.md` | CREATE/ALTER/DROP/EXECUTE TASK, scheduling (cron & interval), triggered tasks (stream-driven), serverless vs user-managed compute, task graphs (DAGs), finalizer tasks, WHEN conditions, overlap policies, CONFIG & return-value passing, retry & auto-suspend, monitoring views, security & privileges, cost control | 2026-03-26 |
| Permissions & RBAC | `references/permissions.md` | Access control framework (DAC/RBAC/UBAC), securable object hierarchy, privilege categories (high-level), OWNERSHIP, system-defined roles (ACCOUNTADMIN, SECURITYADMIN, USERADMIN, SYSADMIN, PUBLIC), custom roles, database roles, role hierarchy & inheritance, access-role vs functional-role pattern, grant management (GRANT/REVOKE, future grants, managed access schemas), auditing (SHOW GRANTS, GRANTS_TO_ROLES, GRANTS_TO_USERS, APPLICABLE_ROLES, ENABLED_ROLES), recursive role-chain walker query, best practices | 2026-03-26 |
| dbt Projects | `references/dbt-projects.md` | dbt Core overview, project structure, profiles.yml & dbt_project.yml configuration, SQL commands (CREATE/ALTER/EXECUTE/DROP/SHOW DBT PROJECT), Snowflake CLI (`snow dbt deploy/execute/list/describe/drop`), Git integration setup, dependency management (external access integration, cross-project deps), scheduling with Tasks (run→test DAGs), CI/CD with GitHub Actions, monitoring & observability (logging, tracing, artifact access), schema customization, access control (RBAC privileges), semantic views, supported dbt Core versions, best practices | 2026-03-26 |

<!--
  ==========================================================================
  MAINTAINING REFERENCES
  ==========================================================================

  RESEARCH SOURCES
  ----------------
  Gather information from these sources, in rough priority order:

  1. Official Snowflake documentation (docs.snowflake.com)
     - SQL reference pages for the feature's DDL/DML
     - "Using" / conceptual guides that explain behavior and design intent
     - Release notes and "what's new" entries for recent changes
  2. Snowflake Community & Knowledge Base
     - community.snowflake.com posts with verified answers
     - Snowflake support knowledge base articles
  3. Snowflake engineering blogs (snowflake.com/blog, snowflake.com/engineering-blog)
  4. Third-party deep dives and tutorials
     - Medium / Towards Data Science articles by Snowflake practitioners
     - Blog posts from consulting firms (e.g., Hashmap, phData, Snowflake Solutions)
     - Conference talks and recorded demos (Snowflake Summit, Data Council)
  5. Stack Overflow & GitHub
     - Highly-voted answers tagged [snowflake-cloud-data-platform]
     - Open issues or discussions in snowflake-labs repos for known bugs/workarounds

  For sources 3-5, only use material published within the last 3 months. Snowflake evolves fast and older third-party content often describes outdated behavior. Official docs (1) and Snowflake Community/KB (2) are exempt since Snowflake maintains them.

  When sources conflict, prefer official docs. When official docs are silent on a practical matter (performance tuning, real-world gotchas), lean on well-regarded community sources and note the origin.

  COMPILING INTO A REFERENCE FILE
  -------------------------------
  The goal is a single, self-contained document an agent can read and immediately apply -- not a link dump or copy-paste of raw docs. Follow this process:

  1. Collect raw material from the sources above
  2. Deduplicate -- most sources repeat the same syntax; keep one canonical version
  3. Organize by how a practitioner thinks about the feature:
     a. What it is and when to use it (brief conceptual overview)
     b. How to create/configure it (syntax + annotated examples)
     c. How it behaves at runtime (refresh mechanics, ordering, costs, etc.)
     d. Limitations, gotchas, and common mistakes
     e. Best practices and anti-patterns
     f. Version/preview status and feature dependencies
  4. Synthesize, don't quote -- rewrite in a consistent voice. Use direct, imperative language. Cite the source inline only when credibility matters (e.g., "per Snowflake release notes 2025-03") or the info is surprising.
  5. Include practical examples that show real-world usage, not just minimal syntax stubs. Prefer examples that demonstrate gotchas or non-obvious behavior.
  6. Omit information that is obvious to anyone who knows SQL (e.g., don't explain what a SELECT statement does) -- focus on what's Snowflake-specific.

  REFERENCE FILE STRUCTURE
  ------------------------
  Every reference file should follow this general layout:

    # [Feature Name]
    Brief overview: what it is, primary use cases, when to choose it.

    ## Syntax
    DDL/DML with all clauses. Annotate non-obvious parameters.

    ## Examples
    Practical, real-world examples (not just hello-world).

    ## Behavior & Internals
    How it works at runtime -- refresh cadence, costs, ordering, etc.

    ## Limitations & Gotchas
    Things that surprise people. Known bugs or preview caveats.

    ## Best Practices
    Patterns that work well. Anti-patterns to avoid and why.
    
    ## Documentation & Resources (Optional)
    Links to official docs, community posts, and other sources used.  Use a max of 3 sources, ideally less.  The agent will need to read the reference end-to-end, so don't overload it with links -- only include the most essential ones that provide unique information not fully captured in the reference.

  SIZE TARGETS
  ------------
  Target 200-400 lines per reference. If a topic grows beyond 500 lines, split it into sub-topics (e.g., streams-cdc.md, streams-append-only.md).

  ==========================================================================
  ADDING A NEW TOPIC
  ==========================================================================

  1. Research the topic using the sources listed above
  2. Compile findings into a reference file following the structure above
  3. Save as references/<topic>.md (kebab-case, e.g., references/dynamic-tables.md)
  4. Add a row to the Topic Index table with Last Updated set to today's date (YYYY-MM-DD)
  5. Verify the file reads well end-to-end -- an agent loading it for the first time should be able to work with the feature without further research

  ==========================================================================
  UPDATING AN EXISTING TOPIC
  ==========================================================================

  1. Read the existing reference file to understand current coverage
  2. Research what has changed -- check Snowflake release notes, updated docs, and community posts for new behavior, lifted limitations, or deprecated syntax
  3. Update the reference file in place:
     - Add new sections or examples for added capabilities
     - Correct any information that is now outdated or wrong
     - Remove caveats for limitations that have been lifted
     - Keep the size target as described above for the final document
  4. Keep the established structure and tone intact -- don't reorganize unless the topic has grown enough to warrant a split
  5. Update the "Covers" column in the Topic Index if scope has changed
  6. Set "Last Updated" in the Topic Index to today's date (YYYY-MM-DD)
-->


## Snowflake SQL Shortcuts

Snowflake extends ANSI SQL with several conveniences. **Use these by default** when writing Snowflake queries.

**Trailing commas in SELECT** — A trailing comma after the last column is valid: `SELECT col_a, col_b, FROM ...`. Makes reordering and commenting out columns easier.

**EXCLUDE** — Drop columns from `SELECT *` without listing every other one: `SELECT * EXCLUDE (created_at, updated_at) FROM ...`. Also supports `RENAME`, `REPLACE`, and `ILIKE` after `*`.

**Column alias reuse** — Aliases defined in SELECT (`expr AS alias`) can be referenced in `WHERE`, `JOIN`, `GROUP BY`, `ORDER BY`, and other SELECT expressions in the same query. Use this to avoid repeating complex expressions: `SELECT revenue - cost AS profit, profit / revenue AS margin FROM ...`.

**GROUP BY ALL** — Almost always prefer `GROUP BY ALL` over listing columns. Snowflake automatically groups by every non-aggregate SELECT expression: `SELECT region, product, SUM(amount) FROM sales GROUP BY ALL`.


## Rules

- Load **only** the reference(s) matching the current task -- never bulk-load all files
- If multiple features are involved, load each relevant reference individually
- References are curated compilations, not raw docs -- treat them as authoritative for this project
- If a reference file should exist for a topic but doesn't, **say so** and work from your general knowledge while noting the gap
- When a reference conflicts with your training data, prefer the reference (it may reflect newer behavior or project-specific conventions)
- If unsure which reference applies, briefly describe the available topics and ask which to load
