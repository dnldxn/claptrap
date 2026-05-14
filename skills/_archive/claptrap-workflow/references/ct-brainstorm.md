# ct-brainstorm

Invoke the `using-superpowers` and `brainstorming` skills after loading this file. Do not invoke `writing-plans` during this operation.

## Overrides

- Ignore any visual companion instructions.
- Read `.planning/ROADMAP.md` if it exists to determine the next `M##`; otherwise start at `M01`.
- Generate milestone and phase slugs using the shared slug rules in `../SKILL.md`.
- Before writing milestone documents, ask whether to create and checkout branch `feature/M##-slug` from the default branch or stay on the current branch.
- If the user chooses the feature branch, create and checkout it first, then write the milestone documents there.
- Write the design doc to `.planning/milestones/M##-slug/DESIGN.md`.
- Spawn parallel research subagents for major topics, then synthesize the results into `.planning/milestones/M##-slug/RESEARCH.md` from the [RESEARCH template](../assets/RESEARCH.md).
- After the design is approved, create `.planning/milestones/M##-slug/MILESTONE_SUMMARY.md` from the [MILESTONE-SUMMARY template](../assets/MILESTONE-SUMMARY.md).
- Once `MILESTONE_SUMMARY.md` exists, record the current branch name and base branch there, even if the user chooses to leave the milestone docs uncommitted for now.
- Create phase plan files at `.planning/milestones/M##-slug/M##-P##-slug-PLAN.md` from the [PHASE-PLAN template](../assets/PHASE-PLAN.md). Fill in only the summary sections (Context through Definition of Done); leave the plan content placeholder for `ct-plan`.
- Once the milestone documents are drafted, update `.planning/ROADMAP.md`: add the milestone to Active Milestones, set Phase to `P01-first-phase-slug (1 of Y)`, Status to `Ready to plan`, reset Progress to `[░░░░░░░░░░] 0%`, and update Last Activity.

## Post-Brainstorm Options

Once the milestone documents are drafted, present these three options:

1. **Commit the milestone docs** (Recommended): Commit all milestone docs and the updated ROADMAP on the branch already chosen for this milestone.
2. **Continue brainstorming**: Keep iterating on the design before committing.
3. **Finish without committing**: End the brainstorm session; leave changes uncommitted.

### Option 1: Commit the milestone docs

1. Stage and commit all milestone documents (`DESIGN.md`, `RESEARCH.md`, `MILESTONE_SUMMARY.md`, all `M##-P##-slug-PLAN.md` files) and the updated `ROADMAP.md` with message `brainstorm: M##-slug`.

### Option 2: Continue brainstorming

Return to the brainstorming conversation and repeat the options when ready.

### Option 3: Finish without committing

Remind the user that the milestone docs and updated `ROADMAP.md` are still uncommitted, and to commit them manually before starting `claptrap-plan`.
