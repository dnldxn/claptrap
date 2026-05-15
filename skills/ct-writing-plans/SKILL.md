---
name: ct-writing-plans
description: Use when writing implementation plans after a design or spec has been approved.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

**REQUIRED SUB-SKILL:** Use `writing-plans` with the following modifications:
- Plan files **MUST** be saved to `.planning/plans/YYYY-MM-DD-<spec-slug>-<order>-<plan-slug>.md`
- Derive `<spec-slug>` from the spec's title/header line (usually H1) as a short kebab-case visual hint only; do not record an authoritative spec-plan link.
- Use two-digit `<order>` values (`01`, `02`, ...).

After saving each plan file, invoke `ct-manage-state-file` to record the current state and note which plan file was written.

Spec:
$ARGUMENTS
