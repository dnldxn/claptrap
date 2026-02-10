# Diagnostic SQL Queries for Snowflake Performance

Ready-to-use queries for identifying and analyzing performance issues.

## Table of Contents

- [Slow Query Discovery](#slow-query-discovery)
- [Partition Pruning Analysis](#partition-pruning-analysis)
- [Spillage Detection](#spillage-detection)
- [Warehouse Utilization](#warehouse-utilization)
- [Clustering Health](#clustering-health)
- [Cost Analysis](#cost-analysis)
- [Caching Effectiveness](#caching-effectiveness)
- [Query Patterns and Grouping](#query-patterns-and-grouping)

---

## Slow Query Discovery

### Top 50 slowest queries (last 30 days)

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 100) AS query_preview,
    user_name,
    warehouse_name,
    total_elapsed_time / 1000 AS elapsed_seconds,
    execution_time / 1000 AS exec_seconds,
    compilation_time / 1000 AS compile_seconds,
    queued_overload_time / 1000 AS queue_seconds,
    bytes_scanned / (1024*1024*1024) AS gb_scanned,
    rows_produced,
    start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND query_type IN ('SELECT', 'INSERT', 'CREATE_TABLE_AS_SELECT', 'MERGE', 'UPDATE', 'DELETE')
ORDER BY total_elapsed_time DESC
LIMIT 50;
```

### Time breakdown for a specific query

```sql
SELECT
    query_id,
    total_elapsed_time / 1000 AS total_sec,
    compilation_time / 1000 AS compile_sec,
    queued_overload_time / 1000 AS queued_sec,
    queued_provisioning_time / 1000 AS provisioning_sec,
    transaction_blocked_time / 1000 AS blocked_sec,
    execution_time / 1000 AS exec_sec,
    -- Time breakdown percentages
    ROUND(compilation_time * 100.0 / NULLIF(total_elapsed_time, 0), 1) AS pct_compile,
    ROUND(queued_overload_time * 100.0 / NULLIF(total_elapsed_time, 0), 1) AS pct_queued,
    ROUND(execution_time * 100.0 / NULLIF(total_elapsed_time, 0), 1) AS pct_exec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_id = '<QUERY_ID>';
```

### Most expensive queries by compute (bytes scanned, last 7 days)

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 100) AS query_preview,
    warehouse_name,
    bytes_scanned / (1024*1024*1024) AS gb_scanned,
    partitions_scanned,
    partitions_total,
    ROUND(partitions_scanned * 100.0 / NULLIF(partitions_total, 0), 1) AS pct_partitions_scanned,
    execution_time / 1000 AS exec_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
ORDER BY bytes_scanned DESC
LIMIT 50;
```

---

## Partition Pruning Analysis

### Find queries with poor pruning (scanning > 80% of partitions)

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 100) AS query_preview,
    warehouse_name,
    partitions_scanned,
    partitions_total,
    ROUND(partitions_scanned * 100.0 / NULLIF(partitions_total, 0), 1) AS pct_scanned,
    bytes_scanned / (1024*1024*1024) AS gb_scanned,
    execution_time / 1000 AS exec_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND partitions_total > 100
    AND partitions_scanned * 1.0 / NULLIF(partitions_total, 0) > 0.8
ORDER BY partitions_total DESC
LIMIT 50;
```

### Full table scans (100% partition scan)

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 150) AS query_preview,
    user_name,
    warehouse_name,
    partitions_scanned,
    partitions_total,
    bytes_scanned / (1024*1024*1024) AS gb_scanned,
    execution_time / 1000 AS exec_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND partitions_total > 100
    AND partitions_scanned = partitions_total
ORDER BY bytes_scanned DESC
LIMIT 50;
```

---

## Spillage Detection

### Queries spilling to storage (last 30 days)

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 100) AS query_preview,
    user_name,
    warehouse_name,
    warehouse_size,
    bytes_spilled_to_local_storage / (1024*1024*1024) AS gb_spilled_local,
    bytes_spilled_to_remote_storage / (1024*1024*1024) AS gb_spilled_remote,
    execution_time / 1000 AS exec_seconds,
    start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND (bytes_spilled_to_local_storage > 0 OR bytes_spilled_to_remote_storage > 0)
ORDER BY bytes_spilled_to_remote_storage DESC, bytes_spilled_to_local_storage DESC
LIMIT 25;
```

### Spillage summary by warehouse (are any warehouses undersized?)

```sql
SELECT
    warehouse_name,
    warehouse_size,
    COUNT(*) AS spill_query_count,
    SUM(CASE WHEN bytes_spilled_to_remote_storage > 0 THEN 1 ELSE 0 END) AS remote_spill_count,
    ROUND(AVG(bytes_spilled_to_local_storage) / (1024*1024*1024), 2) AS avg_gb_spilled_local,
    ROUND(AVG(bytes_spilled_to_remote_storage) / (1024*1024*1024), 2) AS avg_gb_spilled_remote,
    ROUND(AVG(execution_time) / 1000, 1) AS avg_exec_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -30, CURRENT_TIMESTAMP())
    AND (bytes_spilled_to_local_storage > 0 OR bytes_spilled_to_remote_storage > 0)
GROUP BY ALL
ORDER BY remote_spill_count DESC, spill_query_count DESC;
```

---

## Warehouse Utilization

### Warehouses with queuing (concurrency bottleneck, last 30 days)

```sql
SELECT
    TO_DATE(start_time) AS date,
    warehouse_name,
    ROUND(SUM(avg_running), 1) AS sum_running,
    ROUND(SUM(avg_queued_load), 1) AS sum_queued
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY ALL
HAVING SUM(avg_queued_load) > 0
ORDER BY sum_queued DESC;
```

### Idle warehouse cost (warehouses running with no queries)

```sql
SELECT
    warehouse_name,
    SUM(credits_used) AS total_credits,
    SUM(credits_used_compute) AS compute_credits,
    SUM(credits_used_cloud_services) AS cloud_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY ALL
ORDER BY total_credits DESC;
```

### Queries with high queue time

```sql
SELECT
    query_id,
    SUBSTR(query_text, 1, 100) AS query_preview,
    warehouse_name,
    queued_overload_time / 1000 AS queue_seconds,
    total_elapsed_time / 1000 AS total_seconds,
    ROUND(queued_overload_time * 100.0 / NULLIF(total_elapsed_time, 0), 1) AS pct_queued,
    start_time
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND queued_overload_time > 5000  -- queued more than 5 seconds
ORDER BY queued_overload_time DESC
LIMIT 25;
```

---

## Clustering Health

### Check clustering info for a table

```sql
-- Clustering depth (lower is better; 1-2 = well clustered)
SELECT SYSTEM$CLUSTERING_DEPTH('db.schema.table_name');

-- Full clustering information (JSON)
SELECT SYSTEM$CLUSTERING_INFORMATION('db.schema.table_name');

-- Clustering info on specific columns (even without a defined key)
SELECT SYSTEM$CLUSTERING_INFORMATION('db.schema.table_name', '(col1, col2)');

-- Estimate reclustering costs before enabling
SELECT SYSTEM$ESTIMATE_AUTOMATIC_CLUSTERING_COSTS('db.schema.table_name');
```

### Monitor reclustering costs (last 30 days)

```sql
SELECT
    TO_DATE(start_time) AS date,
    database_name,
    schema_name,
    table_name,
    SUM(credits_used) AS credits_used,
    SUM(num_bytes_reclustered) / (1024*1024*1024) AS gb_reclustered
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY ALL
ORDER BY credits_used DESC;
```

---

## Cost Analysis

### Credit consumption by warehouse (last 30 days)

```sql
SELECT
    warehouse_name,
    ROUND(SUM(credits_used), 2) AS total_credits,
    ROUND(SUM(credits_used_compute), 2) AS compute_credits,
    ROUND(SUM(credits_used_cloud_services), 2) AS cloud_credits,
    COUNT(DISTINCT TO_DATE(start_time)) AS active_days,
    ROUND(SUM(credits_used) / COUNT(DISTINCT TO_DATE(start_time)), 2) AS avg_daily_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY ALL
ORDER BY total_credits DESC;
```

### Table storage costs (largest tables)

```sql
SELECT
    table_catalog AS database,
    table_schema AS schema,
    table_name,
    ROUND(active_bytes / (1024*1024*1024), 2) AS active_gb,
    ROUND(time_travel_bytes / (1024*1024*1024), 2) AS time_travel_gb,
    ROUND(failsafe_bytes / (1024*1024*1024), 2) AS failsafe_gb,
    ROUND((active_bytes + time_travel_bytes + failsafe_bytes) / (1024*1024*1024), 2) AS total_gb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE active_bytes > 0
ORDER BY total_gb DESC
LIMIT 50;
```

### Materialized view refresh costs

```sql
SELECT
    TO_DATE(start_time) AS date,
    database_name,
    schema_name,
    table_name,
    SUM(credits_used) AS credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY ALL
ORDER BY credits_used DESC;
```

---

## Caching Effectiveness

### Result cache hit rate

```sql
SELECT
    warehouse_name,
    COUNT(*) AS total_queries,
    SUM(CASE WHEN percentage_scanned_from_cache = 100 THEN 1 ELSE 0 END) AS full_cache_hits,
    ROUND(AVG(percentage_scanned_from_cache), 1) AS avg_pct_from_cache,
    ROUND(full_cache_hits * 100.0 / total_queries, 1) AS cache_hit_rate_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND query_type = 'SELECT'
GROUP BY ALL
ORDER BY total_queries DESC;
```

---

## Query Patterns and Grouping

### Most repeated query patterns (by query_parameterized_hash)

```sql
SELECT
    query_parameterized_hash,
    COUNT(*) AS execution_count,
    SUBSTR(ANY_VALUE(query_text), 1, 100) AS sample_query,
    ROUND(AVG(total_elapsed_time) / 1000, 1) AS avg_elapsed_sec,
    ROUND(AVG(bytes_scanned) / (1024*1024*1024), 2) AS avg_gb_scanned,
    ROUND(SUM(bytes_scanned) / (1024*1024*1024), 2) AS total_gb_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
GROUP BY query_parameterized_hash
HAVING COUNT(*) >= 5
ORDER BY total_gb_scanned DESC
LIMIT 25;
```

### Using QUERY_TAG for tracking

```sql
-- Set a query tag for a session
ALTER SESSION SET QUERY_TAG = 'etl:daily_load:customers';

-- Find queries by tag
SELECT query_id, query_tag, total_elapsed_time / 1000 AS elapsed_sec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_tag LIKE 'etl:%'
    AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY total_elapsed_time DESC;

-- Unset when done
ALTER SESSION UNSET QUERY_TAG;
```

### Comprehensive health check query

```sql
SELECT
    warehouse_name,
    COUNT(*) AS query_count,
    ROUND(AVG(total_elapsed_time) / 1000, 1) AS avg_elapsed_sec,
    ROUND(AVG(execution_time) / 1000, 1) AS avg_exec_sec,
    ROUND(AVG(compilation_time) / 1000, 1) AS avg_compile_sec,
    ROUND(AVG(queued_overload_time) / 1000, 1) AS avg_queue_sec,
    ROUND(AVG(bytes_scanned) / (1024*1024*1024), 2) AS avg_gb_scanned,
    SUM(CASE WHEN bytes_spilled_to_local_storage > 0 THEN 1 ELSE 0 END) AS local_spill_count,
    SUM(CASE WHEN bytes_spilled_to_remote_storage > 0 THEN 1 ELSE 0 END) AS remote_spill_count,
    ROUND(AVG(percentage_scanned_from_cache), 1) AS avg_cache_pct,
    ROUND(AVG(
        CASE WHEN partitions_total > 0
            THEN partitions_scanned * 100.0 / partitions_total
            ELSE NULL END
    ), 1) AS avg_pct_partitions_scanned
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
    AND execution_status = 'SUCCESS'
    AND query_type IN ('SELECT', 'INSERT', 'CREATE_TABLE_AS_SELECT', 'MERGE', 'UPDATE', 'DELETE')
GROUP BY ALL
ORDER BY query_count DESC;
```

### EXPLAIN plan

```sql
-- Tabular output (default)
EXPLAIN SELECT * FROM orders WHERE order_date >= '2024-01-01';

-- JSON output (more detail)
EXPLAIN USING JSON SELECT * FROM orders WHERE order_date >= '2024-01-01';

-- Key columns to check:
-- partitionsTotal, partitionsAssigned (pruning effectiveness)
-- expressions (what operations are planned)
-- operation types (TableScan, Filter, Join, Sort, Aggregate, etc.)
```

**Note**: EXPLAIN shows the logical plan (upper-bound estimates). It does not require a running warehouse. For actual execution statistics, use Query Profile.
