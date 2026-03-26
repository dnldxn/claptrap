# Snowflake Optimization: Compute & Warehouses

How to right-size warehouses, choose between Gen 1 and Gen 2, configure multi-cluster scaling, and optimize auto-suspend/resume behavior. This reference focuses on compute cost and throughput optimization — not on general warehouse administration.

## Warehouse Sizing

### The Sizing Principle

Snowflake warehouses scale linearly: each size-up doubles compute resources and credits per hour. The key insight is that **doubling the warehouse size halves the runtime for most scan-heavy queries**, so the total credit cost stays roughly the same. What you gain is *latency*.

| Size | Credits/Hour | Relative Compute |
|------|-------------|-----------------|
| X-Small | 1 | 1× |
| Small | 2 | 2× |
| Medium | 4 | 4× |
| Large | 8 | 8× |
| X-Large | 16 | 16× |
| 2X-Large | 32 | 32× |
| 3X-Large | 64 | 64× |
| 4X-Large | 128 | 128× |
| 5X-Large | 256 | 256× |
| 6X-Large | 512 | 512× |

**When sizing up saves money:** If a query on a Small warehouse runs for 10 minutes, it may run for 5 minutes on a Medium — same credit cost, but frees the warehouse sooner for other work and reduces queuing.

**When sizing up wastes money:** Queries that are not compute-bound (e.g., waiting on locks, compilation-bound, or result-cache hits) do not benefit from a larger warehouse.

### Right-Sizing Approach

1. **Baseline**: Run representative workloads on the current warehouse size. Record `TOTAL_ELAPSED_TIME`, `BYTES_SCANNED`, and spill metrics from `QUERY_HISTORY`.
2. **Test one size up and one size down**: Re-run the same workloads. Compare elapsed time and total credits consumed.
3. **Check spill**: If the current size shows `BYTES_SPILLED_TO_REMOTE_STORAGE > 0`, sizing up will likely improve performance *and* save credits by eliminating remote spill.
4. **Check queuing**: If `QUEUING_OVERLOAD_TIME > 0`, the warehouse is at capacity. Either size up, enable multi-cluster, or spread workloads.

```sql
-- Find warehouses where queries are spilling to remote storage
SELECT warehouse_name, warehouse_size,
       COUNT(*) AS query_count,
       SUM(bytes_spilled_to_remote_storage) / POWER(1024, 3) AS total_gb_remote_spill,
       AVG(total_elapsed_time) / 1000 AS avg_elapsed_sec
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND bytes_spilled_to_remote_storage > 0
GROUP BY warehouse_name, warehouse_size
ORDER BY total_gb_remote_spill DESC;
```

### Workload Isolation

Use separate warehouses for workloads with different characteristics:

| Workload Type | Warehouse Strategy |
|--------------|-------------------|
| **ETL/ELT batch** | Dedicated warehouse, sized to the largest transform. Auto-suspend aggressively (60s). |
| **BI/Dashboard** | Dedicated warehouse, multi-cluster for concurrency. Higher auto-suspend (300-900s) to preserve cache. |
| **Ad-hoc/Data Science** | Separate warehouse. Consider QAS for unpredictable large scans. |
| **dbt runs** | Dedicated warehouse (or per-model warehouses for large projects). Size for the heaviest model. |
| **Serverless Tasks** | No warehouse needed — Snowflake auto-sizes. Use `SERVERLESS_TASK_MIN/MAX_STATEMENT_SIZE` to bound costs. |

Mixing workloads on a single warehouse leads to either over-provisioning (wasted credits) or queuing (slow queries).

## Gen 1 vs Gen 2 Warehouses

Gen 2 is an updated warehouse architecture with faster hardware and software optimizations. Gen 2 became the default for new organizations in most regions starting mid-2025.

### Key Differences

| Aspect | Gen 1 | Gen 2 |
|--------|-------|-------|
| **Hardware** | Original Snowflake compute nodes | Newer hardware (faster CPUs, more memory, NVMe) |
| **Optimized operations** | Baseline | Enhanced DELETE, UPDATE, MERGE, and table scan performance |
| **Concurrency** | Baseline | Improved — can process more concurrent queries per cluster |
| **Credit rate** | Standard | Higher per-hour rate (see Snowflake Service Consumption Table) |
| **Net cost for scan-heavy queries** | Baseline | Usually lower — queries finish faster, offsetting the higher rate |
| **Availability** | All regions | All regions except AWS EU (Zurich), AWS Africa (Cape Town), GCP ME Central2 (Dammam), Azure US Gov Virginia |
| **Max size** | Up to 6X-Large | Up to 4X-Large (5XL/6XL not available) |

### When to Use Gen 2

Gen 2 is likely beneficial when:

- The workload is **scan-heavy** (large table scans, data-intensive joins, aggregations over billions of rows).
- Queries involve heavy **DELETE, UPDATE, or MERGE** operations — Gen 2 has specific optimizations for these.
- You need **better throughput** on a fixed warehouse size (Gen 2 handles more concurrent work per cluster).
- You are already on **4X-Large or smaller** (Gen 2 does not support 5XL/6XL).

Gen 2 is *not* beneficial when:

- Queries are **sub-second or very short** — the per-credit rate increase may not be offset by the speedup.
- The workload is **compilation-bound** (cloud-services layer) rather than execution-bound.
- You rely on **5X-Large or 6X-Large** warehouse sizes (not available in Gen 2).

### Identifying Gen 2 Candidates

Use this query to find warehouses where Gen 2 would likely help:

```sql
-- Warehouses with high scan volume and execution time (Gen 2 candidates)
SELECT warehouse_name, warehouse_size,
       COUNT(*) AS query_count,
       SUM(bytes_scanned) / POWER(1024, 4) AS total_tb_scanned,
       AVG(execution_time) / 1000 AS avg_exec_sec,
       SUM(bytes_spilled_to_local_storage + bytes_spilled_to_remote_storage) / POWER(1024, 3) AS total_gb_spill,
       SUM(credits_used_cloud_services) AS cloud_svc_credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
  AND warehouse_name IS NOT NULL
GROUP BY warehouse_name, warehouse_size
HAVING total_tb_scanned > 1   -- warehouses scanning >1 TB/month
ORDER BY total_tb_scanned DESC;
```

**Good Gen 2 candidates** have:
- High `total_tb_scanned` (scan-heavy workloads)
- High `avg_exec_sec` (long-running queries that would benefit from faster execution)
- Non-trivial spill (Gen 2's faster hardware reduces spill probability)
- Low `cloud_svc_credits` relative to total credits (i.e., the workload is execution-bound, not compilation-bound)

**Poor Gen 2 candidates** have:
- Low scan volumes with many short queries (e.g., thousands of <1s lookups)
- High cloud-services credits relative to execution credits (compilation-bound)

### Migration Strategy

1. **Test first**: Create a Gen 2 warehouse of the same size. Run representative workloads against both. Compare elapsed times and credits.
2. **Convert in-place** (preferred): `ALTER WAREHOUSE my_wh SET GENERATION = '2';` — can be done while running; existing queries finish on Gen 1, new queries use Gen 2.
3. **Cost consideration during conversion**: While existing Gen 1 queries are still running, both Gen 1 and Gen 2 compute resources are billed. Convert during low-traffic periods or suspend first to avoid double billing.
4. **Rollback**: `ALTER WAREHOUSE my_wh SET GENERATION = '1';` — can always switch back.
5. **Replication note**: If you use account replication, ensure all secondary regions support Gen 2 before converting. Gen 2 warehouses may fail to resume in regions that don't support them.

```sql
-- Convert to Gen 2 (recommended: GENERATION clause)
ALTER WAREHOUSE analytics_wh SET GENERATION = '2';

-- Convert to Gen 2 (alternative: RESOURCE_CONSTRAINT clause)
ALTER WAREHOUSE analytics_wh SET RESOURCE_CONSTRAINT = STANDARD_GEN_2;

-- Check current generation
SHOW WAREHOUSES LIKE 'analytics_wh';
-- Look at the "resource_constraint" column in the output
```

## Multi-Cluster Warehouses

Multi-cluster warehouses automatically add clusters when concurrency demand increases, then remove them when demand drops.

### When to Use

- Dashboard/BI workloads with many concurrent users
- API-serving workloads with unpredictable concurrency
- Any warehouse where `QUEUING_OVERLOAD_TIME > 0` in QUERY_HISTORY

### Configuration for Optimization

| Parameter | Optimization Guidance |
|-----------|---------------------|
| `MIN_CLUSTER_COUNT` | Set to 1 for cost optimization (clusters scale to zero beyond the first). Set higher if startup latency for new clusters is unacceptable. |
| `MAX_CLUSTER_COUNT` | Set based on peak concurrency needs. Each additional cluster doubles the concurrency capacity at the cost of additional credits. |
| `SCALING_POLICY` | **STANDARD** (default): Adds clusters proactively to minimize queuing. Better for latency-sensitive workloads. **ECONOMY**: Waits until queuing builds up before adding clusters. Saves 20-30% credits but accepts some queuing. |

```sql
-- Multi-cluster warehouse optimized for BI
CREATE WAREHOUSE bi_wh
  WAREHOUSE_SIZE = 'MEDIUM'
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 4
  SCALING_POLICY = 'STANDARD'
  AUTO_SUSPEND = 300;
```

### Monitoring Multi-Cluster Effectiveness

```sql
-- Check how often additional clusters are needed
SELECT warehouse_name, cluster_number,
       SUM(credits_used) AS credits_used
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time > DATEADD('day', -30, CURRENT_TIMESTAMP())
  AND warehouse_name = 'BI_WH'
GROUP BY warehouse_name, cluster_number
ORDER BY cluster_number;
```

If cluster 2+ is rarely used, your max cluster count is higher than needed. If the max cluster is frequently active, consider increasing it or sizing up.

## Auto-Suspend & Auto-Resume

Auto-suspend and auto-resume are the simplest and most impactful cost controls for warehouses.

### Auto-Suspend Optimization

| Setting | Use Case |
|---------|----------|
| **60 seconds** | ETL/batch warehouses with predictable, bursty workloads. Saves maximum credits between runs. |
| **120-300 seconds** | General-purpose warehouses. Balances cache preservation with cost. |
| **600-900 seconds** | BI/dashboard warehouses where cache hit rates matter. Keeps data in the warehouse SSD cache longer. |
| **0 (never suspend)** | Only for continuously active warehouses. Rare — usually a mistake. |

**The 60-second minimum**: Snowflake charges a 60-second minimum each time a warehouse resumes. If your workload triggers frequent suspend/resume cycles (e.g., a query every 90 seconds with auto-suspend at 60s), you pay the 60-second minimum repeatedly. In this case, increase auto-suspend to avoid the resume penalty.

```sql
-- Detect warehouses with excessive resume cycles
SELECT warehouse_name,
       COUNT(CASE WHEN event_name = 'RESUME_WAREHOUSE' THEN 1 END) AS resume_count,
       COUNT(CASE WHEN event_name = 'SUSPEND_WAREHOUSE' THEN 1 END) AS suspend_count
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY
WHERE timestamp > DATEADD('day', -7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
HAVING resume_count > 100   -- more than ~14 resumes/day
ORDER BY resume_count DESC;
```

### Auto-Resume

Auto-resume is enabled by default and should almost always stay enabled. Disabling it means queries will fail if the warehouse is suspended, which is only appropriate for warehouses that should be manually managed (e.g., a dedicated large warehouse for monthly batch runs).

## Resource Monitors

Resource monitors are guardrails, not optimization tools — but they prevent runaway costs while you optimize:

```sql
-- Create a monitor that alerts at 80% and suspends at 100%
CREATE RESOURCE MONITOR monthly_limit
  WITH CREDIT_QUOTA = 10000
  TRIGGERS
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND_IMMEDIATE;

-- Assign to a warehouse
ALTER WAREHOUSE analytics_wh SET RESOURCE_MONITOR = monthly_limit;

-- Assign to the account (all warehouses)
ALTER ACCOUNT SET RESOURCE_MONITOR = monthly_limit;
```

## Version & Status

- Gen 2 standard warehouses: GA (2025). Default for new organizations in most regions since mid-2025.
- Gen 2 not available for sizes 5X-Large and 6X-Large, or for Snowpark-optimized warehouses.
- `GENERATION` clause: recommended over `RESOURCE_CONSTRAINT` for specifying Gen 2.
- Multi-cluster warehouses: GA. Available in Standard edition and above.
- `WAREHOUSE_EVENTS_HISTORY`: GA in ACCOUNT_USAGE.
