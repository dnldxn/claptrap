# Proposal Hints (Design -> proposal.md)

Use this file as guidance when generating `openspec/changes/<change-id>/proposal.md`.

## Non-negotiables

- The first line of proposal.md MUST be:
  `<!-- Source: ../../../.claptrap/designs/<feature-slug>/design.md -->`
- Preserve scope discipline: do not add requirements that are not in the design.

## Extraction Rules

| Design Section | Proposal Section | Transformation |
|----------------|------------------|----------------|
| Intent | Why | Direct copy or light summarization (2-3 sentences) |
| Scope -> In Scope | What Changes | Summarize to 2-3 sentences |
| Intent + Scope | Capabilities | Extract kebab-case capability slugs + one-line descriptions |
| Scope -> Out of Scope | Non-Goals | Direct copy |
| Key Decisions | Impact -> Key Decisions | Summarize each decision (keep rationale) |
| Architecture Overview -> Components | Impact -> Code Changes | List impacted areas/files/modules |

## Required Sections (proposal.md must include these headings)

- `## Why`
- `## What Changes`
- `## Capabilities`
- `## Non-Goals`
- `## Impact`
- `## Source`

## Source section (must be present)

Include a link back to the design document:

`Full design: [design.md](../../../.claptrap/designs/<feature-slug>/design.md)`
