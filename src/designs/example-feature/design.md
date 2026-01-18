# Design: Design Artifacts Directory
Date: 2026-01-16
Status: Draft
Author: Example Author

## Intent
Provide a consistent place to capture design exploration before writing OpenSpec
proposals, so brainstorm output is discoverable and reusable.

## Scope
### In Scope
- Add a top-level `designs/` directory for design artifacts.
- Provide a reusable template for future design docs.
- Include an example design that demonstrates each section.

### Out of Scope
- Updating existing commands to generate design files.
- Enforcing a specific diagram tool or format.

## Acceptance Criteria
- [ ] `designs/TEMPLATE.md` exists with all required sections.
- [ ] `designs/<feature-slug>/design.md` is the documented structure.
- [ ] Example design demonstrates realistic content for every section.

## Architecture Overview
### Components
- `designs/`: Root directory for all design exploration.
- `designs/TEMPLATE.md`: Standardized template for new designs.
- `designs/example-feature/`: Reference example for contributors.

### Data Flow Diagram
- Placeholder: add a simple flow diagram showing brainstorm -> design -> proposal.

## Key Decisions
| Choice | Rationale |
| --- | --- |
| Use `designs/<feature-slug>/design.md` | Keeps content grouped by feature. |
| Include a template | Reduces setup time and increases consistency. |

## Open Questions
- Should design documents be required before every proposal?

## Next Steps
- Create an OpenSpec proposal once the design is reviewed and accepted.
