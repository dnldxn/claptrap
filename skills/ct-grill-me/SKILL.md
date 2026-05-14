---
name: ct-grill-me
description: Invoke the existing `grill-me` Skill with modifications
---

> **OPERATION OVERRIDE**: The instructions in this file take precedence over conflicting instructions in any other Skills.

Invoke the `grill-me` Skill with the following modifications:
- Do **NOT** invoke the `caveman` Skill.  Stop Caveman.  Normal mode.

After the `grill-me` Skill is complete, and all of the questions have been answered, invoke the `brainstorming` Skill to finalize any open questions, then ask the user if they want to generate a new spec file.  The design file **MUST** be saved to `.planning/specs/YYYY-MM-DD-<topic>-spec.md`.
