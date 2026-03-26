# Snowflake Dynamic Tables

Dynamic tables are declarative, automatically-refreshing materializations. Define the result as a SELECT; Snowflake handles refresh scheduling, incremental processing, and dependency orchestration. They replace most Streams + Tasks patterns and Materialized Views for pipeline workloads.

**Primary use cases:** multi-step ELT pipelines (bronze → silver → gold), pre-computed joins/aggregations, SCDs (Type 1 and 2), replacing Stream + Task CDC pipelines, transitioning batch to near-real-time.

## When to Use Dynamic Tables vs Alternatives

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| Multi-step transformation pipeline | **Dynamic Table** | Declarative chaining, auto dependency orchestration, incremental refresh |
| Pre-computed joins across tables | **Dynamic Table** | MVs are single-table only; DTs support full SQL including joins |
| CDC pipeline (inserts/updates/deletes) | **Dynamic Table** | Eliminates MERGE + Stream + Task boilerplate |
| Single-table aggregation with query rewrite | **Materialized View** | Always current; optimizer auto-rewrites base-table queries |
| Alternate clustering on same base table | **Materialized View** | Own clustering key + transparent auto-rewrite |
| Procedural logic / non-deterministic functions | **Streams + Tasks** | DTs require declarative SQL only |
| Exact cron scheduling | **Streams + Tasks** | DTs use TARGET_LAG; Tasks support cron expressions |
| Event-driven triggers / external webhooks | **Streams + Tasks** | Tasks support arbitrary WHEN conditions |
| Full CDC audit trail (per-row action metadata) | **Streams** (+ Tasks/DTs) | Streams expose ACTION, ISUPDATE, ROW_ID |
| One-off data backfill | **Task** (or CTAS) | No need for continuous refresh |

**Rule of thumb:** If the transformation is a SELECT and you want managed refresh, use a DT. For procedural logic, exact scheduling, or external functions, use Tasks.

## Syntax

### CREATE DYNAMIC TABLE

```sql
CREATE [ OR REPLACE ] [ TRANSIENT ] DYNAMIC TABLE [ IF NOT EXISTS ] <name> (
    <col_name> <col_type>
      [ [ WITH ] MASKING POLICY <policy> [ USING ( <col>, ... ) ] ]
      [ [ WITH ] PROJECTION POLICY <policy> ]
      [ [ WITH ] TAG ( <tag> = '<value>' [, ...] ) ]
      [ COMMENT '<string>' ]
    [, ...]
  )
  TARGET_LAG = { '<num> { seconds | minutes | hours | days }' | DOWNSTREAM }
  [ SCHEDULER = { DISABLE | ENABLE } ]
  WAREHOUSE = <warehouse_name>
  [ INITIALIZATION_WAREHOUSE = <warehouse_name> ]
  [ REFRESH_MODE = { AUTO | FULL | INCREMENTAL } ]
  [ INITIALIZE = { ON_CREATE | ON_SCHEDULE } ]
  [ CLUSTER BY ( <expr> [, ...] ) ]
  [ DATA_RETENTION_TIME_IN_DAYS = <integer> ]
  [ MAX_DATA_EXTENSION_TIME_IN_DAYS = <integer> ]
  [ IMMUTABLE WHERE ( <expr> ) ]
  [ BACKFILL FROM ]
  [ EXECUTE AS USER <user_name> [ USE SECONDARY ROLES { ALL | NONE | <role> [, ...] } ] ]
  AS <query>
```

**Key parameters:**

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `TARGET_LAG` | Maximum staleness. `DOWNSTREAM` = refresh only when a downstream DT needs it. Minimum 60s. | Required |
| `WAREHOUSE` | Warehouse for refresh compute. Requires USAGE privilege. | Required |
| `INITIALIZATION_WAREHOUSE` | Larger warehouse for initial/reinitialization refreshes only. | Same as WAREHOUSE |
| `REFRESH_MODE` | `INCREMENTAL` (deltas only), `FULL` (recompute all), `AUTO` (Snowflake picks at creation — immutable after). | `AUTO` |
| `INITIALIZE` | `ON_CREATE` = synchronous populate. `ON_SCHEDULE` = empty until first scheduled refresh. | `ON_CREATE` |
| `SCHEDULER` | `DISABLE` = manual-only refresh via `ALTER ... REFRESH`. Isolation boundary for external orchestrators. | `ENABLE` |
| `TRANSIENT` | No fail-safe storage — lower cost for transitory data. | Permanent |
| `IMMUTABLE WHERE` | Predicate for rows that never change — skipped during refresh. | None |
| `BACKFILL FROM` | Zero-copy import into immutable region. Use with `IMMUTABLE WHERE`. | None |
| `CLUSTER BY` | Clustering key for the DT (Automatic Clustering maintains it). | None |
| `EXECUTE AS USER` | Refresh runs as this user instead of SYSTEM. Enables multi-role access. | SYSTEM |

### ALTER and CREATE OR ALTER

**CREATE OR ALTER** evolves a DT non-destructively. Changes to `TARGET_LAG`, `WAREHOUSE`, `CLUSTER BY`, `IMMUTABLE WHERE`, `COMMENT`, and retention preserve data. Changes to `REFRESH_MODE` or query/column list trigger reinitialization. Add columns at end only; dropping columns used in `IMMUTABLE WHERE` or `CLUSTER BY` is not supported.

**ALTER** supports: `SUSPEND` / `RESUME`, `REFRESH` (manual, works when suspended), `SET TARGET_LAG`, `SET SCHEDULER = DISABLE`, `SET WAREHOUSE`, `SET/UNSET INITIALIZATION_WAREHOUSE`, `CLUSTER BY` / `DROP CLUSTERING KEY`, `SET/UNSET IMMUTABLE WHERE` (unset triggers reinit), `ADD SEARCH OPTIMIZATION`, `RENAME TO`, `SWAP WITH`.

## Examples

### Bronze → silver → gold pipeline

```sql
CREATE OR REPLACE DYNAMIC TABLE silver_orders
  TARGET_LAG = DOWNSTREAM
  WAREHOUSE = transform_wh
  REFRESH_MODE = INCREMENTAL
  AS
    SELECT
      raw:order_id::INT         AS order_id,
      raw:customer_id::INT      AS customer_id,
      raw:product_id::INT       AS product_id,
      raw:quantity::INT         AS quantity,
      raw:price::DECIMAL(10,2)  AS price,
      raw:order_date::DATE      AS order_date
    FROM raw_orders;

CREATE OR REPLACE DYNAMIC TABLE gold_daily_revenue
  TARGET_LAG = '10 minutes'
  WAREHOUSE = transform_wh
  REFRESH_MODE = INCREMENTAL
  AS
    SELECT
      o.order_date,
      p.product_category,
      SUM(o.quantity * o.price)  AS revenue,
      COUNT(*)                   AS order_count
    FROM silver_orders o
    JOIN dim_products p ON o.product_id = p.product_id
    GROUP BY ALL;
```

`silver_orders` uses `DOWNSTREAM` — it refreshes only when `gold_daily_revenue` needs it. The gold layer drives refresh cadence for the entire pipeline.

### Immutability for time-series data

```sql
CREATE OR REPLACE DYNAMIC TABLE metrics_hourly
  TARGET_LAG = '5 minutes'
  WAREHOUSE = transform_wh
  REFRESH_MODE = INCREMENTAL
  IMMUTABLE WHERE (ts < CURRENT_TIMESTAMP() - INTERVAL '2 days')
  AS
    SELECT
      DATE_TRUNC('hour', ts) AS hour,
      metric_name,
      AVG(value) AS avg_value, MAX(value) AS max_value, COUNT(*) AS sample_count
    FROM raw_metrics
    GROUP BY ALL;
```

Rows older than 2 days are immutable — skipped during refresh. The immutable region grows automatically with time-relative predicates.

### External orchestrator mode (dbt integration)

```sql
CREATE OR REPLACE DYNAMIC TABLE stg_orders
  SCHEDULER = DISABLE
  WAREHOUSE = transform_wh
  REFRESH_MODE = INCREMENTAL
  AS SELECT ... FROM raw_orders;

-- dbt or external scheduler triggers refresh:
ALTER DYNAMIC TABLE stg_orders REFRESH;
```

`SCHEDULER = DISABLE` creates an isolation boundary: manual refresh does not cascade upstream or downstream.

## Behavior & Internals

### Refresh Modes

| Mode | Behavior | When to Use |
|------|----------|-------------|
| **INCREMENTAL** | Merges deltas from changed rows. Much cheaper for low-change-rate workloads. | <5% data changes; supported operators; good data locality |
| **FULL** | Re-executes entire query and replaces results. | High change rate; unsupported operators (PIVOT, SAMPLE, subquery ops) |
| **AUTO** | Snowflake picks at creation time — immutable after. | **Avoid in production** — behavior may change across releases. |

**Critical:** Incremental DTs cannot be downstream from full-refresh DTs.

### Operators and Incremental Refresh

**Consistently efficient** (cost ∝ changed rows): `SELECT`, `WHERE`, `FROM`, `UNION ALL`, `LATERAL FLATTEN`, `QUALIFY ROW_NUMBER/RANK/DENSE_RANK ... = 1` (optimized fast path).

**Locality-sensitive** (cost depends on clustering/change distribution): `INNER JOIN`, `OUTER JOIN`, `GROUP BY`, `DISTINCT`, window functions (`OVER`). Best when <5% of keys change. Cluster source tables by join/group/partition keys.

**Not supported** (force FULL): PIVOT/UNPIVOT, SAMPLE, set operators other than UNION ALL, WITH RECURSIVE, subquery operators (EXISTS, NOT EXISTS, IN subquery), sequence functions, VOLATILE UDFs, external functions, ANY_VALUE.

Always include `PARTITION BY` in window functions — without it, every refresh recomputes the entire window.

### TARGET_LAG Mechanics

- Measured relative to **root** DTs in the graph, not direct upstream.
- Snowflake schedules refreshes *before* the deadline — actual intervals are often shorter than specified.
- TARGET_LAG is a **target, not a guarantee**. Lag may exceed target under load.
- Minimum 60 seconds. Cannot be shorter than upstream DTs' lag.
- If all DTs in a pipeline use `DOWNSTREAM`, nothing refreshes. Set a time-based lag on the most-downstream DT.

### Snapshot Isolation

Refreshes Time Travel all upstream dependencies to the same timestamp — guaranteeing pipeline-wide consistency. **Caveat:** Ad-hoc `SELECT` queries joining multiple DTs are *not* snapshot-isolated; each DT commits independently. Build a downstream DT for cross-DT consistency.

### Initialization and Reinitialization

`ON_CREATE` (default) populates synchronously; `ON_SCHEDULE` defers to first scheduled refresh. Reinitialization triggers: base table recreation (even identical schema), masking/row-access policy changes on base tables (incremental DTs), schema changes via `SELECT *`, `REFRESH_MODE` changes, replication failover. Use `INITIALIZATION_WAREHOUSE` to run (re)init on a larger warehouse.

### Cost Model

| Component | Details |
|-----------|---------|
| **Warehouse compute** | Credits per refresh. Primary lever — controlled by TARGET_LAG frequency and warehouse size. |
| **Cloud Services** | Change detection on base tables. If no changes, no warehouse credits consumed. |
| **Storage** | Result set + Time Travel + Fail-safe (unless TRANSIENT). Incremental DTs add per-row metadata overhead. |

If source data hasn't changed, Cloud Services detects this and skips the warehouse refresh — near-zero cost for quiescent pipelines. Snowflake auto-suspends DTs on upstream suspension, cloning, or errors; check `scheduling_state` via `SHOW DYNAMIC TABLES`.

## Limitations & Gotchas

- **Unsupported sources:** Cannot read from directory tables, external tables, streams, or materialized views. Can read from standard tables, views (with caveats), other DTs, and Iceberg tables.
- **View restriction:** Cannot create a DT reading from a view that queries another DT.
- **No DML:** Cannot INSERT, UPDATE, DELETE, MERGE, or TRUNCATE a DT.
- **No temporary DTs.** Only permanent and transient.
- **REFRESH_MODE is immutable** after creation. Use `CREATE OR REPLACE` to change it.
- **AUTO mode risk:** If AUTO picks INCREMENTAL and a later upstream change makes it unsupported, refresh fails. Always set INCREMENTAL or FULL explicitly in production.
- **Incremental → full constraint:** Incremental DTs cannot be downstream from full-refresh DTs.
- **SELECT * fragility:** Schema changes on base tables break the DT. Always use explicit column lists.
- **Account limit:** 50,000 DTs per account.
- **Staleness:** If not refreshed within `MAX_DATA_EXTENSION_TIME_IN_DAYS`, the DT goes stale and must be recreated.
- **Streams on DTs:** Only on incremental-mode DTs. Only standard (delta) streams — no append-only or insert-only.
- **Non-deterministic functions:** `CURRENT_USER()` not supported. `CURRENT_TIMESTAMP` only in WHERE/HAVING/QUALIFY, not SELECT.
- **QAS not supported** for DT refreshes.
- **Aggregation/projection policies** on base tables prevent DT creation.

## Best Practices

### Pipeline Design
- Use `DOWNSTREAM` for intermediate layers; set time-based TARGET_LAG only on consumer-facing DTs.
- Break complex transformations into multiple DTs for debuggability, mixed refresh modes, and better data locality.
- Apply filters and dedup early — reduce row volume for downstream DTs.

### Incremental Optimization
- Prefer INNER JOIN over OUTER JOIN. Verify referential integrity to eliminate outer joins.
- Use `QUALIFY ROW_NUMBER() = 1` instead of `DISTINCT` — it has an optimized incremental fast path.
- Materialize compound GROUP BY expressions: split `DATE_TRUNC('minute', ts)` into a compute DT + a grouping DT.
- Always use `PARTITION BY` in window functions.
- Cluster source tables by join/GROUP BY/PARTITION BY keys. Target <5% of keys changing between refreshes.

### Cost Control
- Set TARGET_LAG as loose as the business allows (1h = ~24 refreshes/day; 1min = ~1440/day).
- Use TRANSIENT for transitory data. Use INITIALIZATION_WAREHOUSE for large initial loads.
- Use IMMUTABLE WHERE for time-series data — historical rows are skipped automatically.
- Isolate DT refresh costs on dedicated warehouses during baselining.
- Suspend full-refresh DTs outside business hours when freshness isn't needed 24/7.

### Anti-Patterns
- **AUTO in production** — unpredictable behavior across releases.
- **SELECT \*** — schema changes silently break the DT.
- **Monolithic single-DT pipeline** — poor debuggability, no mixed refresh modes.
- **TARGET_LAG < 1 min with expensive queries** — refresh can't complete in time, causing lag overshoot.
- **DOWNSTREAM on the final consumer DT** — nothing triggers refresh; the pipeline never runs.

## Monitoring

```sql
-- Refresh history (rows, timing, mode)
SELECT name, state, refresh_trigger, refresh_mode,
       data_timestamp, refresh_start_time, refresh_end_time,
       statistics:numInsertedRows::NUMBER AS rows_inserted,
       statistics:numDeletedRows::NUMBER  AS rows_deleted
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME => 'my_db.my_schema.gold_daily_revenue',
  DATA_TIMESTAMP_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
ORDER BY refresh_start_time DESC;

-- Pipeline graph and scheduling states
SELECT name, qualified_name, target_lag, warehouse, scheduling_state
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_GRAPH_HISTORY())
WHERE valid_from > DATEADD('day', -1, CURRENT_TIMESTAMP())
ORDER BY qualified_name;
```

If `refresh_mode` shows FULL when you expected INCREMENTAL, the query uses an unsupported operator or AUTO chose full at creation.

## Security & Privileges

| Operation | Required Privileges |
|-----------|-------------------|
| CREATE | `CREATE DYNAMIC TABLE` on schema, `SELECT` on sources, `USAGE` on database, schema, warehouse |
| SELECT | `SELECT` on the DT, `USAGE` on database and schema |
| ALTER (operate) | `OPERATE` on the DT (suspend, resume, refresh, set warehouse/lag) |
| ALTER (own) | `OWNERSHIP` (rename, swap, clustering, policies, all SET operations) |
| DROP | `OWNERSHIP` on the DT |
| MONITOR | `MONITOR` on the DT (metadata, refresh history, graph history) |

The owner role must have USAGE on the warehouse. If ownership is transferred, verify warehouse access or refreshes fail silently.

## Documentation & Resources

- [Dynamic Tables Overview](https://docs.snowflake.com/en/user-guide/dynamic-tables-about) — Concepts, use cases, and refresh behavior
- [CREATE DYNAMIC TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table) — Full syntax reference with all parameters
- [Dynamic Tables vs Streams & Tasks](https://docs.snowflake.com/en/user-guide/dynamic-tables-tasks-create) — Decision guide for choosing between approaches
