---
name: ct-writing-plans
description: Use when writing implementation plans after a design or spec has been approved.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

**REQUIRED SUB-SKILL:** Use `writing-plans` with the following modifications:
- Plan files **MUST** be saved to `.planning/plans/YYYY-MM-DD-<order>-<spec-slug>-<plan-slug>.md`
- Use two-digit `<order>` values (`01`, `02`, ...).
- Identify the parent spec/design file before writing plans (normally under `.planning/specs/`).
- Derive `<spec-slug>` from the parent spec's title/header line (usually H1) as a short kebab-case visual hint.
- The parent spec/design linkage **MUST** be captured in `.planning/state.html` when each plan is written.

After saving each plan file, invoke `ct-manage-state-file` to record the current state and include:
- which plan file was written
- the parent spec/design file for that plan

When parent linkage is uncertain, make a best-effort guess and explicitly label it as inferred so `ct-manage-state-file` can mark the mapping as inferred in `.planning/state.html`.

Spec:
$ARGUMENTS
