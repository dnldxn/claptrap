# Snowflake Optimization: Overview & Diagnostic Framework

This is the entry point for Snowflake performance and cost optimization. It provides the mental model for understanding where Snowflake costs originate, a diagnostic toolkit for identifying optimization opportunities, and a routing guide to the detailed sub-topic files.

**Sub-topic files:**
- `optimization-query-performance.md` — Query profiling, slow query diagnosis, tuning techniques, caching
- `optimization-compute.md` — Warehouse sizing, Gen 1 vs Gen 2, multi-cluster, auto-suspend
- `optimization-data-access.md` — Clustering, SOS, QAS, Materialized Views, Dynamic Tables

Load only the sub-topic(s) relevant to the current task.

## Snowflake Cost Model for Optimization

Understanding where money goes is prerequisite to optimizing it. Snowflake costs fall into four buckets:

| Cost Category | What Drives It | Key Monitoring Views |
|---------------|---------------|---------------------|
| **Virtual Warehouse Compute** | Warehouse size × run-time. Credits billed per-second (60s minimum on resume). Idle running warehouses burn credits. | `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` |
| **Serverless Compute** | Automatic Clustering, Materialized View maintenance, Search Optimization maintenance, Serverless Tasks, Dynamic Table refreshes, Replication. Billed per compute-hour. | `SNOWFLAKE.ACCOUNT_USAGE.SERVERLESS_TASK_HISTORY`, `AUTOMATIC_CLUSTERING_HISTORY`, `MATERIALIZED_VIEW_REFRESH_HISTORY`, `SEARCH_OPTIMIZATION_HISTORY`, `DYNAMIC_TABLE_REFRESH_HISTORY` |
| **Cloud Services** | Query compilation, metadata operations, SHOW/DESCRIBE commands, authentication. Free up to 10% of daily warehouse compute; excess is billed. | `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` (filter `warehouse_name IS NULL` for pure cloud-services queries) |
| **Storage** | Active data, Time Travel, Fail-safe, staging, clones divergence, MV storage, search access paths. | `SNOWFLAKE.ACCOUNT_USAGE.STORAGE_USAGE`, `TABLE_STORAGE_METRICS` |

**Practical implication:** Most optimization effort should target warehouse compute (typically 60-80% of total spend). Serverless features can creep up if left unmonitored — especially Automatic Clustering on tables with heavy DML.

## Optimization Decision Framework

Not every table or query needs optimization. Use this decision tree to avoid over-engineering:

1. **Is there an actual problem?** Measure before optimizing. Compare query runtimes against SLAs. Check whether credit spend exceeds budget.
2. **What is the bottleneck?** Use the diagnostic toolkit below to determine whether the issue is compute (warehouse too small/large), data access (poor pruning), query design (anti-patterns), or unnecessary work (redundant queries, stale pipelines).
3. **What is the cheapest fix?** Order of effort, roughly:
   - Query rewrite (free)
   - Warehouse right-sizing or schedule tuning (minutes)
   - Clustering key addition (hours, ongoing cost)
   - SOS / QAS enablement (minutes to enable, ongoing cost)
   - Materialized View or Dynamic Table (design + ongoing cost)
4. **Does the fix pay for itself?** Every serverless feature and clustering key costs credits. Estimate the break-even: will the saved warehouse credits exceed the maintenance cost?

## Diagnostic Toolkit

### Key ACCOUNT_USAGE Views

These views retain 365 days of history (1-year rolling). Use them for trend analysis and systemic optimization.

| View | What It Tells You |
|------|-------------------|
| `QUERY_HISTORY` | Every query: runtime, bytes scanned, partitions scanned/total, compilation time, queuing time, spill, warehouse. The single most important view for optimization. |
| `AGGREGATE_QUERY_HISTORY` | Queries grouped by parameterized hash — identify the most expensive query *patterns*, not just individual executions. |
| `WAREHOUSE_METERING_HISTORY` | Credit consumption per warehouse per hour. Spot idle warehouses and right-sizing opportunities. |
| `AUTOMATIC_CLUSTERING_HISTORY` | Credits spent on reclustering per table. Detect runaway clustering costs. |
| `MATERIALIZED_VIEW_REFRESH_HISTORY` | Credits spent maintaining MVs. Find MVs that cost more than they save. |
| `SEARCH_OPTIMIZATION_HISTORY` | Credits for SOS maintenance per table. |
| `QUERY_ACCELERATION_HISTORY` | Credits consumed by QAS and which queries used it. |
| `DYNAMIC_TABLE_REFRESH_HISTORY` | DT refresh durations, data processed, and refresh mode (incremental vs full). |
| `TABLE_STORAGE_METRICS` | Per-table storage: active, time travel, fail-safe, retained for clones. |

### Key System Functions

| Function | Purpose |
|----------|---------|
| `SYSTEM$CLUSTERING_INFORMATION('<table>', '(<cols>)')` | Clustering quality report: average depth, histogram, partition overlap. |
| `SYSTEM$CLUSTERING_DEPTH('<table>', '(<cols>)')` | Single number — average clustering depth for given columns. |
| `SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('<table>')` | Projected storage and compute cost to enable SOS on a table. |
| `SYSTEM$ESTIMATE_QUERY_ACCELERATION('<query_id>')` | Whether a past query was QAS-eligible, and estimated speedup at various scale factors. |
| `GET_QUERY_OPERATOR_STATS('<query_id>')` | Operator-level statistics from the query profile — programmatic access to what Snowsight shows in the profile UI. |

### Query Profile (Snowsight)

The query profile in Snowsight is the primary tool for diagnosing individual slow queries. Key things to look for:

| Profile Signal | What It Means | Action |
|---------------|---------------|--------|
| **Bytes scanned >> bytes sent** | The query reads far more data than it returns — poor pruning or missing filters. | Add clustering keys or filters. Consider SOS for point lookups. |
| **Partitions scanned >> partitions total × selectivity** | Micro-partition pruning is ineffective. | Check clustering depth; add/change clustering key on the filtered columns. |
| **Spillage to local/remote storage** | Intermediate results exceed warehouse memory. Local spill is ~1 order of magnitude slower; remote spill is ~2 orders. | Increase warehouse size, or rewrite the query to reduce intermediate data (e.g., filter earlier, avoid unnecessary DISTINCT). |
| **Long compilation time** | Complex SQL, deep view chains, or heavy cloud-services load. | Simplify SQL, reduce nested view depth, check for excessive CTEs. |
| **Queuing time > 0** | Warehouse is overloaded — queries are waiting for compute. | Scale up the warehouse, enable multi-cluster, or distribute workloads across warehouses. |
| **Percentage scanned from cache** | 0% means no warehouse cache benefit — data not recently accessed or warehouse was recently resumed. | Keep warehouse running if the workload is cache-sensitive. |
| **Query Acceleration statistics** | Shows if QAS was used and how much work it offloaded. | If QAS was not used but the query has large scans, evaluate enabling it. |

### Standard Diagnostic Queries

**Top 20 most expensive queries (by scan) in the last 7 days:**
```sql
SELECT query_id, query_text, warehouse_name,
       total_elapsed_time / 1000 AS elapsed_sec,
       bytes_scanned / POWER(1024, 3) AS gb_scanned,
       partitions_scanned, partitions_total,
       ROUND(partitions_scanned / NULLIF(partitions_total, 0) * 100, 1) AS pct_scanned,
       bytes_spilled_to_local_storage / POWER(1024, 3) AS gb_spill_local,
       bytes_spilled_to_remote_storage / POWER(1024, 3) AS gb_spill_remote
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND warehouse_name IS NOT NULL
  AND bytes_scanned > 0
ORDER BY bytes_scanned DESC
LIMIT 20;
```

**Warehouses with lowest utilization (potential right-sizing candidates):**
```sql
SELECT warehouse_name,
       SUM(credits_used) AS total_credits,
       COUNT(DISTINCT DATE_TRUNC('hour', start_time)) AS active_hours,
       ROUND(total_credits / NULLIF(active_hours, 0), 2) AS credits_per_active_hour
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;
```

**Tables with runaway clustering costs:**
```sql
SELECT table_name, SUM(credits_used) AS clustering_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY clustering_credits DESC
LIMIT 10;
```

**Queries with excessive cloud-services time (potential billing risk):**
```sql
SELECT query_id, query_text,
       compilation_time / 1000 AS compile_sec,
       total_elapsed_time / 1000 AS elapsed_sec,
       ROUND(compilation_time / NULLIF(total_elapsed_time, 0) * 100, 1) AS pct_compile
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND compilation_time > 5000   -- >5 sec compilation
ORDER BY compilation_time DESC
LIMIT 20;
```

## Routing Guide

| Symptom | Start With |
|---------|------------|
| Individual queries are slow | `optimization-query-performance.md` |
| High warehouse credit spend | `optimization-compute.md` |
| Queries scan too many partitions | `optimization-data-access.md` (Clustering) |
| Point lookups are slow on large tables | `optimization-data-access.md` (SOS) |
| Ad-hoc queries with large scans are slow | `optimization-data-access.md` (QAS) |
| Repeated expensive aggregations | `optimization-data-access.md` (Materialized Views) |
| Complex pipelines need simplification | `optimization-data-access.md` (Dynamic Tables) |
| Warehouse queuing / concurrency issues | `optimization-compute.md` (Multi-cluster) |
| Unclear whether Gen 2 warehouses would help | `optimization-compute.md` (Gen 1 vs Gen 2) |
| Need to reduce serverless costs | `optimization-data-access.md` (cost sections for each feature) |

## Version & Status

All features discussed in the optimization sub-topics are GA unless noted otherwise. Gen 2 warehouses became GA in 2025 and are now the default for new organizations in most regions.
