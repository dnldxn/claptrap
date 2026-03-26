# dbt Projects on Snowflake

dbt (data build tool) Core is an open-source SQL transformation framework. Snowflake treats dbt projects as **first-class schema-level objects** — you create, version, execute, and schedule them entirely within Snowflake, without an external dbt Cloud account or orchestrator. Two interaction paths: **SQL commands** (CREATE/ALTER/EXECUTE/DROP DBT PROJECT) and **Snowflake CLI** (`snow dbt`).

**When to use dbt on Snowflake vs alternatives:**

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| SQL-based ELT with testing, docs, and team collaboration | **dbt on Snowflake** | Declarative models, built-in testing, lineage DAG, Git integration |
| Continuous auto-refreshing materializations | **Dynamic Tables** | Fully managed refresh, no scheduling needed |
| Procedural logic (stored procs, external functions) | **Streams + Tasks** | dbt requires declarative SQL |
| Simple single-table aggregation | **Materialized Views** | Auto-rewrite, always current |

## dbt Core Concepts (Brief)

dbt operates on the "T" in ELT — raw data is loaded first, then dbt transforms it via SQL SELECT **models**. Key primitives: **models** (SQL files materialized as tables/views), **sources** (YAML declarations of raw tables), **tests** (data quality assertions), **seeds** (CSV lookup tables), **snapshots** (SCD Type 2), **macros** (Jinja SQL functions), **packages** (reusable modules via `dbt deps`). The **DAG** is resolved from `{{ ref() }}` and `{{ source() }}` calls.

## Configuration

### profiles.yml

When running natively on Snowflake, `account` and `user` are injected. **Passwords are not supported — they cause deployment failures.** The target schema must pre-exist (Snowflake dbt does NOT auto-create schemas).

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: ''                # Ignored — Snowflake injects
      user: ''                   # Ignored — Snowflake injects
      role: TRANSFORM_ROLE
      database: ANALYTICS_DB
      schema: DEV
      warehouse: TRANSFORM_WH
    prod:
      type: snowflake
      account: ''
      user: ''
      role: TRANSFORM_ROLE
      database: ANALYTICS_DB
      schema: PROD
      warehouse: TRANSFORM_WH
```

### dbt_project.yml

```yaml
name: 'my_project'
version: '1.0.0'
profile: 'my_project'          # Must match profiles.yml
model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
models:
  my_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

## SQL Commands

### CREATE DBT PROJECT

```sql
CREATE [ OR REPLACE ] DBT PROJECT [ IF NOT EXISTS ] <name>
  [ FROM '<source_location>' ]
  [ COMMENT = '<string>' ]
  [ DBT_VERSION = <version> ]
  [ DEFAULT_TARGET = <target> ]
  [ EXTERNAL_ACCESS_INTEGRATIONS = ( <integration> [ , ... ] ) ]
```

**Source locations:** Git stage (`'@db.schema.git_stage/branches/main/path'`), existing project (`'snow://dbt/db.schema.project/versions/last'`), internal stage (`'@db.schema.stage/path'`), workspace (`'snow://workspace/user$.public."name"/versions/live/path'`). Requires `CREATE DBT PROJECT` on the schema.

### ALTER DBT PROJECT

```sql
ALTER DBT PROJECT <name> ADD VERSION [<alias>] FROM '<source>'   -- auto-increments version$N
ALTER DBT PROJECT <name> SET [DEFAULT_TARGET=...] [DBT_VERSION=...] [EXTERNAL_ACCESS_INTEGRATIONS=(...)] [COMMENT='...']
ALTER DBT PROJECT <name> RENAME TO <new_name>                    -- requires OWNERSHIP
```

### EXECUTE DBT PROJECT

```sql
EXECUTE DBT PROJECT <name> [ ARGS = '<command> [--option value ...]' ] [ DBT_VERSION = '<ver>' ]
-- From workspace:
EXECUTE DBT PROJECT [FROM WORKSPACE <ws>] [ARGS='...'] [PROJECT_ROOT='<subdir>']
```

Returns: `Success` (bool), `EXCEPTION`, `STDOUT`, `OUTPUT_ARCHIVE_URL`. Requires `USAGE` on the project. The role in `profiles.yml` must have privileges on warehouse, database, schema, and referenced objects.

### Other Commands

```sql
DESCRIBE DBT PROJECT <name>;
DROP DBT PROJECT [ IF EXISTS ] <name>;                            -- requires OWNERSHIP
SHOW DBT PROJECTS [LIKE '<pattern>'] [IN {ACCOUNT|DATABASE|SCHEMA}];
SHOW VERSIONS IN DBT PROJECT <name>;
```

## Snowflake CLI (`snow dbt`)

Requires CLI version ≥ 3.13.0. Install: `brew install snowflake-cli` or `pip install snowflake-cli`.

```bash
snow dbt deploy <name> [--source DIR] [--profiles-dir DIR] [--default-target T] [--dbt-version V] [--external-access-integration I] [--force]
snow dbt execute <name> <command> [--select MODEL+] [--target T]   # run, test, compile, deps, seed, snapshot, build, etc.
snow dbt execute --run-async <name> run                             # non-blocking
snow dbt list [--like PATTERN] [--in database DB]
snow dbt describe <name>
snow dbt drop <name>
```

**Supported commands:** `build`, `compile`, `deps`, `list`, `parse`, `retry`, `run`, `run-operation`, `seed`, `show`, `snapshot`, `test`

## Examples

### Git-sourced Project

```sql
-- Git integration setup
CREATE OR REPLACE SECRET my_db.integrations.git_secret TYPE=password USERNAME='user' PASSWORD='ghp_token';
CREATE OR REPLACE API INTEGRATION git_api API_PROVIDER=git_https_api
  API_ALLOWED_PREFIXES=('https://github.com/my-org') ALLOWED_AUTHENTICATION_SECRETS=(my_db.integrations.git_secret) ENABLED=TRUE;

-- Create, run, test
CREATE DBT PROJECT my_db.dbt.sales FROM '@my_db.integrations.git_stage/branches/main/project'
  DEFAULT_TARGET='prod' EXTERNAL_ACCESS_INTEGRATIONS=('dbt_ext_access');
EXECUTE DBT PROJECT my_db.dbt.sales ARGS='run --target prod';
EXECUTE DBT PROJECT my_db.dbt.sales ARGS='test --target prod';

-- Update from Git
ALTER GIT REPOSITORY my_db.integrations.git_stage FETCH;
ALTER DBT PROJECT my_db.dbt.sales ADD VERSION FROM '@my_db.integrations.git_stage/branches/main/project';
```

### Local Dev Workflow (CLI)

```bash
snow dbt deploy my_project --source . --default-target dev
snow dbt execute my_project deps
snow dbt execute my_project compile         # validate SQL
snow dbt execute my_project run --target dev
snow dbt execute my_project test --target dev
snow dbt execute my_project run --target prod   # promote
```

### Scheduling with Tasks (Run → Test DAG)

```sql
CREATE OR ALTER TASK my_db.dbt.run_task WAREHOUSE=TRANSFORM_WH SCHEDULE='6 hours'
  AS EXECUTE DBT PROJECT my_db.dbt.sales ARGS='run --target prod';

CREATE OR ALTER TASK my_db.dbt.test_task WAREHOUSE=TRANSFORM_WH AFTER my_db.dbt.run_task
  AS EXECUTE DBT PROJECT my_db.dbt.sales ARGS='test --target prod';

ALTER TASK my_db.dbt.test_task RESUME;
ALTER TASK my_db.dbt.run_task RESUME;
```

**Note:** Serverless tasks cannot run dbt projects — must use a user-managed warehouse. Tasks must reside in the same db/schema as the dbt project object.

## Dependencies

Packages in `packages.yml` install into `dbt_packages/` via `dbt deps`. Two approaches:
1. **In-Snowflake** — run `dbt deps` in a Workspace before deploying. Requires an external access integration.
2. **Outside Snowflake** — run `dbt deps` locally or in CI, then deploy the full project with `snow dbt deploy`. No external access needed.

When you deploy with an `EXTERNAL_ACCESS_INTEGRATIONS`, Snowflake auto-runs `dbt deps` during compilation.

```sql
CREATE OR REPLACE NETWORK RULE dbt_net_rule MODE=EGRESS TYPE=HOST_PORT VALUE_LIST=('hub.getdbt.com','codeload.github.com');
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION dbt_ext_access ALLOWED_NETWORK_RULES=(dbt_net_rule) ENABLED=TRUE;
```

**Cross-project deps:** only same-folder references supported. Copy the dependency into a subfolder and use `local: local_packages/other_project` in `packages.yml`.

## Monitoring & Observability

Enable on the dbt schema: `ALTER SCHEMA SET LOG_LEVEL='INFO', TRACE_LEVEL='ALWAYS', METRIC_LEVEL='ALL';`

**Snowsight:** Navigate to **Transformation → dbt Projects** for run history, status, stdout, and OpenTelemetry traces.

**Programmatic access:**

| Function | Returns |
|----------|---------|
| `SYSTEM$GET_DBT_LOG(query_id)` | Text log output |
| `SYSTEM$LOCATE_DBT_ARTIFACTS(query_id)` | Folder path to `manifest.json`, compiled SQL, logs |
| `SYSTEM$LOCATE_DBT_ARCHIVE(query_id)` | ZIP file URL |
| `DBT_PROJECT_EXECUTION_HISTORY()` | Table function of execution history |

Monitoring requires `GRANT MONITOR ON DBT PROJECT <name> TO ROLE <role>;`

## Access Control

```sql
GRANT CREATE DBT PROJECT ON SCHEMA my_db.my_schema TO ROLE deployer;   -- create projects
GRANT OWNERSHIP ON DBT PROJECT my_project TO ROLE deployer;             -- alter, drop
GRANT USAGE ON DBT PROJECT my_project TO ROLE runner;                   -- execute, list files
GRANT MONITOR ON DBT PROJECT my_project TO ROLE viewer;                 -- Snowsight monitoring
```

The dbt command runs with the `role` from `profiles.yml`, further restricted to the calling user's grants.

## Schema Customization

dbt combines target and custom schemas: `<target_schema>_<custom_schema>`. Override `generate_schema_name` in `macros/` to change this (e.g., use only the custom schema in prod).

## CI/CD (GitHub Actions)

```yaml
steps:
  - uses: actions/checkout@v4
  - run: pip install snowflake-cli
  - run: |
      mkdir -p ~/.snowflake && cat > ~/.snowflake/config.toml <<EOF
      [connections.default]
      account = "${{ secrets.SF_ACCOUNT }}"
      user = "${{ secrets.SF_USER }}"
      password = "${{ secrets.SF_PASSWORD }}"
      role = "TRANSFORM_ROLE"
      warehouse = "TRANSFORM_WH"
      database = "ANALYTICS_DB"
      schema = "DBT_SCHEMA"
      EOF
  - run: snow dbt deploy my_project --source ./dbt --force
  - run: snow dbt execute my_project run --target prod
  - run: snow dbt execute my_project test --target prod
```

No Git repository object in Snowflake required — just your Git server and Snowflake CLI.

## Limitations & Gotchas

- **Target schema must pre-exist** — Snowflake dbt will not auto-create it
- **No passwords in profiles.yml** — Snowflake injects auth; passwords cause failures
- **Serverless tasks unsupported** — must use a user-managed warehouse
- **Versions are immutable** — `dbt deps` against a deployed object has no effect; add a new version
- **Cross-project refs must be same-folder** — `local: ../other` not supported
- **`dbt deps` needs external access** — network rule + integration for `hub.getdbt.com` and `codeload.github.com`
- **Tasks must be in same db/schema** as the dbt project object
- **Schema combining** — custom schema produces `<target>_<custom>`, not just `<custom>`; override `generate_schema_name` if needed
- **Trial accounts** — external access integrations for `dbt deps` not supported

## Best Practices

- **Separate dev/prod with targets** — different schemas and warehouses; promote via `--target prod`
- **Pin dbt version** — `DBT_VERSION = '1.10.15'` for reproducible runs
- **Dedicated warehouses** — isolate dbt compute for cost monitoring
- **Run → Test DAG** — chain tasks to catch quality issues before consumers see bad data
- **Install deps outside Snowflake** for prod — deploy full `dbt_packages/` to avoid external network dependency
- **Enable monitoring** — set `LOG_LEVEL`, `TRACE_LEVEL`, `METRIC_LEVEL` on the dbt schema
- **Use `--select model+`** — run only changed models and downstream dependencies
- **CI/CD with `snow dbt deploy --force`** — automate deployment on merge

## Supported dbt Core Versions

| Version | Snowflake | dbt Labs |
|---------|-----------|----------|
| 1.10.15 | Active | Critical support until Jun 2026 |
| 1.9.4 | Active | Deprecated |

```sql
SELECT SYSTEM$SUPPORTED_DBT_VERSIONS();                          -- check versions
ALTER DBT PROJECT my_project SET DBT_VERSION = '1.10.15';        -- pin version
EXECUTE DBT PROJECT my_project DBT_VERSION = '1.10.15';          -- override at runtime
```

Deprecated dbt Labs versions remain functional on Snowflake until explicitly decommissioned.

## Semantic Views

The [`dbt_semantic_view`](https://github.com/Snowflake-Labs/dbt_semantic_view) package (add `Snowflake-Labs/dbt_semantic_view` v1.0.3 to `packages.yml`) enables `{{ config(materialized='semantic_view') }}` models that define TABLES, RELATIONSHIPS, FACTS, DIMENSIONS, and METRICS — usable with Cortex Analyst and other Snowflake applications.

## Documentation & Resources

- [dbt Projects on Snowflake — Official Docs](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake)
- [Getting Started Guide](https://www.snowflake.com/en/developers/guides/dbt-projects-on-snowflake/)
- [SQL Reference: CREATE](https://docs.snowflake.com/en/sql-reference/sql/create-dbt-project) · [ALTER](https://docs.snowflake.com/en/sql-reference/sql/alter-dbt-project) · [EXECUTE](https://docs.snowflake.com/en/sql-reference/sql/execute-dbt-project) · [SHOW](https://docs.snowflake.com/en/sql-reference/sql/show-dbt-projects) · [DROP](https://docs.snowflake.com/en/sql-reference/sql/drop-dbt-project)
- [Deploy](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-deploy) · [Schedule](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-schedule-project-execution) · [Monitor](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-monitoring-observability) · [Dependencies](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-dependencies) · [Access Control](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-access-control) · [Schema](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-schema-customization) · [Versions](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-dbt-core-versions)
- [Snowflake CLI dbt Commands](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/dbt-commands/overview)
- [dbt Core Docs](https://docs.getdbt.com/) · [dbt Packages Hub](https://hub.getdbt.com/)
- [Getting Started Lab Repo](https://github.com/Snowflake-Labs/getting-started-with-dbt-on-snowflake)
