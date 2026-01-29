# Spec Hints (Design -> specs/**/spec.md)

Use this file as guidance when generating capability specs under:
`openspec/changes/<change-id>/specs/<capability>/spec.md`

## Non-negotiables

- The first line of every spec.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Every scenario MUST use WHEN/THEN bullets.

## Extraction Rules

| Design Section | Spec Section | Transformation |
|----------------|--------------|----------------|
| Acceptance Criteria | Requirements | Each checkbox criterion -> one Requirement |
| Acceptance Criteria | Scenarios | Convert into WHEN/THEN scenarios (testable, observable outcomes) |
| Key Decisions | Constraints | Add as scenario conditions or explicit requirement notes |
| Architecture Overview -> Core Types | References | Link back to design for type/interface definitions |

## Scenario format (required)

```markdown
- **WHEN** <precondition or trigger>
- **THEN** <expected observable outcome>
```
