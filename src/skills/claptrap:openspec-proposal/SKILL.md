---
name: "claptrap:openspec-proposal"
description: Convert a well-defined idea into a formal OpenSpec proposal.md document, creating the change structure and validating the result.
---

# OpenSpec Create Proposal

## Overview

Convert a user's well-defined idea into a properly formatted OpenSpec `proposal.md` document. This skill handles the full workflow: generating the change name, creating the change directory via `openspec new change`, writing the proposal document, and validating the result.

## When to Use

Use this skill when you have a **well-defined idea** that needs to be formalized as an OpenSpec proposal. The input should already be thought through—this skill converts and formats, it does not brainstorm or refine.

For rough ideas that need exploration first, use the `brainstorming` skill instead.

## Skills

Invoke the `memory` skill to read and write memories as needed.

## Inputs

- A well-defined idea/prompt describing the desired change (provided by user)

## Process

### 1. Analyze the Input

Extract from the user's prompt:
- **Core motivation** (why this change?)
- **What will change** (capabilities, behavior, components)
- **Capabilities affected** (new vs. modified)
- **Impact scope** (files, APIs, dependencies)
- **Design decisions** ONLY INCLUDE IF the user input INCLUDES design or architecture decisions/recommendations
- **Implementation notes** ONLY INCLUDE IF the user input INCLUDES implementation notes/details/code snippets

### 2. Generate Change Name

Create a kebab-case change name from the input:
- Use 2-4 words that capture the essence
- Format: `verb-noun` or `verb-noun-qualifier`
- Examples: `add-rate-limiting`, `fix-auth-timeout`, `update-cache-strategy`

Also generate a short description (1 sentence, <80 chars).

### 3. Create the Change

Run the shell command:
```bash
openspec new change --description "<short-description>" <change-name>
```

This creates `openspec/changes/<change-name>/` with required files.

### 4. Write the Proposal

Write `openspec/changes/<change-name>/proposal.md` using the template at `templates/proposal.md`.

**Important:** The proposal must be **detailed and comprehensive**, capturing every point from the user's input. Do not summarize away details or reduce scope. The document length should be proportional to the input.  A complex, detailed prompt produces a thorough proposal; a brief prompt produces a concise one.

Transform the user's input into the formal structure:

| Section | Content |
|---------|---------|
| **Why** | Motivation, problem being solved, why now |
| **What Changes** | Specific capabilities, modifications, removals |
| **Capabilities > New** | List with kebab-case names and descriptions |
| **Capabilities > Modified** | Only if spec-level requirements change |
| **Impact** | Affected code, APIs, dependencies, systems |
| **Design Decisions** | INCLUDE ONLY IF the user input INCLUDES design or architecture decisions/recommendations |
| **Implementation Notes** | INCLUDE ONLY IF the user input INCLUDES implementation notes/details/code snippets |

### 5. Validate

Run the following OpenSpec shell command:
```bash
openspec validate --no-interactive --strict <change-name>
```

If warnings or errors occur (ignore design or implementation section warnings/errors):
- Fix the issues in `proposal.md`
- Re-validate until clean

## Output

- Change directory: `openspec/changes/<change-name>/`
- Proposal file: `openspec/changes/<change-name>/proposal.md`
- Validation: passing with no warnings/errors (ignore design or implementation section warnings/errors)

## Examples

### Example 1: Adding a Feature

**Input:**
> "Add rate limiting to the API. We're getting hammered by one client making too many requests. Should limit to 100 req/min per API key."

**Generated:**
- Change name: `add-api-rate-limiting`
- Description: "Add per-API-key rate limiting to prevent abuse"

**Proposal:**
```markdown
## Why

A single client is overwhelming the API with excessive requests, degrading service for other users. Rate limiting provides protection against abuse and ensures fair resource distribution.

## What Changes

Add request rate limiting enforced per API key. Requests exceeding the limit receive HTTP 429 responses with retry-after headers.

## Capabilities

### New Capabilities
- `api-rate-limiting`: Per-API-key request throttling with configurable limits and 429 responses

### Modified Capabilities
(none)

## Impact

- API gateway/middleware layer
- Response headers (adds Rate-Limit-*, Retry-After)
- etc...
```

### Example 2: Fixing a Bug

**Input:**
> "Auth tokens aren't being refreshed properly. Users get logged out after 1 hour even though refresh should extend the session."

**Generated:**
- Change name: `fix-token-refresh`
- Description: "Fix auth token refresh to properly extend sessions"

**Proposal:**
```markdown
## Why

Users are unexpectedly logged out after 1 hour because the token refresh mechanism fails to extend session lifetime. This creates friction and support tickets.

## What Changes

Fix the token refresh flow to properly update token expiration when refresh occurs.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `auth-tokens`: Fix refresh logic to correctly extend session lifetime

## Impact

- Auth service token refresh endpoint
- Token storage/caching layer
```

### Example 3: Architectural Change

**Input:**
> "Move from synchronous to async job processing for report generation. Reports are timing out for large datasets."

**Generated:**
- Change name: `async-report-generation`
- Description: "Convert report generation to async job processing"

**Proposal:**
```markdown
## Why

Large dataset reports timeout during synchronous generation. Async processing allows reports to complete in the background without blocking requests or hitting timeout limits.

## What Changes

Convert report generation from synchronous request handling to async job queue processing. Users receive a job ID and poll for completion.

## Capabilities

### New Capabilities
- `async-jobs`: Background job queue for long-running operations
- `report-status-api`: Endpoints to check report generation status

### Modified Capabilities
- `report-generation`: Changed from sync to async with job-based workflow

## Impact

- Report API endpoints (new async flow)
- Job queue infrastructure (new component)
- etc...
```

## Tone and Style

The proposal document should:
- Be **comprehensive** — capture every point, requirement, and detail from the user's input; nothing should be lost in translation
- Be **proportional** — the document length should mirror the complexity, scope, and length of the user's prompt (a detailed input deserves a detailed proposal; a concise input produces a concise proposal)
- Be **specific** — name concrete components, not vague abstractions
- Use **imperative mood** — "Add X", "Fix Y", not "This will add X"
- Capture **intent** — the "why" matters as much as the "what"
- **No summarizing away details** — if the user specified it, include it in the appropriate section
