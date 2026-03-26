# Snowflake Optimization: Query Performance

How to identify, diagnose, and fix slow queries. This reference assumes familiarity with the Snowflake query profile and ACCOUNT_USAGE views covered in `optimization-overview.md`.

## Identifying Slow Queries

### Using QUERY_HISTORY

The `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` view is the primary source for identifying slow queries at scale. Key columns for optimization work:

| Column | Optimization Signal |
|--------|-------------------|
| `TOTAL_ELAPSED_TIME` | Wall-clock time including queuing. High values indicate slow queries or concurrency pressure. |
| `EXECUTION_TIME` | Actual processing time (excludes compilation and queuing). Compare against elapsed to isolate bottleneck. |
| `COMPILATION_TIME` | Time in the cloud-services layer compiling the query. High values indicate complex SQL or deep view nesting. |
| `QUEUING_OVERLOAD_TIME` | Time waiting because the warehouse was overloaded. Non-zero means the warehouse needs scaling. |
| `BYTES_SCANNED` | Raw data read from storage. High values with low result set sizes indicate pruning problems. |
| `PARTITIONS_SCANNED` / `PARTITIONS_TOTAL` | The ratio reveals pruning efficiency. Scanning >10% of partitions for selective queries signals poor clustering or missing filters. |
| `BYTES_SPILLED_TO_LOCAL_STORAGE` | Intermediate results exceeded warehouse memory. Performance impact ~5-10x slower than in-memory. |
| `BYTES_SPILLED_TO_REMOTE_STORAGE` | Spill exceeded local SSD. Performance impact ~50-100x slower than in-memory. This is the single biggest performance killer. |
| `PERCENTAGE_SCANNED_FROM_CACHE` | How much data was served from the warehouse's local SSD cache vs. remote storage. |
| `QUERY_ACCELERATION_PARTITIONS_SCANNED` | If >0, QAS was active for this query. Useful for measuring QAS effectiveness. |

### Using AGGREGATE_QUERY_HISTORY

For workload-level analysis, group queries by their parameterized hash to find the most expensive *patterns*:

```sql
-- Most expensive query patterns in the last 30 days
SELECT parameterized_query_hash,
       any_value(query_text) AS sample_query,
       COUNT(*) AS executions,
       SUM(total_elapsed_time) / 1000 AS total_elapsed_sec,
       AVG(total_elapsed_time) / 1000 AS avg_elapsed_sec,
       SUM(bytes_scanned) / POWER(1024, 4) AS total_tb_scanned,
       SUM(bytes_spilled_to_remote_storage) / POWER(1024, 3) AS total_gb_remote_spill
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
  AND warehouse_name IS NOT NULL
GROUP BY parameterized_query_hash
ORDER BY total_elapsed_sec DESC
LIMIT 20;
```

This is more useful than looking at individual queries because one bad query pattern running 10,000 times a day has far more impact than a single slow ad-hoc query.

### Using Query Tags

Set `QUERY_TAG` on sessions or individual statements to classify workloads for analysis:

```sql
ALTER SESSION SET QUERY_TAG = 'team=analytics;pipeline=daily_revenue';
```

Then filter in QUERY_HISTORY:
```sql
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_tag LIKE '%pipeline=daily_revenue%'
  AND start_time > DATEADD('day', -7, CURRENT_TIMESTAMP());
```

Tags are free metadata — use them to attribute costs and performance to teams, pipelines, or SLAs.

## Diagnosing Slow Queries

### Query Profile / Operator Stats

The query profile (Snowsight → Query Details → Profile) shows the operator tree. For programmatic access, use `GET_QUERY_OPERATOR_STATS`:

```sql
SELECT * FROM TABLE(GET_QUERY_OPERATOR_STATS('<query_id>'));
```

Key columns: `input_rows`, `output_rows`, `pruning_scanned_partitions`, `pruning_total_partitions`, `spilling_bytes_local_storage`, `spilling_bytes_remote_storage`.

### What to Look For

**1. TableScan operators with high partition counts:**
If `Partitions scanned` is a large fraction of `Partitions total`, the query is not pruning effectively. This is the most common cause of slow queries on large tables. Solutions: add or adjust clustering keys, add filters earlier in the query, or enable SOS for point lookups.

**2. Aggregate operators with high input rows:**
If an aggregation reads billions of rows to produce a few hundred, consider a Materialized View to pre-compute the aggregation, or restructure the query to filter before aggregating.

**3. Join operators:**
- **Hash join with spill**: The build side is too large. Reorder the join so the smaller table is on the build side, or add filters to reduce it.
- **CartesianJoin or NestedLoop**: Almost always unintentional — missing join condition or CROSS JOIN. Fix the query.
- **Broadcast vs. Hash redistribution**: Broadcast is efficient when one side is small. If both sides are large and you see a broadcast, the optimizer chose poorly — try rewriting with explicit subqueries or CTEs that reduce one side first.

**4. Sort operators with spill:**
Large ORDER BY or GROUP BY operations can spill. Consider whether the sort is necessary. If it is, increase warehouse size.

**5. WindowFunction operators:**
Window functions over large partitions are expensive. Ensure PARTITION BY columns have reasonable cardinality. Consider pre-aggregating or using incremental approaches.

**6. Filter operators:**
If a filter appears after a large scan or join, it may be more efficient pushed earlier in the plan.

### Clustering Depth Analysis

For tables with clustering keys, check micro-partition quality:

```sql
SELECT SYSTEM$CLUSTERING_INFORMATION('<fully_qualified_table_name>');
```

- **average_depth**: Lower is better. Values >5–10 suggest poor clustering.
- **average_overlap**: Lower is better. High overlap means micro-partitions contain broadly overlapping value ranges.
- **partition_depth_histogram**: A heavy right tail indicates the table needs re-clustering.

For tables without clustering keys where pruning is poor, check what predicates the query filters on and consider clustering on those columns.

### View Lineage

Queries referencing views may hide complexity. Trace the full lineage:

```sql
SELECT GET_DDL('VIEW', '<fully_qualified_view_name>');
```

Recursively inspect referenced views. Also check `OBJECT_DEPENDENCIES` for dependency chains:

```sql
SELECT referencing_object_name, referenced_object_name, referenced_object_domain
FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
WHERE referenced_object_name = '<TABLE_OR_VIEW_NAME>'
   OR referencing_object_name = '<TABLE_OR_VIEW_NAME>';
```

Issues to flag:
- **Deeply nested view chains** (3+ levels): can confuse the optimizer or hide unnecessary joins/columns.
- **Views with `SELECT *`**: pull all columns even when the outer query only needs a few.
- **Views with aggregations or `DISTINCT`**: the optimizer cannot always push predicates through them.

## Query Tuning Techniques

### Filter Pushdown

Snowflake's optimizer pushes filters down through views and subqueries, but cannot always do so. Ensure filters appear as early as possible in the query, especially:

- In CTEs that feed large joins
- Before FLATTEN operations (FLATTEN on unfiltered VARIANT arrays is expensive)
- Inside subqueries rather than outside them when the outer filter references only the subquery's columns

### Avoiding Full Table Scans

- Always include a filter on the clustering key columns when querying large tables
- Use `LIMIT` with `ORDER BY` to enable top-N optimization
- Avoid `SELECT *` — only select columns you need (Snowflake's columnar format means fewer columns = less data scanned)
- Avoid applying functions to filter columns: `WHERE YEAR(date_col) = 2025` cannot prune but `WHERE date_col >= '2025-01-01' AND date_col < '2026-01-01'` can

### Reducing Spill

Spill is the #1 performance killer after bad pruning:

1. **Increase warehouse size** — each size doubles memory. If you're spilling to remote storage, this is usually the first fix.
2. **Filter earlier** — reduce intermediate result sizes before joins/aggregations.
3. **Avoid unnecessary DISTINCT** — DISTINCT forces a full sort. Use GROUP BY if you need aggregation anyway.
4. **Break complex queries into stages** — use temp tables for very large intermediate results. This gives the optimizer better statistics for downstream stages.
5. **Reduce join fan-out** — if a join produces more rows than either input, check for duplicates in join keys.

### Join Optimization

- **Order matters for hash joins**: Snowflake typically picks the smaller side for the hash build, but CTEs and subqueries can confuse the optimizer. If a join is slow, try rewriting with explicit intermediate results.
- **Use transient tables for large staging**: `CREATE TRANSIENT TABLE ... AS SELECT ...` materializes an intermediate result with statistics, helping the optimizer plan downstream joins better.
- **Avoid joining on expressions**: `ON CAST(a.col AS DATE) = b.date_col` prevents pruning and can cause type-mismatch issues. Align types at the source.

### FLATTEN Optimization

FLATTEN on large VARIANT arrays is a common source of poor performance:

- Filter the parent rows before FLATTEN, not after
- Use `LATERAL FLATTEN` and ensure the outer query restricts the row set
- If you frequently flatten the same semi-structured column, consider a Materialized View with the flattened structure
- For equality predicates on VARIANT paths, SOS can help significantly

### Reducing Compilation Time

High compilation time (>5 seconds) indicates the cloud-services layer is working hard:

- **Simplify deeply nested views**: Each layer of view nesting adds compilation work. Flatten view chains where possible.
- **Reduce CTE complexity**: Dozens of CTEs referencing each other increase the search space for the optimizer.
- **Avoid excessive UNION ALL**: Chains of 50+ UNION ALL subqueries can blow up compilation time. Consider using COPY INTO with multiple files or INSERT ... SELECT in a loop.
- **Parameterize queries**: Use bind variables instead of literal values. This improves result-cache hit rates and reduces per-query compilation overhead.

### Materialization Opportunities

When the same expensive computation runs repeatedly, materialize it:

1. **Dynamic Table**: Best for continuous/periodic refresh when source data changes. Supports multi-table joins and complex transformations.
2. **Materialized View**: Best for simple aggregations/filters on a single table. Auto-maintained by Snowflake but limited to single-table queries.
3. **Temp/Transient Table with Task**: Best for complex multi-table joins on a schedule when dynamic tables aren't appropriate.

Candidates: repeated subqueries/CTEs across dashboards, aggregations on large tables with the same GROUP BY, complex multi-join views read far more often than the underlying data changes.

### Warehouse Sizing

Check if warehouses are appropriately sized by looking at spill and queuing patterns across the workload:

```sql
SELECT warehouse_name, warehouse_size,
       AVG(total_elapsed_time)/1000 AS avg_elapsed_sec,
       AVG(bytes_spilled_to_remote_storage) AS avg_remote_spill,
       AVG(queued_overload_time)/1000 AS avg_queued_sec,
       COUNT(*) AS query_count
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND execution_status = 'SUCCESS' AND warehouse_name IS NOT NULL
GROUP BY warehouse_name, warehouse_size
ORDER BY avg_elapsed_sec DESC;
```

Consistent remote spill → upsize. Consistent queuing → upsize, enable multi-cluster, or isolate workloads.

## Caching

Snowflake has three cache layers. Understanding them is key to avoiding unnecessary work.

### Result Cache

- **Scope**: Account-wide. If the same query text returns the same results, Snowflake returns the cached result without using any warehouse compute.
- **Lifetime**: 24 hours, extended each time the result is reused. Invalidated when underlying data changes.
- **Optimization**: Use consistent SQL text (same formatting, same bind approach) to maximize hits. Avoid non-deterministic functions like `CURRENT_TIMESTAMP()` in queries you want cached.
- **Cost**: Free — no warehouse credits, no cloud-services credits beyond the initial cache lookup.

### Metadata Cache

- **Scope**: Cloud-services layer. Answers queries that only need metadata — `COUNT(*)`, `MIN()`, `MAX()` on clustering-key columns, `SELECT 1 FROM table LIMIT 0`.
- **Optimization**: Queries served entirely from metadata show `PARTITIONS_SCANNED = 0` and `BYTES_SCANNED = 0` in QUERY_HISTORY. This is the fastest possible path.

### Warehouse (Local SSD) Cache

- **Scope**: Per-warehouse. Data read from remote storage is cached on the warehouse's local SSD for future queries.
- **Lifetime**: Until the warehouse is suspended (cache is cleared on suspend).
- **Optimization**: For cache-sensitive workloads, tune `AUTO_SUSPEND` to keep the warehouse running longer (e.g., 10-15 minutes instead of the default 5). Trade-off: more credits for idle time vs. better cache hit rates.
- **Monitoring**: Check `PERCENTAGE_SCANNED_FROM_CACHE` in QUERY_HISTORY. Consistent 0% on a running warehouse means the workload doesn't benefit from caching (data is too large or access patterns are too random).

## Common Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| `SELECT *` | Scans all columns. In wide tables (100+ columns), this dramatically increases I/O. | Select only needed columns. |
| `ORDER BY` without `LIMIT` | Forces a full sort of the entire result set, often with spill. | Remove ORDER BY if not needed, or add LIMIT. |
| Functions on filter columns | `WHERE UPPER(name) = 'FOO'` prevents pruning on `name`. | Store pre-transformed values, or use `COLLATE` for case-insensitive matching. |
| Cartesian joins (missing ON clause) | Explodes row count — N × M rows. | Always include a join condition. |
| FLATTEN without pre-filtering | Flattens every row in the table before filtering. | Filter parent rows first, then FLATTEN. |
| Excessive use of DISTINCT | Forces full-table sort and dedup. | Investigate why duplicates exist — fix at the source. |
| `NOT IN (subquery)` on nullable cols | Unexpected NULL handling, may prevent optimization. | Use `NOT EXISTS` or `LEFT JOIN ... WHERE key IS NULL`. |
| Correlated subqueries in SELECT | Executes per-row, poor scaling. | Rewrite as JOIN or window function. |
| `UNION` instead of `UNION ALL` | Adds implicit DISTINCT — extra sort/dedup. | Use `UNION ALL` if duplicates are acceptable. |
| `COUNT(DISTINCT)` on high cardinality | Expensive full sort/hash. | Use `APPROX_COUNT_DISTINCT` if approximate is acceptable. |
| Multiple CTEs scanning same table | Each CTE re-scans independently. | Combine into a single scan with conditional aggregation. |
| `LIKE '%value%'` (leading wildcard) | Cannot use pruning or search optimization. | Use Search Optimization Service or restructure data. |
| Joining on expressions or casts | Prevents partition pruning on join. | Align types at source or materialize as a stored column. |
| Deep view nesting (>5 levels) | High compilation time, difficult for optimizer to push down filters. | Flatten the view chain or materialize intermediate results. |
| Running SHOW/DESCRIBE in loops | Each is a cloud-services call. Thousands per minute can trigger cloud-services billing. | Use INFORMATION_SCHEMA views or RESULT_SCAN instead. |
| Not using bind variables | Each literal variant is a different query for result-cache purposes. | Parameterize queries in application code. |

## Prioritizing Recommendations

When presenting tuning recommendations, use this priority framework:

| Priority | Scope | Examples |
|----------|-------|---------|
| **P0 — Critical** | Fix immediately, highest impact | Remote storage spill, row explosion from bad joins, full scans on >1 TB tables, runaway/Cartesian queries |
| **P1 — High** | Significant performance/cost win | Local storage spill on large data, wrong clustering key for dominant queries, `SELECT *` on wide tables, nested views adding unnecessary joins, high-frequency queries lacking caching/materialization |
| **P2 — Medium** | Meaningful improvement, moderate effort | Materializing frequent aggregations, adding/changing clustering keys, `NOT IN` → `NOT EXISTS`, combining CTEs scanning same table, enabling SOS for point lookups, warehouse contention (multi-cluster or isolation) |
| **P3 — Low** | Incremental, good hygiene | `APPROX_COUNT_DISTINCT`, `UNION ALL` over `UNION`, projecting fewer intermediate columns, tuning auto-suspend/auto-resume |

For each recommendation, include: the finding with specific metrics (query ID, elapsed time, spill volume, partition scan %), the root cause, the specific fix (with SQL), estimated impact, effort level, and any risks.

## Version & Status

- `AGGREGATE_QUERY_HISTORY` is GA.
- `QUERY_ACCELERATION_PARTITIONS_SCANNED` column in QUERY_HISTORY is GA.
- `GET_QUERY_OPERATOR_STATS()` function is GA.
