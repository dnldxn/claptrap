# Snowflake Optimization: Data Access — Clustering, SOS, QAS, MVs, Dynamic Tables

How to use Snowflake's data-access optimization features to improve query performance and reduce cost. This reference focuses on **when and how to apply each feature for optimization**, not on how the features work in general — defer to the respective feature references for that.

## Choosing the Right Optimization Feature

Use this decision matrix to select the right feature for the workload pattern:

| Workload Pattern | Best Feature | Why |
|-----------------|-------------|-----|
| Range filters on large tables (date ranges, ID ranges) | **Clustering** | Co-locates rows by filter columns, enabling micro-partition pruning |
| Point lookups / equality filters on large tables | **SOS** | Search access paths enable sub-linear lookups without scanning |
| Equality on VARIANT / semi-structured paths | **SOS** | SOS supports VARIANT equality, IN, ARRAY_CONTAINS natively |
| Substring / regex searches (LIKE, ILIKE, RLIKE) | **SOS** | SOS builds substring indexes for text search acceleration |
| Ad-hoc queries with large scans and selective filters | **QAS** | Offloads parallel scan work to shared compute |
| Repeated expensive aggregations | **Materialized Views** | Pre-computes and auto-maintains the aggregation |
| Different clustering needs on the same base table | **Materialized Views** | MV can define a different clustering key than the base table |
| Complex multi-step transformation pipelines | **Dynamic Tables** | Declarative pipelines with incremental refresh |
| Pre-computed joins (multiple source tables) | **Dynamic Tables** | MVs are single-table only; DTs support joins |

**These features are complementary, not mutually exclusive.** SOS and QAS can accelerate the same query. Clustering improves both direct queries and MV/DT refresh performance. A well-optimized table might use clustering + SOS for different query patterns.

## Clustering Keys for Optimization

### When Clustering Pays Off

Clustering is cost-effective when all of these are true:
- The table is **multi-terabyte** (millions of micro-partitions)
- Queries are **selective** — they need a small fraction of the data
- Most queries filter or join on the **same few columns**
- The table has a **high query-to-DML ratio** (queried often, changed infrequently)

Do not cluster:
- Small tables (<1 TB) — Snowflake's natural micro-partition ordering is usually sufficient
- Tables with heavy continuous DML — reclustering costs will be high
- Tables where queries are full scans (no selective filters)

### Selecting Clustering Key Columns

**Priority order:**
1. Columns in **WHERE** clauses (most selective filters first)
2. Columns in **JOIN** predicates
3. Columns in **ORDER BY** or **GROUP BY** (lower priority)

**Cardinality guidelines:**
- **Too low** (e.g., boolean): Minimal pruning benefit — only 2 distinct values means partitions can't be meaningfully separated.
- **Sweet spot** (thousands to low millions): Date columns, status enums, region codes, category IDs.
- **Too high** (e.g., nanosecond timestamps, UUIDs): Reclustering cost explodes. Wrap in an expression: `TO_DATE(ts_col)` or `TRUNC(id_col, -5)`.

**Column ordering in multi-column keys:**
Order from **lowest cardinality to highest**. The first column in the key dominates the partition grouping. Putting a high-cardinality column first degrades the effectiveness of subsequent columns.

```sql
-- Good: low-card region first, medium-card date second
ALTER TABLE events CLUSTER BY (region, TO_DATE(event_timestamp));

-- Bad: high-card timestamp first destroys region clustering
ALTER TABLE events CLUSTER BY (event_timestamp, region);
```

**Maximum key columns:** 3-4 columns. Beyond that, reclustering costs increase faster than pruning benefits.

### Monitoring Clustering Health

```sql
-- Check clustering quality for specific columns
SELECT SYSTEM$CLUSTERING_INFORMATION('my_db.my_schema.events', '(region, TO_DATE(event_timestamp))');
```

Key metrics in the output:
- **`average_depth`**: Lower is better. Depth of 1-2 is excellent. Depth >5 on a frequently-queried table signals reclustering is needed.
- **`partition_depth_histogram`**: Shows distribution. If most partitions are at depth 1-2 with a tail of higher depths, the table is mostly well-clustered.

```sql
-- Track clustering costs over time
SELECT table_name,
       SUM(credits_used) AS total_credits,
       SUM(num_bytes_reclustered) / POWER(1024, 3) AS gb_reclustered
FROM SNOWFLAKE.ACCOUNT_USAGE.AUTOMATIC_CLUSTERING_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY total_credits DESC;
```

**If clustering costs are high for a table**, check whether:
- The clustering key has too many columns or too-high cardinality
- The table has heavy continuous DML (consider batching writes)
- The table needs clustering at all (re-evaluate query patterns)

### Clustering + Other Features

- **Clustering + SOS**: Clustering helps range queries; SOS helps point lookups. Both can be active on the same table for different query types.
- **Clustering + QAS**: Clustering reduces the scan set; QAS parallelizes scanning what remains. Complementary.
- **Clustering + MVs**: You can cluster a Materialized View differently from its base table. If queries need the data ordered by `region` but the base table is clustered by `date`, create an MV clustered by `region`.

## Search Optimization Service (SOS)

### When SOS Pays Off

SOS is cost-effective when:
- The table is large (millions of micro-partitions)
- Queries use **equality predicates** (`=`, `IN`), **substring/regex** (`LIKE`, `ILIKE`, `RLIKE`), or **VARIANT path access**
- Point lookups are frequent (hundreds-thousands per day)
- Current query times are unacceptable for the use case (e.g., interactive dashboards)

SOS is not helpful for:
- Range queries (`BETWEEN`, `>`, `<`) — use clustering instead
- Full table scans or non-selective queries
- Small tables where scans are already fast

### Supported Predicate Types for Optimization

| Predicate Type | Example | SOS Benefit |
|---------------|---------|-------------|
| Equality | `WHERE id = 123` | High — direct lookup via search access path |
| IN | `WHERE id IN (1, 2, 3)` | High — multiple point lookups |
| VARIANT equality | `WHERE payload:user_id::STRING = 'abc'` | High — avoids scanning all VARIANT data |
| ARRAY_CONTAINS | `WHERE ARRAY_CONTAINS(tags::VARIANT, 'premium')` | High — indexes array elements |
| ARRAYS_OVERLAP | `WHERE ARRAYS_OVERLAP(tags, ARRAY_CONSTRUCT('a','b'))` | High |
| LIKE / ILIKE | `WHERE name ILIKE '%smith%'` | Moderate-High — substring index |
| RLIKE | `WHERE email RLIKE '.*@example\\.com'` | Moderate — regex search access path |
| IS NULL / IS NOT NULL | `WHERE deleted_at IS NULL` | Moderate |
| Geospatial | `ST_WITHIN(geo_col, ...)` | Moderate — spatial index |

### Cost Estimation and ROI

Always estimate before enabling:

```sql
SELECT SYSTEM$ESTIMATE_SEARCH_OPTIMIZATION_COSTS('my_db.my_schema.events');
```

Returns projected storage cost and compute cost for building and maintaining the search access path. Compare this against the warehouse credits saved by faster queries.

**Enabling on specific columns (recommended):**
```sql
-- Enable SOS only for the columns that matter
ALTER TABLE events ADD SEARCH OPTIMIZATION ON EQUALITY(user_id), SUBSTRING(email);
```

Enabling on specific columns (rather than the whole table) reduces maintenance cost and storage.

### Monitoring SOS Effectiveness

```sql
-- SOS maintenance costs
SELECT table_name, SUM(credits_used) AS sos_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.SEARCH_OPTIMIZATION_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY sos_credits DESC;
```

Check `search_optimization_progress` in `SHOW TABLES` output — SOS does not accelerate queries until the search access path is fully built.

## Query Acceleration Service (QAS)

### When QAS Pays Off

QAS is cost-effective when:
- The warehouse handles **ad-hoc or variable workloads** with unpredictable query sizes
- Queries have **large scans with selective filters or aggregations**
- **Outlier queries** are slowing down the entire warehouse (QAS offloads their scan work)
- You want to avoid permanently sizing up the warehouse for occasional heavy queries

QAS is not helpful for:
- Very small scans (not enough partitions to parallelize)
- Queries with non-selective filters or very high-cardinality GROUP BY
- Queries with non-deterministic functions (SEQ, RANDOM)
- Workloads where all queries are uniformly heavy (just size up the warehouse instead)

### Identifying QAS Candidates

**Per-query estimation:**
```sql
SELECT PARSE_JSON(SYSTEM$ESTIMATE_QUERY_ACCELERATION('your-query-id-here'));
```

Returns `eligible`/`ineligible` status, estimated query times at various scale factors, and the reason for ineligibility if applicable.

**Per-warehouse analysis:**
```sql
-- Warehouses with the most QAS-eligible time in the last 7 days
SELECT warehouse_name,
       COUNT(query_id) AS eligible_queries,
       SUM(eligible_query_acceleration_time) AS total_eligible_time_sec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_ELIGIBLE
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_eligible_time_sec DESC;

-- Distribution of scale factors needed for a specific warehouse
SELECT upper_limit_scale_factor, COUNT(*) AS query_count
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_ELIGIBLE
WHERE warehouse_name = 'ANALYTICS_WH'
  AND start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY upper_limit_scale_factor
ORDER BY upper_limit_scale_factor;
```

### Configuring QAS

```sql
-- Enable QAS with default scale factor (8)
ALTER WAREHOUSE analytics_wh SET ENABLE_QUERY_ACCELERATION = TRUE;

-- Set custom scale factor (cost control)
ALTER WAREHOUSE analytics_wh SET
  ENABLE_QUERY_ACCELERATION = TRUE
  QUERY_ACCELERATION_MAX_SCALE_FACTOR = 4;

-- Unlimited scale factor (max acceleration, no cost cap)
ALTER WAREHOUSE analytics_wh SET
  ENABLE_QUERY_ACCELERATION = TRUE
  QUERY_ACCELERATION_MAX_SCALE_FACTOR = 0;
```

**Scale factor tuning:** The scale factor sets the maximum additional compute QAS can lease, as a multiplier of warehouse size. A scale factor of 4 on a Medium warehouse (4 credits/hour) means QAS can add up to 16 additional credits/hour. Start conservative (2-4), check `QUERY_ACCELERATION_HISTORY` for actual usage, and adjust.

**Multi-cluster note:** The scale factor applies to the entire warehouse. If using multi-cluster, consider increasing the scale factor proportionally since QAS is shared across all clusters.

### Monitoring QAS Costs

```sql
SELECT warehouse_name,
       SUM(credits_used) AS qas_credits,
       COUNT(DISTINCT query_id) AS accelerated_queries
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_ACCELERATION_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY qas_credits DESC;
```

## Materialized Views for Optimization

### When MVs Pay Off

MVs are cost-effective when:
- A query (or pattern of queries) runs **frequently** and the underlying data changes **infrequently**
- The query involves expensive **aggregations** (`SUM`, `COUNT`, `AVG`) over large datasets
- You need a **different clustering** on the same base table data
- You want to pre-flatten **semi-structured data** (VARIANT) to avoid repeated FLATTEN overhead
- Queries need a **subset of columns** from a very wide table

MVs are not cost-effective when:
- The base table changes rapidly (high maintenance cost)
- The query is rarely executed (cost of maintenance > saved compute)
- The query needs joins (MVs are single-table only)
- The query uses unsupported functions (window functions, UDFs, etc.)

### Optimization-Specific Patterns

**Pattern 1: Pre-aggregation for dashboards**
```sql
CREATE MATERIALIZED VIEW mv_daily_revenue AS
  SELECT date_trunc('day', order_date) AS order_day,
         product_category,
         SUM(revenue) AS total_revenue,
         COUNT(*) AS order_count
  FROM orders
  GROUP BY 1, 2;
```
Dashboard queries against the base `orders` table will be automatically rewritten to use this MV if they need the same or more restrictive grouping.

**Pattern 2: Alternative clustering**
```sql
CREATE MATERIALIZED VIEW mv_orders_by_customer
  CLUSTER BY (customer_id)
  AS SELECT * FROM orders WHERE order_status = 'ACTIVE';
```
The base `orders` table is clustered by `order_date`, but some queries filter by `customer_id`. This MV provides a differently-clustered copy.

**Pattern 3: Pre-flattened semi-structured data**
```sql
CREATE MATERIALIZED VIEW mv_event_details AS
  SELECT event_id,
         payload:user_id::STRING AS user_id,
         payload:event_type::STRING AS event_type,
         payload:timestamp::TIMESTAMP_NTZ AS event_ts
  FROM raw_events;
```
Queries filtering by `user_id` or `event_type` can now use standard column pruning instead of scanning all VARIANT data.

### Automatic Query Rewrite

The optimizer transparently rewrites base-table queries to use MVs when:
- The MV contains all columns and rows needed by the query
- The MV's filter subsumes the query's filter (range, OR, AND, IN subsumption)
- The MV's aggregation subsumes the query's aggregation

Check the Query Profile or EXPLAIN plan — the MV appears instead of the base table when rewrite occurs.

**If the optimizer is NOT using an available MV**, possible reasons:
- The base table's clustering is already efficient enough for the query
- The query needs columns or rows not in the MV
- The MV is not fully refreshed yet (check `is_invalid` in `SHOW MATERIALIZED VIEWS`)

### MV Cost Monitoring

```sql
SELECT table_name AS mv_name,
       SUM(credits_used) AS maintenance_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.MATERIALIZED_VIEW_REFRESH_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
GROUP BY table_name
ORDER BY maintenance_credits DESC;
```

If an MV's maintenance credits exceed the credits it saves in query acceleration, consider dropping it.

## Dynamic Tables for Optimization

Dynamic Tables (DTs) optimize *pipelines*, not individual queries. They replace hand-managed task-based ETL with declarative transformations that Snowflake orchestrates.

### When DTs Optimize Over Alternatives

| Previous Approach | DT Advantage |
|-------------------|-------------|
| Streams + Tasks for CDC pipelines | DTs eliminate manual orchestration. Declare the result; Snowflake manages the refresh schedule. |
| Task chains (DAGs) for multi-step transforms | DTs chain naturally (downstream DTs depend on upstream DTs). No DAG management. |
| Materialized Views needing joins | MVs are single-table. DTs support full SQL including joins, window functions, UDFs. |
| Periodic full-rebuild tables | DTs use **incremental refresh** when possible, processing only changed data. This can reduce compute 10-100x for insert-heavy workloads. |
| Over-frequent refresh schedules | DTs use `TARGET_LAG` — Snowflake refreshes only as often as needed to meet the freshness target, not on a fixed schedule. |

### TARGET_LAG for Cost Optimization

TARGET_LAG is the primary cost lever for Dynamic Tables:

- **Longer lag = lower cost**: A 1-hour lag refreshes ~24 times/day. A 1-minute lag may refresh ~1440 times/day. Set lag to the loosest freshness acceptable for the use case.
- **DOWNSTREAM lag**: `TARGET_LAG = DOWNSTREAM` means this DT refreshes only when a downstream DT needs it. Use this for intermediate layers that don't need their own freshness guarantee.

```sql
-- Outer-facing DT needs 5-minute freshness
CREATE OR REPLACE DYNAMIC TABLE gold_revenue
  TARGET_LAG = '5 minutes'
  WAREHOUSE = transform_wh
  AS SELECT ... FROM silver_orders JOIN silver_products ...;

-- Intermediate DT refreshes only when gold_revenue needs it
CREATE OR REPLACE DYNAMIC TABLE silver_orders
  TARGET_LAG = DOWNSTREAM
  WAREHOUSE = transform_wh
  AS SELECT ... FROM raw_orders;
```

### Incremental vs Full Refresh

DTs perform **incremental refresh** when the query structure allows it — processing only changed rows rather than recomputing from scratch. Incremental refresh is dramatically cheaper for insert-heavy workloads.

**Operators that support incremental refresh:** SELECT, WHERE, JOIN (inner, left, right, cross), GROUP BY with supported aggregates, UNION ALL, FLATTEN.

**Operators that force full refresh:** WINDOW functions, ORDER BY with LIMIT, non-deterministic functions, EXISTS/NOT EXISTS subqueries, certain complex CTEs.

Check whether a DT is refreshing incrementally:
```sql
SELECT name, refresh_mode
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY())
WHERE name = 'GOLD_REVENUE';
```

If `refresh_mode` is `FULL` when you expect `INCREMENTAL`, restructure the DT query to avoid the operators that force full refresh.

### DT Cost Monitoring

```sql
SELECT name,
       SUM(data_timestamp_diff) AS total_lag_sec,
       AVG(data_timestamp_diff) AS avg_lag_sec,
       SUM(statistics:numInsertedRows::NUMBER) AS total_rows_inserted,
       COUNT(*) AS refresh_count
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY(
  NAME => 'my_db.my_schema.gold_revenue',
  DATA_TIMESTAMP_RANGE_START => DATEADD('day', -7, CURRENT_TIMESTAMP())
))
GROUP BY name;
```

### Immutability Constraints

For tables with historical data that never changes, immutability constraints tell the DT refresh engine to skip those rows:

```sql
CREATE OR REPLACE DYNAMIC TABLE silver_orders
  TARGET_LAG = '5 minutes'
  WAREHOUSE = transform_wh
  AS SELECT * FROM raw_orders
  WHERE order_date > DATEADD('day', -90, CURRENT_DATE())
  -- Mark older partitions as immutable to reduce refresh scope
```

This is particularly effective for time-series data where only recent data changes.

## Feature Comparison: Cost Structure

| Feature | Storage Cost | Compute Cost | Cost Model | Minimum Edition |
|---------|-------------|--------------|------------|-----------------|
| **Clustering** | Indirect (reclustering creates new micro-partitions retained during Time Travel/Fail-safe) | Serverless (Automatic Clustering credits) | Continuous — proportional to DML volume on the table | Standard |
| **SOS** | Yes (search access paths) | Serverless (maintenance of access paths) | Continuous — proportional to DML volume | Enterprise |
| **QAS** | No | Per-second when active (billed separately from warehouse) | On-demand — only when queries are accelerated | Enterprise |
| **Materialized Views** | Yes (pre-computed result set) | Serverless (background refresh) | Continuous — proportional to base table DML | Enterprise |
| **Dynamic Tables** | Yes (full table) | Warehouse (user-managed) or serverless | Continuous — proportional to refresh frequency and data volume | Standard |

## Version & Status

- Clustering + Automatic Clustering: GA, Standard edition.
- Search Optimization Service: GA, Enterprise edition required.
- Query Acceleration Service: GA, Enterprise edition required.
- Materialized Views: GA, Enterprise edition required.
- Dynamic Tables: GA, Standard edition. Incremental refresh for most operators is GA. Immutability constraints are GA.
