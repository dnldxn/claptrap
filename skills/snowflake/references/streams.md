# Snowflake Streams

Streams provide change data capture (CDC) on Snowflake objects. A stream records DML changes (inserts, updates, deletes) to a source object and exposes them as a queryable change table. Streams track changes on standard tables, views (including secure views), directory tables, dynamic tables, external tables, Iceberg tables, and event tables.

A stream stores only an **offset** — not a copy of the data. Querying returns the net changes between the offset and the current transactional time. The offset advances only when the stream is consumed in a DML transaction.

## Stream Types

| Type | Source Objects | Tracks | Behavior |
|------|---------------|--------|----------|
| **Standard** (default) | Standard tables, dynamic tables, Snowflake-managed Iceberg tables, directory tables, views | Inserts, updates, deletes (including truncates) | Joins inserted/deleted rows to produce net delta. A row inserted then deleted in the same interval disappears. |
| **Append-only** | Standard tables, dynamic tables, Snowflake-managed Iceberg tables, views | Inserts only | Ignores updates/deletes/truncates. Significantly more performant for insert-heavy workloads. |
| **Insert-only** | External tables, externally managed Iceberg tables | Inserts only (no-ops on deletes) | Tracks new files in cloud storage. Overwritten files treated as new inserts. |

Choose **standard** for full CDC (SCD Type 2, MERGE). Choose **append-only** for new-row-only workloads (events, logs) — avoids join overhead and allows truncating the source without polluting the stream. Choose **insert-only** for external/externally managed Iceberg tables.

## Syntax

### CREATE STREAM

```sql
CREATE [ OR REPLACE ] STREAM [ IF NOT EXISTS ] <name>
  [ COPY GRANTS ]
  ON { TABLE | VIEW | EXTERNAL TABLE | STAGE | DYNAMIC TABLE | EVENT TABLE } <source_name>
  [ { AT | BEFORE } ( { TIMESTAMP => <ts> | OFFSET => <diff> | STATEMENT => <id> | STREAM => '<name>' } ) ]
  [ APPEND_ONLY = TRUE | FALSE ]
  [ INSERT_ONLY = TRUE ]
  [ SHOW_INITIAL_ROWS = TRUE | FALSE ]
  [ COMMENT = '<string>' ]
  [ [ WITH ] TAG ( <tag_name> = '<tag_value>' [, ...] ) ]
```

Source-specific notes: `AT/BEFORE` and `APPEND_ONLY` apply to tables and views. `INSERT_ONLY` is for external tables and externally managed Iceberg tables. Directory table (`ON STAGE`) and event table streams support only `COMMENT`. Clone syntax: `CREATE STREAM <name> CLONE <source_stream>` (inherits offset).

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `APPEND_ONLY` | Track inserts only (tables & views). Much faster for ELT. | `FALSE` |
| `INSERT_ONLY` | Required for external/externally managed Iceberg tables. | `FALSE` |
| `SHOW_INITIAL_ROWS` | First read returns all pre-existing rows; subsequent reads return normal CDC. | `FALSE` |
| `AT / BEFORE` | Set offset via Time Travel. `STREAM => '<name>'` copies another stream's offset. | Current time |
| `COPY GRANTS` | Retain permissions on `CREATE OR REPLACE`. | — |

### ALTER STREAM

Limited to comment and tag changes. You **cannot** alter the source object, stream type, or offset. To change those, drop and recreate. Preserve the offset with `CREATE OR REPLACE STREAM ... AT(STREAM => '<old_stream>')`.

### Other DDL

`DROP STREAM`, `DESCRIBE STREAM`, and `SHOW STREAMS` work as expected. `SHOW STREAMS` output includes `stale`, `stale_after`, `mode`, `base_tables`, and `invalid_reason`.

## Metadata Columns

Every stream appends three columns to the source schema:

| Column | Type | Description |
|--------|------|-------------|
| `METADATA$ACTION` | VARCHAR | `INSERT` or `DELETE`. Updates appear as a DELETE + INSERT pair. |
| `METADATA$ISUPDATE` | BOOLEAN | `TRUE` if the row is part of an UPDATE pair. `FALSE` for pure inserts/deletes. |
| `METADATA$ROW_ID` | VARCHAR | Immutable row ID. Use to correlate DELETE/INSERT pairs. Not populated for directory-table streams. |

**Reconstructing updates:**

```sql
SELECT del.id, del.amount AS old_amount, ins.amount AS new_amount
FROM my_stream del
JOIN my_stream ins ON del.METADATA$ROW_ID = ins.METADATA$ROW_ID
WHERE del.METADATA$ACTION = 'DELETE' AND ins.METADATA$ACTION = 'INSERT'
  AND del.METADATA$ISUPDATE = TRUE AND ins.METADATA$ISUPDATE = TRUE;
```

## Examples

### Standard stream with MERGE consumption

```sql
CREATE STREAM orders_cdc ON TABLE raw_orders;

MERGE INTO dim_orders t
USING orders_cdc s ON t.order_id = s.order_id
WHEN MATCHED AND s.METADATA$ACTION = 'DELETE' AND s.METADATA$ISUPDATE = FALSE
  THEN DELETE
WHEN MATCHED AND s.METADATA$ACTION = 'INSERT' AND s.METADATA$ISUPDATE = TRUE
  THEN UPDATE SET t.customer_id = s.customer_id,
                  t.amount = s.amount,
                  t.status = s.status,
                  t.updated_at = s.updated_at
WHEN NOT MATCHED AND s.METADATA$ACTION = 'INSERT'
  THEN INSERT (order_id, customer_id, amount, status, updated_at)
       VALUES (s.order_id, s.customer_id, s.amount, s.status, s.updated_at);
```

### Append-only stream for event ingestion

```sql
CREATE STREAM new_events ON TABLE raw_events APPEND_ONLY = TRUE;

INSERT INTO fact_events (event_id, event_type, payload, created_at)
SELECT event_id, event_type, payload, created_at
FROM new_events WHERE METADATA$ACTION = 'INSERT';
```

### Stream-driven triggered task

```sql
CREATE STREAM inventory_changes ON TABLE raw_inventory;

CREATE TASK process_inventory
  TARGET_COMPLETION_INTERVAL = '5 MINUTES'
  WHEN SYSTEM$STREAM_HAS_DATA('inventory_changes')
AS
  MERGE INTO dim_inventory t
  USING inventory_changes s ON t.sku = s.sku
  WHEN MATCHED AND s.METADATA$ACTION = 'INSERT'
    THEN UPDATE SET t.qty = s.qty, t.updated_at = s.updated_at
  WHEN NOT MATCHED AND s.METADATA$ACTION = 'INSERT'
    THEN INSERT (sku, qty, updated_at) VALUES (s.sku, s.qty, s.updated_at);

ALTER TASK process_inventory RESUME;
```

View streams require change tracking on all underlying tables (`ALTER TABLE ... SET CHANGE_TRACKING = TRUE`) before stream creation. Use `SHOW_INITIAL_ROWS = TRUE` for bootstrapping new downstream tables. Preserve an offset when recreating: `CREATE OR REPLACE STREAM ... AT(STREAM => '<old_stream>')`.

## Behavior & Internals

### Offset mechanics

- The offset sits between two **table versions**. Each committed DML creates a new version.
- **Querying** a stream does not advance the offset. Only DML consumption (INSERT, MERGE, UPDATE, DELETE, CTAS, COPY INTO) advances it.
- The offset advances at **transaction commit** to the transaction's start timestamp.
- All statements in an explicit transaction see the same stream snapshot (**repeatable-read isolation**). The stream locks during DML, preventing concurrent advancement.
- Create **separate streams per consumer** — a consumed stream's data is gone for the next reader.

```sql
BEGIN;
  INSERT INTO target_a SELECT * FROM my_stream WHERE category = 'A';
  INSERT INTO target_b SELECT * FROM my_stream WHERE category = 'B';
COMMIT;  -- offset advances once; both statements saw same data
```

### Change tracking

Creating the first stream on a table auto-enables change tracking (hidden metadata columns). For views, enable it on **both** the view and all underlying tables — either via a role that owns both, or with explicit `ALTER ... SET CHANGE_TRACKING = TRUE`.

### CHANGES clause

`SELECT ... FROM <table> CHANGES(INFORMATION => DEFAULT) AT(...)` provides CDC data **without advancing an offset**. Useful for ad-hoc inspection. Supports `APPEND_ONLY` mode and explicit `END(...)` bounds. Requires change tracking. Not supported on directory or external tables.

### Cost model

Streams have **no direct compute cost**. Costs come from:
- **Storage**: Extended retention for staleness prevention; hidden change-tracking columns.
- **Compute**: Querying/consuming uses warehouse compute. Standard streams cost more than append-only (join overhead).
- **Cloud services**: `SYSTEM$STREAM_HAS_DATA` evaluations incur nominal charges.

## Staleness

A stream becomes **stale** when its offset falls outside the source table's data retention period. Stale streams cannot be read and must be recreated.

### Retention extension

If `DATA_RETENTION_TIME_IN_DAYS` < 14, Snowflake auto-extends retention up to `MAX_DATA_EXTENSION_TIME_IN_DAYS` (default 14). This extension applies only while the stream exists unconsumed and incurs additional storage.

| `DATA_RETENTION_TIME_IN_DAYS` | `MAX_DATA_EXTENSION_TIME_IN_DAYS` | Must consume within |
|-------------------------------|-----------------------------------|---------------------|
| 14 | 0 | 14 days |
| 1 | 14 | 14 days |
| 0 | 90 | 90 days |

`stale_after` = last consumption time + MAX(DATA_RETENTION, MAX_DATA_EXTENSION). Monitor via `SHOW STREAMS` (`stale`, `stale_after` columns).

### Preventing staleness

1. **Consume regularly** before the `stale_after` timestamp.
2. **Call `SYSTEM$STREAM_HAS_DATA`** — even on empty streams, this extends retention.
3. **Handle false positives** with a no-op DML: `CREATE TEMPORARY TABLE _unused AS SELECT * FROM my_stream WHERE 1=0;`
4. **Increase `MAX_DATA_EXTENSION_TIME_IN_DAYS`** for infrequently consumed streams.
5. **Streams on shared tables/secure views** do not auto-extend retention — consume more frequently.

## SYSTEM$STREAM_HAS_DATA

```sql
SELECT SYSTEM$STREAM_HAS_DATA('my_db.my_schema.my_stream');
```

- Avoids false negatives but **can return false positives** (e.g., rows inserted then deleted between offsets).
- **View streams** have higher false-positive rates — checks underlying table versions, not filtered results.
- Calling on an empty stream **prevents staleness** by extending retention.
- When it returns TRUE but the stream is empty, consume with a no-op DML to reset it.

## Limitations & Gotchas

**Source objects:**
- Standard/append-only streams not supported on externally managed Iceberg tables or partitioned external tables — use insert-only.
- Standard streams cannot track geospatial data — use append-only.
- Not supported on materialized views.
- View streams require projections, filters, inner/cross joins, or UNION ALL only — no GROUP BY, DISTINCT, LIMIT, QUALIFY, non-FROM subqueries, or UDFs.

**Offset & consumption:**
- Querying alone never advances the offset — only DML consumption does.
- One stream = one consumer. Create separate streams for parallel consumers.
- Schema changes (e.g., adding NOT NULL) between offset and current time can break queries.

**Staleness traps:**
- `CREATE OR REPLACE` on the source table makes all its streams stale (history reset).
- Dropping/recreating the source severs streams even if the new table has the same name.
- Renaming the source does **not** break streams (follows the object, not the name).
- Cloning a database/schema: cloned stream's unconsumed records are inaccessible.

**Tasks:**
- Only one task should consume a given stream — multiple tasks cause race conditions.
- False positives from `SYSTEM$STREAM_HAS_DATA` cause unnecessary task runs; handle the empty-stream case.
- Triggered tasks on view streams fire on any underlying table change, even if the view filters it out.

**Other:**
- Streams have no Time Travel or Fail-safe — dropped streams are gone permanently.
- Non-deterministic view functions (`CURRENT_DATE`, `RANDOM()`) produce non-deterministic stream results.
- View joins can amplify changes — one source insert may produce many stream rows.
- Directory-table streams do not populate `METADATA$ROW_ID`.

## Best Practices

**Design:** Use append-only streams for insert-only workloads (events, staging, COPY INTO). Create one stream per consumer. Use `SHOW_INITIAL_ROWS = TRUE` for bootstrapping. Prefer streams over `CHANGES` for production pipelines.

**Consumption:** Wrap multi-statement consumption in explicit transactions for atomic offset advancement. Always filter on `METADATA$ACTION`. Guard tasks with `WHEN SYSTEM$STREAM_HAS_DATA(...)`.

**Staleness:** Set `MAX_DATA_EXTENSION_TIME_IN_DAYS` proportional to consumption frequency. Monitor `stale_after` in `SHOW STREAMS` and alert when it approaches. Consume shared/secure-view streams more frequently.

**Performance:** Append-only streams on large tables are orders of magnitude faster. Avoid `SELECT *` from standard streams on high-update tables — project only needed columns. Truncating after append-only consumption has zero overhead; standard streams generate DELETE records.

**Stream + task patterns:** Triggered tasks (no SCHEDULE, `WHEN SYSTEM$STREAM_HAS_DATA(...)`) fire within seconds of data arrival. Scheduled tasks with a WHEN guard are better for cost-conscious workloads. The task's implicit autocommit advances the offset.

## Security & Privileges

| Action | Privileges Needed |
|--------|-------------------|
| Create stream on table | `CREATE STREAM` on schema + `SELECT` on table |
| Create stream on view | `CREATE STREAM` on schema + `SELECT` on view |
| Create stream on directory table | `CREATE STREAM` on schema + `USAGE` (external stage) or `READ` (internal stage) |
| Create stream on external table | `CREATE STREAM` on schema + `SELECT` on external table |
| Query a stream | `SELECT` on stream + `SELECT` on source (or USAGE/READ on stage) |
| Enable change tracking | `OWNERSHIP` on the table/view |

Creating the first stream on a table auto-enables change tracking. If the creating role does not own the table, the owner must enable change tracking manually first.

## Documentation & Resources

- [Streams Overview](https://docs.snowflake.com/en/user-guide/streams-intro) — Concepts, offset mechanics, and stream types
- [CREATE STREAM](https://docs.snowflake.com/en/sql-reference/sql/create-stream) — Full syntax reference for all source object types
- [Stream Staleness & Data Retention](https://docs.snowflake.com/en/user-guide/streams-manage) — Staleness prevention and monitoring
