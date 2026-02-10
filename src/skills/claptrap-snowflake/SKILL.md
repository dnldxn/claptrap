---
name: claptrap-snowflake
description: >
  Snowflake query performance optimization, tuning, and diagnostics. Use when writing,
  reviewing, or optimizing Snowflake SQL queries, diagnosing slow queries, choosing warehouse
  sizes, evaluating clustering keys, or improving query execution plans. Also use when asked
  about Snowflake performance best practices, partition pruning, caching, join optimization,
  or cost reduction strategies.
---

# Snowflake Performance Optimization

Systematic guide for diagnosing and fixing Snowflake performance issues.

## Diagnostic Workflow

When a query is slow, follow this sequence:

1. **Check Query Profile** (Snowsight > Query History > select query > Query Profile)
   - Identify the most expensive operator nodes (% of total time)
   - Check `Partitions Scanned` vs `Partitions Total` on TableScan nodes
   - Look for spillage indicators (bytes spilled to local/remote storage)
   - Check for exploding joins (output rows >> input rows)

2. **Check key metrics** in `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`:
   - `bytes_spilled_to_local_storage` / `bytes_spilled_to_remote_storage` > 0 = memory pressure
   - `partitions_scanned` / `partitions_total` close to 1.0 = poor pruning
   - `queued_overload_time` > 0 = warehouse concurrency bottleneck
   - `compilation_time` high = complex query plan or metadata issues
   - `percentage_scanned_from_cache` low = cold cache or different data each time

3. **Apply fixes** based on the bottleneck identified (see sections below)

See [references/diagnostic-queries.md](references/diagnostic-queries.md) for ready-to-use SQL.

## Partition Pruning

The single most impactful optimization. Snowflake stores min/max metadata per micro-partition
per column; good pruning means scanning a fraction of partitions.

**Target**: `Partitions Scanned` << `Partitions Total` on TableScan nodes.

### Rules

- Filter on **raw columns**, not expressions: `WHERE date_col >= '2024-01-01'` not `WHERE YEAR(date_col) = 2024`
- Never `CAST` the column side; cast the constant: `WHERE col = 42` not `WHERE CAST(col AS NUMBER) = 42`
- `IN (SELECT ...)` subqueries do NOT enable pruning; use `JOIN` or `EXISTS` instead
- Range predicates on well-clustered columns prune effectively
- Verify pruning in Query Profile: check TableScan node statistics

### Anti-Patterns That Break Pruning

| Anti-Pattern | Fix |
|---|---|
| `WHERE YEAR(date_col) = 2024` | `WHERE date_col >= '2024-01-01' AND date_col < '2025-01-01'` |
| `WHERE CAST(col AS NUMBER) = 5` | `WHERE col = 5` (implicit cast on constant is fine) |
| `WHERE col IN (SELECT ...)` | `WHERE EXISTS (SELECT 1 FROM ... WHERE ...)` or use JOIN |
| `SELECT *` | Select only needed columns |
| Filter on non-clustered column | Add clustering key or restructure query |
| `OR` in join conditions | Split into `UNION ALL` of equi-joins |

## Clustering Keys

Add clustering keys only when **all** of these are true:
- Table is large (multi-TB, millions of micro-partitions)
- Queries filter/join on the same 1-3 columns consistently
- High read-to-write ratio
- `SYSTEM$CLUSTERING_INFORMATION` shows high depth/overlap

### Choosing Columns

1. Most common WHERE filter columns first
2. Then JOIN predicate columns
3. Order low-to-high cardinality in `CLUSTER BY`
4. Max 3-4 columns
5. Reduce high-cardinality columns with expressions: `TO_DATE(timestamp_col)`, `TRUNC(id, -5)`
6. VARCHAR columns: only first 5 bytes used in clustering metadata

```sql
-- Cluster by expression to reduce cardinality
ALTER TABLE events CLUSTER BY (TO_DATE(event_ts), event_type);

-- Check clustering health
SELECT SYSTEM$CLUSTERING_INFORMATION('db.schema.table_name', '(col1, col2)');

-- Estimate costs before enabling
SELECT SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS('db.schema.table_name');
```

**Depth interpretation**: 1-2 = well clustered; increasing over time = degrading; compare with query performance as the ultimate indicator.

## Warehouse Sizing

| Size | Credits/Hr | Use Case |
|------|-----------|----------|
| XS | 1 | Dev/test, simple SELECTs, lightweight tasks |
| S | 2 | Basic ELT, simple dashboards |
| M | 4 | Moderate queries, standard ELT |
| L | 8 | Complex joins/aggregations |
| XL | 16 | Heavy transformations, large MERGE |
| 2XL+ | 32-512 | Large-scale batch processing |

### Scale Up vs Scale Out

- **Spilling to local/remote storage** -> Scale UP (larger warehouse = more memory)
- **Queries queuing** -> Scale OUT (multi-cluster) or separate warehouses
- **Load consistently < 1, no queuing** -> Scale DOWN (over-provisioned)

### Multi-Cluster Warehouses

- **Standard scaling policy**: new cluster starts immediately on queuing (latency-sensitive)
- **Economy scaling policy**: new cluster only if busy >= 6 min (cost-sensitive)
- Start with auto-scale, min=1, max=2-3; adjust based on monitoring

### Cost Rules

- Set auto-suspend to **60 seconds** for virtually all warehouses
- Never mix BI + ETL on the same warehouse
- Separate warehouses by workload type (BI, ETL, ad-hoc, tasks)
- Resume takes < 1 second; don't avoid suspending

## Query Optimization Patterns

### JOINs

- **Smaller table on left** (build side of hash join), larger on right (probe side)
- Use `DIRECTED JOIN` if optimizer gets join order wrong
- **Never use OR in join conditions** -- causes Cartesian join; split into `UNION ALL`
- **Range joins** (`BETWEEN`, `>=`/`<`) cause Cartesian joins; use `ASOF JOIN` or add equi-join binning column
- Add clustered columns to join/merge predicates for dynamic pruning

```sql
-- ANTI-PATTERN: OR in join (Cartesian, minutes)
SELECT * FROM a JOIN b ON a.x = b.x OR a.y = b.y;

-- FIX: UNION ALL of equi-joins (seconds)
SELECT * FROM a JOIN b ON a.x = b.x
UNION ALL
SELECT * FROM a JOIN b ON a.y = b.y;

-- Range join fix: ASOF JOIN
SELECT r.*, p.price
FROM refills r
ASOF JOIN prices p
    MATCH_CONDITION (r.ts >= p.valid_from)
    ON r.station_id = p.station_id;
```

### CTEs vs Temp Tables

- CTEs are **not materialized by default** in Snowflake (inlined like subqueries)
- Multi-referenced CTEs may get a `WithClause` materialization -- check Query Profile
- Use **temp tables** when: intermediate result is expensive AND used by multiple downstream queries

```sql
-- When CTE is referenced multiple times and is expensive, materialize it
CREATE TEMPORARY TABLE stage_1 AS
SELECT customer_id, SUM(amount) AS total
FROM orders WHERE order_date >= DATEADD(year, -1, CURRENT_DATE())
GROUP BY customer_id;
```

### QUALIFY

Always prefer `QUALIFY` over wrapping subqueries for window function filtering:

```sql
-- Instead of subquery wrapper
SELECT * FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- Deduplication pattern
SELECT * FROM raw_events
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _loaded_at DESC) = 1;
```

Execution order: `FROM > WHERE > GROUP BY > HAVING > Window Fns > QUALIFY > DISTINCT > ORDER BY > LIMIT`

### GROUP BY

- Use `GROUP BY ALL` (Snowflake extension) to auto-group by all non-aggregate SELECT columns
- **Filter before grouping** -- reduce input rows with WHERE before GROUP BY
- Use `APPROX_COUNT_DISTINCT()` for ~2% error but much faster distinct counts
- For skewed data (many NULLs), filter dominant values separately and `UNION ALL`

### DISTINCT

DISTINCT is expensive -- sorts/hashes all output rows. Prefer alternatives:

| Instead of DISTINCT... | Use... |
|---|---|
| Dedup after join | `EXISTS` (avoids join explosion) |
| Dedup rows | `QUALIFY ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts DESC) = 1` |
| Count distinct | `APPROX_COUNT_DISTINCT()` for dashboards |

### EXISTS vs IN vs JOIN

| Pattern | Best For |
|---|---|
| `EXISTS` | Semi-joins (existence checks) -- stops on first match |
| `IN` | Small static lists only |
| `JOIN` | When you need columns from both tables |

Avoid `IN (SELECT ...)` on large tables; prefer `EXISTS`.

### UNION ALL vs UNION

Always use `UNION ALL` unless you specifically need deduplication. `UNION` = `UNION ALL` + `DISTINCT`.

### Window Functions

- Prefer over self-joins for row-relative calculations (LAG, LEAD, ROW_NUMBER)
- Use named windows (`WINDOW w AS (...)`) when reusing the same PARTITION BY/ORDER BY
- Same window spec across multiple functions shares the sort
- Always use QUALIFY to filter window results (not a wrapping subquery)

## Caching

### Three Layers

| Cache | Scope | Duration | Cost | How to Leverage |
|---|---|---|---|---|
| **Result cache** | Global | 24h (extends on reuse, max 31d) | Free | Exact same query text + no data changes + no non-deterministic fns |
| **Local disk cache** | Per-warehouse | While warehouse runs | Free | Keep related workloads on same warehouse |
| **Metadata cache** | Global | Always | Free | Good clustering = better min/max stats |

**Result cache gotchas**: Case-sensitive, whitespace-sensitive, alias-sensitive. Standardize query patterns.

## Semi-Structured Data (VARIANT)

- Always cast extractions to native types: `src:field::STRING`, `src:price::NUMBER`
- Element names are **case-sensitive** (unlike column names)
- Prefer higher-order functions (`FILTER`, `TRANSFORM`) over `FLATTEN` when possible
- When using `LATERAL FLATTEN`, cast early and filter early
- Consider clustering on VARIANT paths: `CLUSTER BY (v:"Data":id::NUMBER)`

## Search Optimization Service

For **point lookups** on high-cardinality columns (emails, IDs) on large tables:

```sql
ALTER TABLE customers ADD SEARCH OPTIMIZATION ON (email, customer_id);
SELECT SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('db.schema.table_name');
```

Best for equality filters returning few rows. Not useful for range queries (use clustering).

## Materialized Views

Use when an expensive aggregation/join is queried repeatedly with identical logic:

- Refresh is automatic but costs serverless credits
- Cannot include UDFs, QUALIFY, LIMIT, or certain complex constructs
- Best for: pre-aggregated dashboards, denormalized lookup tables
- Consider temp tables or scheduled tasks as alternatives with more flexibility

## Data Loading

- Target **100-250 MB compressed** files for COPY INTO
- Thousands of tiny files = high overhead
- Use `COPY INTO` with `FILE_FORMAT` options, not INSERT
- Separate loading warehouse from query warehouse

## Priority Checklist for Slow Queries

1. Check Query Profile -- find the most expensive nodes
2. Filter early -- push WHERE clauses close to source tables
3. Check partition pruning -- Partitions Scanned vs Total
4. Select only needed columns -- avoid `SELECT *`
5. Optimize joins -- no OR; use DIRECTED if needed; ASOF for range joins
6. Use QUALIFY -- not subquery wrappers for window filtering
7. Leverage caching -- standardize query text
8. Materialize when needed -- temp tables for expensive multi-ref intermediates
9. UNION ALL over UNION
10. EXISTS over IN for existence checks
11. APPROX_COUNT_DISTINCT when exact counts unnecessary
12. Cast VARIANT data to native types early
13. If still slow -- increase warehouse size (especially if spilling)

## References

- [references/diagnostic-queries.md](references/diagnostic-queries.md) -- Ready-to-use SQL for performance diagnosis
- [references/resources.md](references/resources.md) -- External articles, docs, and community resources

## External Documentation

- [Snowflake Performance Overview](https://docs.snowflake.com/en/guides-overview-performance)
- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-snowsight-activity)
- [Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys)
- [Micro-partitions](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions)
- [Warehouse Sizing](https://docs.snowflake.com/en/user-guide/performance-query-warehouse)
- [Search Optimization](https://docs.snowflake.com/en/user-guide/search-optimization-service)
- [Materialized Views](https://docs.snowflake.com/en/user-guide/views-materialized)
- [EXPLAIN](https://docs.snowflake.com/en/sql-reference/sql/explain)
- [QUALIFY](https://docs.snowflake.com/en/sql-reference/constructs/qualify)
- [ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage)
