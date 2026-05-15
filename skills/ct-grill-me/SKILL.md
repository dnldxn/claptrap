---
name: ct-grill-me
description: Use when starting a new design or spec to interview the user, answer open questions, and draft a specification.
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

**REQUIRED SUB-SKILL:** Use `grill-me` with the following modifications:
- Do **NOT** invoke the `caveman` Skill.  Stop Caveman.  Normal mode.  Full prose helps with clarity during the design phase.

After the `grill-me` reaches shared understanding, invoke the `brainstorming` Skill to finalize any remaining open questions. Then ask the user whether to save a new spec file. If the user declines, stop without invoking `ct-manage-state-file`. If the user agrees, save the spec to `.planning/specs/YYYY-MM-DD-<topic>-spec.md`.

After saving the spec, invoke `ct-manage-state-file` to record the current state and note which spec file was written.

Proposal:
$ARGUMENTS
