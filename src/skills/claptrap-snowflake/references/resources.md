# Snowflake Performance Optimization Resources

Curated external resources for deep-dives into specific optimization topics.

## Official Snowflake Documentation

### Core Performance Guides
- [Performance Optimization Overview](https://docs.snowflake.com/en/guides-overview-performance) -- Starting point for all performance topics
- [Exploring Query Execution Times](https://docs.snowflake.com/en/user-guide/performance-query-exploring) -- How to find and analyze slow queries
- [Query Profile](https://docs.snowflake.com/en/user-guide/ui-snowsight-activity) -- Detailed guide to reading the Query Profile UI

### Storage & Clustering
- [Micro-partitions & Data Clustering](https://docs.snowflake.com/en/user-guide/tables-clustering-micropartitions) -- How Snowflake stores data
- [Clustering Keys](https://docs.snowflake.com/en/user-guide/tables-clustering-keys) -- When and how to define clustering keys
- [Automatic Clustering](https://docs.snowflake.com/en/user-guide/tables-auto-reclustering) -- How background reclustering works
- [Optimizing Storage for Performance](https://docs.snowflake.com/en/user-guide/performance-query-storage) -- Storage-level optimizations
- [Search Optimization Service](https://docs.snowflake.com/en/user-guide/search-optimization-service) -- Point lookup acceleration

### Warehouses
- [Warehouse Overview](https://docs.snowflake.com/en/user-guide/warehouses-overview) -- Sizes, credit consumption, basics
- [Multi-cluster Warehouses](https://docs.snowflake.com/en/user-guide/warehouses-multicluster) -- Auto-scaling and concurrency
- [Snowpark-optimized Warehouses](https://docs.snowflake.com/en/user-guide/warehouses-snowpark-optimized) -- High-memory workloads
- [Optimizing Warehouses for Performance](https://docs.snowflake.com/en/user-guide/performance-query-warehouse) -- Right-sizing guide
- [Monitoring Warehouse Load](https://docs.snowflake.com/en/user-guide/warehouses-load-monitoring) -- Utilization monitoring
- [Reducing Queues](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-queue) -- Fixing concurrency issues
- [Resolving Memory Spillage](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-memory) -- Fixing spill issues

### SQL Reference
- [EXPLAIN](https://docs.snowflake.com/en/sql-reference/sql/explain) -- Execution plan syntax and output
- [QUALIFY](https://docs.snowflake.com/en/sql-reference/constructs/qualify) -- Window function filtering
- [Temporary & Transient Tables](https://docs.snowflake.com/en/user-guide/tables-temp-transient) -- Table types and trade-offs
- [Persisted Query Results (Caching)](https://docs.snowflake.com/en/user-guide/querying-persisted-results) -- Result cache behavior
- [Computing Distinct Counts](https://docs.snowflake.com/en/user-guide/querying-distinct-counts) -- APPROX_COUNT_DISTINCT and HLL
- [Querying Semi-structured Data](https://docs.snowflake.com/en/user-guide/querying-semistructured) -- VARIANT, FLATTEN, type casting
- [Materialized Views](https://docs.snowflake.com/en/user-guide/views-materialized) -- When and how to use

### Monitoring & Diagnostics
- [ACCOUNT_USAGE Views](https://docs.snowflake.com/en/sql-reference/account-usage) -- All account usage views
- [QUERY_HISTORY View](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) -- Query performance columns
- [WAREHOUSE_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history) -- Credit consumption
- [TABLE_STORAGE_METRICS](https://docs.snowflake.com/en/sql-reference/account-usage/table_storage_metrics) -- Storage analysis
- [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) -- Cost control and alerts

## Community Articles & Blogs

### Comprehensive Optimization Guides
- [Greybeam: Snowflake Query Optimization - 7 Tips for Faster Queries](https://blog.greybeam.ai/snowflake-query-optimization/) -- Covers disjunctive joins, range joins, ASOF JOIN, directed joins, dynamic pruning. Excellent practical examples.
- [SELECT: Snowflake Query Optimization - 16 Tips](https://select.dev/posts/snowflake-query-optimization) -- Detailed guide covering directed joins, range join optimization, ASOF JOIN, predicate pushdown, and advanced patterns.
- [Metaplane: How to Optimize Your Snowflake Query Performance](https://www.metaplane.dev/blog/optimize-your-snowflake-query-performance) -- Good overview of clustering, pruning, caching, and common anti-patterns.

### Warehouse Tuning
- [Riya Khandelwal: Snowflake Warehouse Tuning Guide](https://medium.com/@riyukhandelwal/snowflake-warehouse-tuning-guide-sizing-scaling-cost-optimization-1f943be9d0b4) -- Sizing, scaling, cost optimization with credit tables.

### Monitoring & Diagnostics
- [Arun Kumar: 10 Must-Know Queries to Observe Snowflake Performance](https://medium.com/@arunkumarmadhavannair/10-must-know-queries-to-observe-snowflake-performance-part-1-f927c93a7b04) -- Practical diagnostic SQL queries.

### Community Discussions
- [Reddit: How to Systematically Improve Performance of a Snowflake Query](https://www.reddit.com/r/snowflake/comments/1krwnvl/how_to_systematically_improve_performance_of_a/) -- Real-world optimization workflow discussion with community tips.

## Key ACCOUNT_USAGE Views for Performance

| View | Purpose | Latency | Retention |
|---|---|---|---|
| `QUERY_HISTORY` | Per-query performance metrics | 45 min | 365 days |
| `AGGREGATE_QUERY_HISTORY` | Aggregated query stats | 45 min | 365 days |
| `WAREHOUSE_LOAD_HISTORY` | Running/queued query load | 45 min | 365 days |
| `WAREHOUSE_METERING_HISTORY` | Credit consumption per warehouse | 45 min | 365 days |
| `TABLE_STORAGE_METRICS` | Table size and storage breakdown | 45 min | 365 days |
| `AUTOMATIC_CLUSTERING_HISTORY` | Reclustering costs and activity | 45 min | 365 days |
| `MATERIALIZED_VIEW_REFRESH_HISTORY` | MV refresh costs | 45 min | 365 days |
| `ACCESS_HISTORY` | What tables/columns were accessed | 45 min | 365 days |
| `LOCK_WAIT_HISTORY` | Transaction lock contention | 45 min | 365 days |
| `METERING_DAILY_HISTORY` | Daily credit summary | 45 min | 365 days |
