# Design: Example Feature (Workflow Demo)
Date: 2026-01-28
Status: Draft
Author: Example Author

## Intent

Demonstrate the complete `design.md` structure produced by `/claptrap-brainstorm`, including optional technical sections used to generate OpenSpec artifacts.

## Scope

### In Scope
- Provide a concrete example of every required design section.
- Include a realistic package structure and core types example.
- Include acceptance criteria that can be converted into spec scenarios.
- Include key decisions in the full Decision/Options/Choice/Rationale format.

### Out of Scope
- Implementing any code.
- Creating OpenSpec artifacts (proposal/specs/tasks) in this repo.

## Acceptance Criteria

- [ ] The design includes at least 2 acceptance criteria with clear, testable outcomes.
- [ ] The design includes a package structure tree that can be converted into file-creation tasks.
- [ ] The design includes at least one core type definition in TypeScript.

## Architecture Overview

### Components
- `ExampleService`: Owns the primary business operation.
- `ExampleRepository`: Persists and retrieves Example data.
- `ExampleCLI`: Provides a simple user entry point for the operation.

### Package Structure

```
packages/example/
├── src/
│   ├── index.ts
│   ├── cli.ts
│   ├── service.ts
│   └── repository.ts
└── package.json
```

### Core Types

```typescript
export interface ExampleRecord {
  id: string
  status: "new" | "processed"
}
```

### Data Flow

1. User invokes CLI command.
2. CLI calls `ExampleService.process(...)`.
3. Service fetches an `ExampleRecord` from repository.
4. Service updates status and writes back to repository.

## Key Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Persistence approach | In-memory only, file-based JSON, DB-backed | file-based JSON | Simple demo with persistence and minimal dependencies |

## Open Questions

- [ ] Should the repository support batch operations?

## Next Steps

1. Review this design document
2. Run `/claptrap-propose .claptrap/designs/example-feature/design.md` to generate OpenSpec artifacts
3. Review and approve proposal/specs/tasks
4. Implement via `/opsx:apply`

## OpenSpec Proposals

<!-- Auto-populated by /claptrap-propose -->
- (none yet)
