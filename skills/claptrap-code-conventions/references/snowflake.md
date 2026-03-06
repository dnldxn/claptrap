---
description: 'Snowflake SQL coding conventions and guidelines'
---

# Snowflake SQL Coding Conventions and Guidelines

## Style & Formatting
- Keywords: Use uppercase for SQL keywords (e.g., `SELECT`, `FROM`, `WHERE`).
- Identifiers: Use lowercase for table names, column names, aliases, and functions (e.g., `customer_id`, `order_date`).
- Keyword Placement: Place SQL keywords at the beginning of lines for better visibility.
- Indentation: Use 4 spaces for indentation; align clauses for better readability.
- Line Length: Keep lines ≤ 125 characters; break long lines at logical points (e.g., after commas, before `AND`/`OR`).
- Commas: Place commas at the end of lines in lists (e.g., in `SELECT`, `FROM`, `WHERE` clauses).
- Trailing Commas: A trailing comma at the end of a `SELECT` list (e.g., `SELECT col1, col2, col3,`) is valid Snowflake syntax. This makes adding or removing columns easier and produces cleaner diffs.
- SELECT Clause: List each column on a new line, indented one level, except for very short lists (≤75 characters).
- Joins: Use explicit `JOIN` syntax instead of commas in the `FROM` clause; prefer `INNER JOIN`, `LEFT JOIN`, etc.
- WHERE and ON Clauses: Each condition should be on its own line, indented for clarity.  The first condition should be on the line after the WHERE or ON keyword, unless there is only one condition.  AND/OR should be at the beginning of the line.
- CTEs: Use Common Table Expressions (CTEs) to break down complex queries to improve readability.
- Aliases: Single-letter or short table aliases are OK.
- Comments: Use comments to explain complex logic or decisions; prefer inline comments for short notes and block comments for longer explanations.
- Use `GROUP BY ALL` instead of `GROUP BY a, b, c`

## Query Structure
- Avoid subqueries in the `SELECT` clause; use CTEs or joins instead.
- ON clause conditions should focus on join logic; filtering conditions should go in the WHERE clause.
- Column Alias Reuse: Snowflake allows column aliases to be referenced later in the same `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, and `ORDER BY` clauses (e.g., `SELECT col1 + col2 AS total, total * 0.1 AS tax FROM t WHERE total > 100`). Leverage this to reduce duplicated expressions within a query.

## Performance
- Use appropriate clustering keys to optimize query performance.
- Avoid `SELECT *`; specify only the columns needed.
- Use filters in the `WHERE` clause to limit data early in the query.
- Analyze query execution plans to identify and address performance bottlenecks.

## Comments
- Comments explain **why**, not what. Prefer readable SQL over comments.
- Use inline comments sparingly; prefer self-explanatory SQL.
- Separate primary/major sections with section headers, for example:
```sql
-----------------------------------------------------------------------------------------------------------------------
-- Section Name
-----------------------------------------------------------------------------------------------------------------------
```

## Snowflake Queries in Python
- When writing Snowflake SQL queries within Python code, use triple quotes (`"""`) for multi-line SQL strings.
- Use f-string formatting to insert variables.
- Follow Python coding conventions for the surrounding code, while adhering to Snowflake SQL conventions within the SQL strings.
- Indent SQL code within the triple quotes for readability.

## Examples
```sql
    SELECT customer_id, order_date, total_amount
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.order_date >= CURRENT_DATE() - 7
    GROUP BY ALL
    ORDER BY o.order_date DESC
```

```sql
    SELECT customer_id, order_date, total_amount
    FROM orders o
    INNER JOIN customers c ON 
        o.customer_id = c.id
        AND o.email = c.email
    WHERE
        o.order_date >= CURRENT_DATE() - 7
        AND o.status = 'completed' 
```

```python
query = f"""
    SELECT customer_id, order_date, total_amount
    FROM orders
    WHERE order_date >= {start_date}
"""
cursor.execute(query)
```
