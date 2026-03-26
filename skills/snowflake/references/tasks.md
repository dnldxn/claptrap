# Snowflake Tasks

Tasks automate SQL execution on a schedule or in response to events. They are Snowflake's native job scheduler — use them for ELT pipelines, materialization, alerting, and any recurring or event-driven SQL workload. Tasks chain into **task graphs** (DAGs) with parallel branches, conditional logic, return-value passing, and a finalizer step.

## Syntax

### CREATE TASK

```sql
CREATE [ OR REPLACE ] TASK [ IF NOT EXISTS ] <name>
  [ WAREHOUSE = <string> ]                              -- user-managed compute
  [ USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = <string> ] -- serverless hint
  [ SCHEDULE = { '<num> { HOURS | MINUTES | SECONDS }'
               | 'USING CRON <expr> <time_zone>' } ]
  [ CONFIG = <json_string> ]
  [ OVERLAP_POLICY = { NO_OVERLAP | ALLOW_CHILD_OVERLAP | ALLOW_ALL_OVERLAP } ]
  [ USER_TASK_TIMEOUT_MS = <num> ]
  [ SUSPEND_TASK_AFTER_NUM_FAILURES = <num> ]
  [ TASK_AUTO_RETRY_ATTEMPTS = <num> ]
  [ TARGET_COMPLETION_INTERVAL = '<num> { HOURS | MINUTES | SECONDS }' ]
  [ SERVERLESS_TASK_MIN_STATEMENT_SIZE = '<size>' ]
  [ SERVERLESS_TASK_MAX_STATEMENT_SIZE = '<size>' ]
  [ ERROR_INTEGRATION = <integration_name> ]
  [ SUCCESS_INTEGRATION = <integration_name> ]
  [ FINALIZE = <root_task_name> ]
  [ COMMENT = '<string>' ]
  [ AFTER <predecessor> [ , <predecessor> , ... ] ]     -- child task in a DAG
  [ WHEN <boolean_expr> ]
  AS
    <sql>
```

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `WAREHOUSE` | Assigns a user-managed warehouse. Omit for serverless. | — |
| `SCHEDULE` | Interval (`'60 MINUTES'`) or cron (`'USING CRON ...'`). Required for root/standalone unless triggered. Children inherit from root. | — |
| `USER_TASK_TIMEOUT_MS` | Max runtime (ms). On root, applies to entire DAG; child-level overrides. | `3600000` |
| `SUSPEND_TASK_AFTER_NUM_FAILURES` | Auto-suspend after N consecutive failures. | `10` |
| `TASK_AUTO_RETRY_ATTEMPTS` | Auto-retry failed DAG run (root only, 0–30). | `0` |
| `OVERLAP_POLICY` | Controls DAG run concurrency (root only). | `NO_OVERLAP` |
| `TARGET_COMPLETION_INTERVAL` | Desired completion time. **Required** for serverless triggered tasks. | Next scheduled |
| `CONFIG` | JSON config accessible via `SYSTEM$GET_TASK_GRAPH_CONFIG()`. Root only. | — |
| `FINALIZE` | Designates this task as the finalizer for the named root task. | — |
| `AFTER` | Makes this a child task; runs after all listed predecessors succeed. Max 100. | — |

### ALTER TASK

```sql
ALTER TASK <name> RESUME | SUSPEND;
ALTER TASK <name> ADD AFTER <t1>[, <t2>];
ALTER TASK <name> REMOVE AFTER <t1>;
ALTER TASK <name> SET <property> = <value>;
ALTER TASK <name> UNSET <property>;
ALTER TASK <name> MODIFY AS <new_sql>;
ALTER TASK <name> MODIFY WHEN <boolean_expr>;
ALTER TASK <name> REMOVE WHEN;
ALTER TASK <name> SET FINALIZE = <root> | UNSET FINALIZE;
```

**Critical:** Suspend the root task before modifying any task in the DAG. Running instances complete before suspension takes effect.

### EXECUTE TASK

```sql
EXECUTE TASK <name>;                                          -- manual run
EXECUTE TASK <name> USING CONFIG = $${"env": "staging"}$$;    -- config override
EXECUTE TASK <name> RETRY LAST;                               -- retry from failure
```

Does **not** require the root to be resumed. Suspended children are skipped.

### Other DDL

`DROP TASK`, `DESCRIBE TASK`, `SHOW TASKS [ LIKE '<pattern>' ] [ IN SCHEMA ] [ ROOT ONLY ]` — standard DDL. `SHOW TASKS` returns state, schedule, predecessors, definition, condition, and more.

## Examples

### Serverless scheduled task

```sql
CREATE TASK hourly_aggregation
  SCHEDULE = '60 MINUTES'
  SUSPEND_TASK_AFTER_NUM_FAILURES = 5
AS
  INSERT INTO hourly_sales_summary
  SELECT DATE_TRUNC('hour', sold_at), SUM(amount)
  FROM raw_sales
  WHERE sold_at >= DATEADD('hour', -1, CURRENT_TIMESTAMP())
  GROUP BY 1;

ALTER TASK hourly_aggregation RESUME;
```

### Triggered task (stream-driven)

```sql
CREATE TASK process_new_orders
  TARGET_COMPLETION_INTERVAL = '15 MINUTES'
  WHEN SYSTEM$STREAM_HAS_DATA('orders_stream')
AS
  INSERT INTO order_facts
  SELECT order_id, customer_id, total, order_ts
  FROM orders_stream WHERE METADATA$ACTION = 'INSERT';

ALTER TASK process_new_orders RESUME;
```

Serverless triggered tasks omit `SCHEDULE` and require `TARGET_COMPLETION_INTERVAL`. Combine `SCHEDULE` + `WHEN` on user-managed warehouse tasks to poll on a schedule but skip when no data exists.

### Task graph (DAG) with parallel branches and finalizer

```sql
CREATE TASK pipeline_root
  SCHEDULE = '1 MINUTE'
  TASK_AUTO_RETRY_ATTEMPTS = 2
  SUSPEND_TASK_AFTER_NUM_FAILURES = 3
  CONFIG = $${"env": "prod", "output": "/data/prod/"}$$
AS
  BEGIN
    CALL SYSTEM$SET_RETURN_VALUE('root complete');
  END;

CREATE TASK load_customers AFTER pipeline_root AS
  INSERT INTO dim_customer SELECT * FROM stg_customer_stream;

CREATE TASK load_products AFTER pipeline_root AS
  INSERT INTO dim_product SELECT * FROM stg_product_stream;

-- Convergence — waits for both parents
CREATE TASK build_sales_fact AFTER load_customers, load_products AS
  INSERT INTO fact_sales
  SELECT c.customer_key, p.product_key, s.amount, s.sold_at
  FROM stg_sales_stream s
  JOIN dim_customer c ON s.cust_id = c.cust_id
  JOIN dim_product p ON s.prod_id = p.prod_id;

-- Finalizer — runs after all tasks, even on failure
CREATE TASK pipeline_finalizer FINALIZE = pipeline_root AS
  BEGIN
    LET root_id := (SELECT SYSTEM$TASK_RUNTIME_INFO('CURRENT_ROOT_TASK_UUID'));
    CALL SYSTEM$SEND_EMAIL('my_integration', 'team@co.com',
      'Pipeline finished', 'See Snowsight for details', 'text/plain');
  END;

SELECT SYSTEM$TASK_DEPENDENTS_ENABLE('pipeline_root');
ALTER TASK pipeline_root RESUME;
```

Use `SYSTEM$GET_PREDECESSOR_RETURN_VALUE('TASK_NAME')` in child WHEN clauses for conditional execution. The task name argument is **case-sensitive** — use uppercase for unquoted names.

## Behavior & Internals

### Compute models

| Model | When to use | Billing |
|-------|-------------|---------|
| **Serverless** | Few tasks, short/variable workloads, schedule adherence | Auto-sizes XSMALL–XXLARGE. Billed per compute-hour. |
| **User-managed warehouse** | Many concurrent tasks, predictable load, need > XXLARGE | You supply the warehouse. Billed by uptime (60s min). |

Tasks in the same DAG can mix compute models.

### Scheduling mechanics

- **Interval** (`'60 MINUTES'`): Timer starts at resume. Runs at resume + N×interval.
- **Cron** (`'USING CRON ...'`): Runs at wall-clock times per the expression.
- **Triggered** (no `SCHEDULE`, uses `WHEN SYSTEM$STREAM_HAS_DATA`): Fires when stream has change data. Min interval 30s (configurable to 10s via `USER_TASK_MINIMUM_TRIGGER_INTERVAL_IN_SECONDS`). A 12-hour health check fires automatically.

Under `NO_OVERLAP`, a scheduled run is **skipped** if the previous run is still executing.

### Overlap policies (root task only)

| Policy | Root overlaps? | Child overlaps? | Use case |
|--------|---------------|-----------------|----------|
| `NO_OVERLAP` (default) | No | No | Safe for most ELT |
| `ALLOW_CHILD_OVERLAP` | No | Yes | Fast root, slow children |
| `ALLOW_ALL_OVERLAP` | Yes | Yes | Only when concurrent runs are safe |

### WHEN clause evaluation

Evaluated in the **cloud services layer** (no warehouse). Supported: `SYSTEM$STREAM_HAS_DATA`, `SYSTEM$GET_PREDECESSOR_RETURN_VALUE` with comparisons, `AND`/`OR`/`NOT`. Cost is nominal; charges accumulate and apply to the next actual run. `PARSE_JSON` is **not** supported in WHEN.

### Task graph execution flow

1. Root fires (schedule, trigger, or `EXECUTE TASK`).
2. Immediate children with all predecessors satisfied run in parallel.
3. Multi-predecessor children wait for **all resumed predecessors** to succeed.
4. **Suspended** children are treated as succeeded — downstream tasks still run.
5. Any **failure** marks the entire DAG FAILED (unless `TASK_AUTO_RETRY_ATTEMPTS > 0`).
6. **Finalizer** runs last regardless of success/failure. Does not run if root was skipped by overlap policy.

### Versioning & execution identity

Resuming or executing a root task sets a **version** for the DAG. All tasks in that run use that version's definitions. Modify tasks while root is suspended; running instances finish on the old version.

Tasks run as a **system service** with the owner role's privileges — no human user associated. Use `EXECUTE AS USER <user>` for user-impersonation (requires `GRANT IMPERSONATE`).

## Limitations & Gotchas

- **DAG limits:** Max 1,000 tasks per DAG, 100 predecessors per child, 100 children per parent. Max 30,000 resumed tasks per account.
- **DAG constraints:** All tasks must share the same owner role and reside in the same schema. Transferring ownership of a single task severs DAG links — use `GRANT OWNERSHIP ... ON ALL TASKS IN SCHEMA`.
- **Renaming not supported.** Workaround: clone → update dependents → drop old.
- **Serverless max = XXLARGE.** Use user-managed warehouse for larger compute.
- **One task per stream.** Multiple consumers cause offset issues. Create separate streams per consumer.
- **AUTOCOMMIT must be TRUE.** Set explicitly on the task if disabled at account level.
- **DST traps:** Cron tasks at 1:00–2:59 a.m. local may fire twice or zero times during transitions. Use UTC.
- **`SYSTEM$STREAM_HAS_DATA` may return TRUE with no data** (false positive by design). It never returns FALSE when data exists.
- **`SYSTEM$GET_PREDECESSOR_RETURN_VALUE` is case-sensitive.** Use uppercase for unquoted task names.
- **`CREATE OR REPLACE TASK` re-creates the task** (new ID, suspended, serverless sizing history cleared). Prefer `CREATE OR ALTER TASK`.
- **Large task bodies may error.** Move complex logic into stored procedures.

## Best Practices

**Design:** Prefer triggered tasks over tight polling for unpredictable data arrival. Use serverless for short/variable workloads; user-managed warehouses for heavy, predictable loads. Keep task SQL simple — put complex logic in stored procedures. Use `CREATE OR ALTER TASK` to preserve state.

**DAG design:** Use a finalizer for cleanup/notifications/error handling. Pass state via `SYSTEM$SET_RETURN_VALUE` / `SYSTEM$GET_PREDECESSOR_RETURN_VALUE` rather than temp tables. Set `CONFIG` on root for environment settings; override with `EXECUTE TASK ... USING CONFIG` for testing. Set `TASK_AUTO_RETRY_ATTEMPTS` to 1–2 on root.

**Cost control:** Set `SUSPEND_TASK_AFTER_NUM_FAILURES` (3–5 recommended) and `USER_TASK_TIMEOUT_MS`. Bound serverless scaling with `SERVERLESS_TASK_MIN/MAX_STATEMENT_SIZE`. Align schedule frequency to actual data arrival. Monitor with `SERVERLESS_TASK_HISTORY()` or `METERING_HISTORY` (filter `service_type = 'SERVERLESS_TASK'`).

**Operations:** Resume all children in one call: `SELECT SYSTEM$TASK_DEPENDENTS_ENABLE('<root>');` then resume root. Test with `EXECUTE TASK` while root is suspended. Use `RETRY LAST` to re-run from failure (requires FAILED/CANCELED, unmodified DAG, within 14 days). Cancel running: `SELECT SYSTEM$USER_TASK_CANCEL_ONGOING_EXECUTIONS('<task>');`. Inspect DAG: `SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_DEPENDENTS('<root>', RECURSIVE => TRUE));`.

## Monitoring & Observability

| Function / View | Source | Purpose |
|----------------|--------|---------|
| `TASK_HISTORY()` | Information Schema | Recent run history — state, timing, errors |
| `TASK_HISTORY` | Account Usage | 365-day run history (up to 45 min latency) |
| `COMPLETE_TASK_GRAPHS` | Account Usage | DAG-level run history and duration |
| `SERVERLESS_TASK_HISTORY()` | Information Schema | Credit usage per serverless run |
| `SERVERLESS_TASK_HISTORY` | Account Usage | 365-day serverless credit history |
| `TASK_DEPENDENTS()` | Information Schema | List child/finalizer tasks for a root |
| `SYSTEM$TASK_RUNTIME_INFO()` | System function | In-task introspection (name, root UUID, etc.) |

```sql
-- Recent failures
SELECT name, state, error_message, scheduled_time, completed_time
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
  TASK_NAME => 'MY_TASK',
  SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP())
))
WHERE state = 'FAILED'
ORDER BY scheduled_time DESC;
```

Set `ERROR_INTEGRATION` / `SUCCESS_INTEGRATION` to push notifications to cloud messaging (SNS, Event Grid, Pub/Sub). At-least-once delivery; email/webhook not supported.

## Security & Privileges

| Action | Privileges needed |
|--------|------------------|
| Create task (user-managed) | `CREATE TASK` on schema + `USAGE` on warehouse |
| Create task (serverless) | `CREATE TASK` on schema + `EXECUTE MANAGED TASK` on account |
| Run/own a task | `EXECUTE TASK` on account + `EXECUTE MANAGED TASK` (serverless) + `USAGE` (warehouse) |
| Resume/suspend | `OWNERSHIP` or `OPERATE` on task |
| View history | `OWNERSHIP`, or `MONITOR EXECUTION` on account |
| Manual execute | `OWNERSHIP` or `OPERATE` on task |

```sql
CREATE ROLE taskadmin;
GRANT EXECUTE TASK ON ACCOUNT TO ROLE taskadmin;
GRANT EXECUTE MANAGED TASK ON ACCOUNT TO ROLE taskadmin;
GRANT ROLE taskadmin TO ROLE my_etl_role;
GRANT CREATE TASK ON SCHEMA my_db.my_schema TO ROLE my_etl_role;
GRANT USAGE ON WAREHOUSE etl_wh TO ROLE my_etl_role;
```

## Documentation & Resources

- [Tasks Overview](https://docs.snowflake.com/en/user-guide/tasks-intro) — Concepts, scheduling, and compute models
- [CREATE TASK](https://docs.snowflake.com/en/sql-reference/sql/create-task) — Full syntax reference with all parameters
- [Task Graphs (DAGs)](https://docs.snowflake.com/en/user-guide/tasks-graphs) — Multi-step workflows, finalizers, and return-value passing
