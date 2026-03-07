---
name: writing-plans
description: >
  Create concise, phased implementation plans for multi-step bugs, features, refactors, or approved specs.
  Use whenever the user asks to plan the implementation, break work into tasks or sprints, outline the steps,
  or turn requirements into an execution plan before coding.
---

# Writing Plans

Create a plan for an implementer with limited codebase context. Be explicit about files, dependencies, acceptance criteria, validation, risks, and rollback.

## Workflow

1. Review the approved requirements and relevant code context.
2. If the plan depends on an external library, API, framework, or service, fetch current docs before drafting.
3. Split the work into sprints that build on each other and end in a demoable increment.
4. Split each sprint into atomic, committable tasks.
5. After drafting, do a gotchas pass for missing steps, risky dependencies, edge cases, or ambiguity, then refine the plan if needed.

## Planning Rules

- Assume the implementer has very little project context.
- Prefer clear, concrete instructions over vague summaries.
- Use exact file paths whenever you can.
- Keep tasks small enough to complete independently.
- Include task dependencies so parallel work is possible.
- Call out migrations, config changes, backfills, permissions, rollout concerns, and rollback steps when relevant.

## Task Rules

Each task should be:
- atomic and committable
- specific about where the work happens
- clear about dependencies
- backed by concrete acceptance criteria
- paired with a validation method when useful

Bad: `Implement Google OAuth`

Good:
- `Add Google OAuth environment variables to config`
- `Create the OAuth callback route in src/routes/auth.ts`
- `Add the Google sign-in button to the login UI`

## Plan Template

```markdown
# [Feature Name] Implementation Plan

**Generated**: [Date]
**Estimated Complexity**: [Low/Medium/High]

## Overview
[Summary of the goals, tasks, and approach]

## Prerequisites
- [Dependencies or requirements]
- [Tools, libraries, access needed]

## Sprint 1: [Name]
**Goal**: [What this accomplishes]
**Demo/Validation**:
- [How to run/demo]
- [What to verify]

### Task 1.1: [Name]
- **Location**: [File paths]
- **Description**: [What to do]
- **Dependencies**: [Previous tasks]

### Task 1.2: [Name]
[...]

## Sprint 2: [Name]
[...]

## Validation Strategy
- [How to verify the full change]
- [What to confirm per sprint]

## Potential Risks & Gotchas
- [What could go wrong]
- [Mitigation strategies]
```

## Completion

- Save the plan to `docs/plans/YYYY-MM-DD-<feature-name>.md`.
- Share the saved path and a short summary of the sprints, major risks, and prerequisites.
- Do not implement the plan.
