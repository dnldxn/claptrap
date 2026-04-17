# ct-brainstorm

Invoke the `using-superpowers` and `brainstorming` skills after loading this file. Do not invoke `writing-plans` during this operation.

## Overrides

- Ignore any visual companion instructions.
- Read `.planning/ROADMAP.md` if it exists to determine the next `M##`; otherwise start at `M01`.
- Generate milestone and phase slugs using the shared slug rules in `../SKILL.md`.
- Before writing `DESIGN.md`, `RESEARCH.md`, `MILESTONE_SUMMARY.md`, or any phase summary files, ask whether to create a dedicated milestone branch and worktree.
- Use the `question` tool (or equivalent ask-user tool) to offer:
  - `Create dedicated worktree (Recommended)`: create branch `feature/M##-slug` from the default branch and worktree `.worktrees/M##-slug/`.
  - `Stay in current checkout`: write milestone files in the current repository checkout.
- If the user chooses the dedicated worktree:
  - Detect the default branch using the shared rules in `../SKILL.md`.
  - Create the branch and worktree before writing any milestone files.
  - Write all new milestone files inside `.worktrees/M##-slug/`.
  - Commit the new milestone files from inside that worktree after the documents are written.
- If the user stays in the current checkout, write the milestone files there and offer the same commit from the current checkout.
- Write the design doc to `<workspace-root>/.planning/milestones/M##-slug/DESIGN.md`.
- After the design is approved, create `<workspace-root>/.planning/milestones/M##-slug/MILESTONE_SUMMARY.md` from the [MILESTONE-SUMMARY template](../assets/MILESTONE-SUMMARY.md), including the chosen git workspace mode, branch, path, and base branch.
- Create phase summary files at `<workspace-root>/.planning/milestones/M##-slug/phases/P##-slug/PHASE_SUMMARY.md` from the [PHASE-SUMMARY template](../assets/PHASE-SUMMARY.md).
- Spawn parallel research subagents for major topics, then synthesize the results into `<workspace-root>/.planning/milestones/M##-slug/RESEARCH.md` from the [RESEARCH template](../assets/RESEARCH.md).
- Update `<workspace-root>/.planning/ROADMAP.md`: set Phase to `1 of Y (first-phase-slug)`, Status to `Ready to plan`, and reset Progress to `[░░░░░░░░░░] 0%`.
- Offer commit `brainstorm: M##-slug` in the workspace where the files were written.
