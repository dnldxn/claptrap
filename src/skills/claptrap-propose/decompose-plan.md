# Decompose Design into One or more OpenSpec Change s

Analyze the design document and produce an ordered list of changes for user approval.

## Process

### 1. Identify components

Scan the design for discrete functional areas. Look for:
- Separate sections/features
- Distinct modules or layers (API, UI, data, etc.)
- Independent capabilities

### 2. Estimate scope

For each component:
- **Small**: single file, isolated, <50 lines
- **Medium**: 2-5 files, some dependencies, 50-200 lines
- **Large**: 5+ files, cross-cutting, 200+ lines

### 3. Decide: single or multiple changes?

**Single change** if:
- ≤3 medium components, OR
- ≤1 large component, OR
- Components are tightly coupled

**Multiple changes** if:
- >3 medium components, OR
- >1 large component, OR
- Clear parallel work opportunities

### 4. If single change

Present to user:
```
This design fits a single change: `<feature-slug>`
Approve? (y/n/rename)
```

Return: `[{ change_id: "<feature-slug>", description: "...", dependencies: [] }]`

### 5. If multiple changes

#### 5a. Group components

- Each change should be independently deployable/testable
- Minimize cross-change dependencies
- Group tightly coupled components together

#### 5b. Assign change-ids

Pattern: `<feature-slug>-<component-slug>`

Example: `auth-system-core`, `auth-system-oauth`, `auth-system-ui`

#### 5c. Map dependencies

- **Sequential**: B requires A to be complete first
- **Parallel**: A and B can be implemented independently

#### 5d. Present plan to user

```
## Proposed Change Plan

This design is large. Recommend splitting into N changes:

| # | Change ID | Description | Dependencies | Size |
|---|-----------|-------------|--------------|------|
| 1 | change-id-1 | Brief desc | None | Medium |
| 2 | change-id-2 | Brief desc | None (parallel) | Small |
| 3 | change-id-3 | Brief desc | #1, #2 | Large |

**Implementation order**: 1 → 2 (parallel) → 3
```

Stop and wait for user approval or edits.
