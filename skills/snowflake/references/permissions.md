# Snowflake Permissions & Role-Based Access Control

Snowflake combines Discretionary Access Control (DAC), Role-Based Access Control (RBAC), and User-Based Access Control (UBAC) into a single framework. Privileges are granted to **roles**, roles are granted to **users** (or other roles), and users act through their **active role** in a session. Every securable object is owned by exactly one role (the one that created it, unless transferred), and access is denied by default unless an explicit grant exists.

This reference focuses on how the permission model works conceptually — when to use which system roles, how role inheritance flows, how to audit access, and how to design role hierarchies that scale. It does not enumerate every privilege on every object type; consult the official privileges reference for that level of detail.

## Core Concepts

### The Three Pillars

| Model | How it works | When it applies |
|-------|-------------|-----------------|
| **DAC** | The role that owns an object can grant access to that object to other roles. | Default behavior in regular schemas. |
| **RBAC** | Privileges are granted to roles; roles are granted to users. Users act through their active role. | The primary mechanism for organizing access. |
| **UBAC** | Privileges can be granted directly to users (not to roles). | Only considered when `USE SECONDARY ROLES` is set to `ALL`. Useful for narrow, user-specific grants. |

### Securable Object Hierarchy

Objects nest inside containers. To access an inner object you need privileges on the outer containers too.

```
Organization
  └── Account
        ├── Warehouse
        ├── Database
        │     └── Schema
        │           ├── Table / View / Materialized View
        │           ├── Stage / File Format / Sequence
        │           ├── Function / Procedure
        │           ├── Stream / Task / Pipe
        │           ├── Dynamic Table / Iceberg Table
        │           └── ... (all other schema-scoped objects)
        ├── User
        ├── Role
        ├── Integration
        └── Resource Monitor
```

**Container access rule:** To query a table, you need at minimum USAGE on the database, USAGE on the schema, and SELECT on the table. Forgetting the container grants is the most common permissions mistake.

### Privileges at a High Level

Rather than listing every privilege for every object, understand the privilege categories:

| Category | Examples | Pattern |
|----------|----------|---------|
| **Container access** | `USAGE` on databases, schemas, warehouses, integrations | Required to "enter" a container and see or use its contents. |
| **Data read** | `SELECT` on tables/views/streams | Read data from an object. |
| **Data write** | `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` on tables | Mutate data in an object. |
| **Object lifecycle** | `CREATE <type>` at the account, database, or schema level | Create new objects of a given type. |
| **Object management** | `MODIFY`, `MONITOR`, `OPERATE` on warehouses/tasks/dynamic tables | Change settings, observe state, start/stop/suspend. |
| **Ownership** | `OWNERSHIP` on any object | Full control — alter, drop, and grant/revoke access. Automatically assigned to the creating role. |
| **Global / Account** | `MANAGE GRANTS`, `MONITOR USAGE`, `EXECUTE TASK`, `CREATE ACCOUNT`, etc. | Account-wide administrative capabilities. |
| **Policy & governance** | `APPLY MASKING POLICY`, `APPLY ROW ACCESS POLICY`, `APPLY TAG`, etc. | Attach governance objects to tables/views/columns. |

For the exhaustive per-object privilege matrix, see the official docs: https://docs.snowflake.com/en/user-guide/security-access-control-privileges

### OWNERSHIP — The Special Privilege

Every object has exactly one owning role. OWNERSHIP provides full control: the ability to ALTER, DROP, and GRANT/REVOKE on the object. When you CREATE an object, OWNERSHIP goes to your active role. You can transfer it:

```sql
GRANT OWNERSHIP ON TABLE mydb.myschema.my_table TO ROLE data_engineer
  COPY CURRENT GRANTS;
```

In **regular schemas**, the owning role decides who else can access the object. In **managed access schemas**, only the schema owner or a role with MANAGE GRANTS can make grant decisions — even the object owner cannot.

## Roles

### System-Defined Roles

Snowflake creates these roles automatically. They cannot be dropped, and their built-in grants cannot be revoked.

```
ACCOUNTADMIN           ← top of the system hierarchy; encapsulates SECURITYADMIN + SYSADMIN
  ├── SECURITYADMIN    ← holds MANAGE GRANTS; inherits USERADMIN
  │     └── USERADMIN  ← holds CREATE USER, CREATE ROLE
  └── SYSADMIN         ← holds CREATE WAREHOUSE, CREATE DATABASE; intended parent of all custom roles
PUBLIC                 ← automatically granted to every user and every role (pseudo-role)
ORGADMIN               ← organization-level management (separate from the account hierarchy)
```

| Role | Purpose | Key privileges |
|------|---------|---------------|
| **ACCOUNTADMIN** | Top-level account governance. Billing, parameters, resource monitors. | Encapsulates SECURITYADMIN + SYSADMIN. **Not** a superuser — still needs grants on objects. |
| **SECURITYADMIN** | Grant management, user/role oversight. | `MANAGE GRANTS` (can grant/revoke any privilege on any object). Inherits USERADMIN. |
| **USERADMIN** | User and role lifecycle. | `CREATE USER`, `CREATE ROLE`. Can manage users/roles it owns. |
| **SYSADMIN** | Object creation and infrastructure. | `CREATE WAREHOUSE`, `CREATE DATABASE`. Should be the parent of all custom roles. |
| **PUBLIC** | Baseline access for everyone. | Everything granted to PUBLIC is available to every user and every role. Use sparingly. |
| **ORGADMIN** | Organization-level tasks (account management, org usage). | Separate hierarchy; not a child of ACCOUNTADMIN. |

**Best practices for ACCOUNTADMIN:**
- Assign to 2+ people (password reset procedures take up to 2 business days otherwise).
- Require MFA for all ACCOUNTADMIN holders.
- Never set ACCOUNTADMIN as any user's default role.
- Don't create objects with ACCOUNTADMIN — use SYSADMIN or a custom role.
- Don't use ACCOUNTADMIN in automated scripts.

### Custom Roles

Create with `CREATE ROLE` (requires USERADMIN or a role with CREATE ROLE). Custom roles start in isolation — you must explicitly grant them to users and wire them into the role hierarchy.

**Critical:** If a custom role is not granted (directly or transitively) to SYSADMIN, then system administrators cannot manage the objects it owns. Always connect custom roles up to SYSADMIN.

### Database Roles

Scoped to a single database. Useful for:
- **Delegated database management:** Database owners can create and manage database roles independently.
- **Data sharing:** Segment shared objects by granting subsets to different database roles.

Limitations: Database roles cannot be activated directly in a session — they must be granted to an account role first. Granting a database role to an account role implicitly grants USAGE on the containing database.

### Role Types Summary

| Type | Scope | Can be activated? | Typical use |
|------|-------|-------------------|-------------|
| **Account role** | Entire account | Yes (primary or secondary role) | General RBAC |
| **Database role** | One database | No — grant to account role | Database-scoped access, data sharing |
| **Instance role** | One class instance | No — grant to account role | Snowflake class method access |
| **Application role** | Snowflake Native App | No — grant to account role | Native App consumer access |
| **Service role** | SPCS service endpoints | No — grant to account/db role | Container service endpoint access |

## Role Hierarchy & Privilege Inheritance

When Role A is granted to Role B, Role B **inherits all privileges** of Role A. This is transitive — if Role C is granted Role B, then Role C inherits both Role B's and Role A's privileges.

```
          ┌─────────────┐
          │  SYSADMIN   │   ← inherits everything below
          └──────┬──────┘
                 │
          ┌──────┴──────┐
          │  func_admin │   ← inherits access_read + access_write
          └──────┬──────┘
           ┌─────┴─────┐
    ┌──────┴──┐  ┌─────┴──────┐
    │access_rw│  │ access_r   │
    └─────────┘  └────────────┘
```

**Key rules:**
- Owning a role (holding OWNERSHIP on it) does **not** inherit the role's privileges. Inheritance flows only through the grant hierarchy.
- A role inherits privileges from all roles granted to it, recursively.
- The PUBLIC role's privileges are available to every role (since PUBLIC is implicitly granted to all).

### Access Roles vs. Functional Roles Pattern

A scalable RBAC design separates **access roles** (permission bundles on objects) from **functional roles** (business personas assigned to users):

```
Users          Functional Roles       Access Roles           Objects
─────          ────────────────       ────────────           ───────
alice   ──►    analyst          ──►   db_sales_r       ──►  sales.*  (SELECT)
bob     ──►    accountant       ──►   db_sales_rw      ──►  sales.*  (SELECT, INSERT, UPDATE, DELETE)
                                 ──►   db_hr_r          ──►  hr.*     (SELECT)
```

1. Grant object-level privileges to **access roles** (e.g., `db_sales_r`, `db_sales_rw`).
2. Grant access roles to **functional roles** (e.g., `analyst`, `accountant`).
3. Grant functional roles to **SYSADMIN** so system admins can manage the objects.
4. Grant functional roles to **users**.

This is the Snowflake-recommended approach. See: https://docs.snowflake.com/en/user-guide/security-access-control-considerations

## Grant Management

### Core Syntax

```sql
-- Grant a privilege on an object to a role
GRANT SELECT ON TABLE mydb.myschema.my_table TO ROLE analyst;

-- Grant a role to another role (build hierarchy)
GRANT ROLE analyst TO ROLE sysadmin;

-- Grant a role to a user
GRANT ROLE analyst TO USER alice;

-- Revoke a privilege
REVOKE INSERT ON TABLE mydb.myschema.my_table FROM ROLE analyst;

-- Transfer ownership
GRANT OWNERSHIP ON SCHEMA mydb.myschema TO ROLE data_engineer
  COPY CURRENT GRANTS;
```

### Future Grants

Define privileges that auto-apply to new objects of a given type, so you don't have to grant after every CREATE:

```sql
-- All new tables in a schema auto-get SELECT granted to analyst
GRANT SELECT ON FUTURE TABLES IN SCHEMA mydb.myschema TO ROLE analyst;

-- All new schemas in a database
GRANT USAGE ON FUTURE SCHEMAS IN DATABASE mydb TO ROLE analyst;
```

Future grants only affect objects created **after** the grant. For existing objects, use `GRANT ... ON ALL <type> IN ...`.

### Managed Access Schemas

In a managed access schema, object owners lose the ability to grant access — only the schema owner or a role with MANAGE GRANTS can. This centralizes permission management and is useful for tightly governed datasets.

```sql
CREATE SCHEMA mydb.governed_schema WITH MANAGED ACCESS;
```

## Auditing Permissions

### Key Metadata Views & Commands

| Source | What it shows | Latency | Use when |
|--------|--------------|---------|----------|
| `SHOW GRANTS ON <object>` | All privileges granted on a specific object | Real-time | Quick check: "who can access this table?" |
| `SHOW GRANTS TO ROLE <role>` | All privileges and roles granted to a role | Real-time | Quick check: "what can this role do?" |
| `SHOW GRANTS TO USER <user>` | All roles granted to a user | Real-time | Quick check: "what roles does this user have?" |
| `SHOW GRANTS OF ROLE <role>` | All users and roles to which a role is granted | Real-time | "Who/what inherits this role?" |
| `SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_ROLES` | Historical privilege grants to roles (including revoked) | Up to 2 hours | Audit trails, compliance, trend analysis |
| `SNOWFLAKE.ACCOUNT_USAGE.GRANTS_TO_USERS` | Historical role grants to users (including revoked) | Up to 2 hours | Audit trails, user access history |
| `SNOWFLAKE.ACCOUNT_USAGE.ROLES` | Role metadata (created, deleted, owner, etc.) | Up to 2 hours | Inventory of all roles, including dropped |
| `SNOWFLAKE.INFORMATION_SCHEMA.APPLICABLE_ROLES` | Roles visible to the current user and their grant relationships | Real-time | Lightweight hierarchy check within session |
| `SNOWFLAKE.INFORMATION_SCHEMA.ENABLED_ROLES` | Roles currently active in the session | Real-time | Debugging "why can't I access this?" |

### GRANTS_TO_ROLES Columns (Key Fields)

| Column | Description |
|--------|-------------|
| `PRIVILEGE` | The privilege granted (e.g., `SELECT`, `USAGE`, `OWNERSHIP`). |
| `GRANTED_ON` | Object type the privilege applies to (e.g., `TABLE`, `DATABASE`, `ROLE`). |
| `NAME` | Name of the object. |
| `GRANTED_TO` | Grantee type: `ACCOUNT ROLE`, `DATABASE_ROLE`, `USER`, etc. |
| `GRANTEE_NAME` | Name of the role or user receiving the privilege. |
| `GRANTED_BY` | Role that authorized the grant. Empty for SYSTEM-granted privileges. |
| `DELETED_ON` | Non-null if the grant was revoked (enables historical analysis). |

### GRANTS_TO_USERS Columns (Key Fields)

| Column | Description |
|--------|-------------|
| `ROLE` | The role granted to the user. |
| `GRANTEE_NAME` | The user who received the grant. |
| `GRANTED_BY` | Role that authorized the grant. |
| `DELETED_ON` | Non-null if the grant was revoked. |

### Walking the Role Inheritance Chain

One of the most common audit questions is: "How does user X end up with access to object Y?" The answer requires tracing through the role hierarchy. Roles can be nested many levels deep, so you need a recursive query.

The following query discovers a user's direct roles, then recursively walks the parent-role chain to show every path through which privileges flow. This is especially useful for diagnosing unexpected access or verifying that principle-of-least-privilege is maintained.

```sql
-- Replace these
SET target_user = 'MY_USER';
SET target_role = NULL;              -- optional if you already know the starting role
SET target_object_type = 'WAREHOUSE';
SET target_object_name = 'MY_WH';

-- Step 1: capture direct roles for the user
SHOW GRANTS TO USER IDENTIFIER($target_user);

CREATE OR REPLACE TEMP TABLE user_direct_roles AS
SELECT
    "name"         AS granted_role,   -- role name granted to the user
    "granted_to"   AS granted_to,
    "grantee_name" AS grantee_name
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "granted_to" = 'USER';

-- Step 2: recursively walk upward through parent roles
WITH RECURSIVE role_chain AS (
    -- direct roles assigned to the user
    SELECT
        granted_role         AS current_role,
        granted_role         AS starting_role,
        granted_role::STRING AS path,
        0                    AS depth
    FROM user_direct_roles

    UNION ALL

    -- find parent roles that inherit child-role privileges
    SELECT
        g.grantee_name              AS current_role,   -- parent role
        rc.starting_role,
        rc.path || ' -> ' || g.grantee_name,
        rc.depth + 1
    FROM role_chain rc
    JOIN snowflake.account_usage.grants_to_roles g
        ON  g.granted_on = 'ROLE'
        AND g.name       = rc.current_role             -- child role name
        AND g.deleted_on IS NULL
)
SELECT DISTINCT *
FROM role_chain
ORDER BY starting_role, depth, current_role;
```

**How to read the output:**
- Each row shows a node in the inheritance chain.
- `starting_role` is the user's direct role that initiated the chain.
- `path` shows the full inheritance path (e.g., `ANALYST -> SYSADMIN -> ACCOUNTADMIN`).
- `depth` indicates how many hops from the direct grant.
- Use the `current_role` values to then check `GRANTS_TO_ROLES` for specific object privileges.

**Performance note:** The `GRANTS_TO_ROLES` view has up to 2 hours of latency. For real-time results on small hierarchies, use `SHOW GRANTS OF ROLE <role>` iteratively instead.

### Quick Diagnostic Queries

```sql
-- What privileges does a role have on a specific database?
SHOW GRANTS TO ROLE my_role;
-- then filter by database in RESULT_SCAN

-- Who owns a specific table?
SHOW GRANTS ON TABLE mydb.myschema.my_table;
-- look for OWNERSHIP in the privilege column

-- What roles does a user have?
SHOW GRANTS TO USER my_user;

-- What future grants exist in a schema?
SHOW FUTURE GRANTS IN SCHEMA mydb.myschema;

-- Find all grants on an object (including through role hierarchy)
-- Combine SHOW GRANTS ON <object> with the role-chain query above
```

## Limitations & Gotchas

- **ACCOUNTADMIN is not a superuser.** It can only access objects if it (or a role below it in the hierarchy) has been explicitly granted privileges. If a custom role is not connected to SYSADMIN, ACCOUNTADMIN cannot manage those objects.
- **Orphaned custom roles.** If you create a role and don't grant it to SYSADMIN (or another connected role), its objects become invisible to administrators. Always wire custom roles into the hierarchy.
- **Container grants are required.** Having SELECT on a table is useless without USAGE on the database and schema. This is the #1 "why can't I query this table?" issue.
- **MANAGE GRANTS impersonates the owner.** When a role with MANAGE GRANTS issues a grant, the `GRANTED_BY` column shows the object owner, not the role that actually ran the command.
- **GRANTS_TO_ROLES latency.** The ACCOUNT_USAGE view can lag up to 2 hours behind real-time state. Use `SHOW GRANTS` commands for immediate results.
- **Query results are user-scoped.** You cannot view another user's query results, even with ACCOUNTADMIN. This is a security feature, not a permission gap.
- **Cloned objects:** When you clone a database/schema/table, existing grants on the source are replicated to the clone. But the clone is a new object with its own grant lifecycle going forward.
- **Future grants vs. existing objects.** `GRANT ... ON FUTURE TABLES` only affects tables created after the grant. Don't forget `GRANT ... ON ALL TABLES IN SCHEMA` for existing objects.

## Best Practices

1. **Use the access-role / functional-role pattern.** Separate "what can be done" (access roles with object privileges) from "who does it" (functional roles assigned to users). This scales far better than granting privileges directly to user-facing roles.

2. **Always connect custom roles to SYSADMIN.** Grant every top-level functional role to SYSADMIN so the system hierarchy stays intact.

3. **Use future grants.** Set them at the schema (or database) level so new objects automatically inherit the correct permissions. Pair with `ON ALL ... IN SCHEMA` for bootstrapping existing objects.

4. **Prefer managed access schemas for sensitive data.** Centralizing grant authority prevents object owners from making unauthorized access decisions.

5. **Set meaningful default roles.** Each user should have a default role that matches their day-to-day work — never ACCOUNTADMIN.

6. **Audit regularly.** Use the ACCOUNT_USAGE grant views to detect privilege drift, orphaned roles, and over-permissioned service accounts.

7. **Apply least privilege.** Grant the minimum set of privileges needed. Prefer read-only access roles and only grant write where necessary.

8. **Don't grant to PUBLIC unless truly universal.** Anything granted to PUBLIC is available to every user and every role in the account.

## References

- Access Control Privileges (full per-object matrix): https://docs.snowflake.com/en/user-guide/security-access-control-privileges
- Access Control Considerations (best practices, role design): https://docs.snowflake.com/en/user-guide/security-access-control-considerations
- Access Control Overview (concepts, role types, hierarchy): https://docs.snowflake.com/en/user-guide/security-access-control-overview
- GRANTS_TO_ROLES view: https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles
- GRANTS_TO_USERS view: https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users
- SHOW GRANTS command: https://docs.snowflake.com/en/sql-reference/sql/show-grants
- Configuring Access Control (create roles, hierarchies, managed schemas): https://docs.snowflake.com/en/user-guide/security-access-control-configure
