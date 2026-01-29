# Tasks Hints (Design + Specs -> tasks.md)

Use this file as guidance when generating:
`openspec/changes/<change-id>/tasks.md`

## Non-negotiables

- The first line of tasks.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Tasks MUST be checkboxes and MUST be numbered (1.1, 1.2, 2.1, ...).
- Include verification tasks that map back to Acceptance Criteria and spec scenarios.

## Extraction Rules

| Input | Tasks Output | Transformation |
|-------|-------------|----------------|
| Architecture Overview -> Components | Task subtasks | Each component -> subtasks for implementation + wiring |
| Architecture Overview -> Package Structure | File tasks | Each directory/file -> explicit creation/edit task |
| Specs scenarios | Verification tasks | Each scenario -> at least one verification step |
| Acceptance Criteria | Verification tasks | Each criterion -> explicit verification checkbox |

## Minimum required groups

Your tasks.md MUST contain a final group:

```markdown
## N. Testing & Verification

- [ ] N.1 Verify all acceptance criteria from design.md
- [ ] N.2 Verify all scenarios from specs
- [ ] N.3 Run `/opsx:verify` after implementation
```
