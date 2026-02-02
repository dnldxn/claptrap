---
name: "claptrap-brainstorming"
description: You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation.
metadata:
   inspiration: https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md
---

# Brainstorming Ideas Into Designs

## Overview

Turn raw ideas into a **clear, validated design document** through structured dialogue **before any implementation begins**.

Start by asking questions one at a time to refine the idea. Once you understand what you're building, present the design in small sections (200-300 words), checking after each section whether it looks right so far.

## Workflow Steps

### Step 0: Load context

- Invoke the `claptrap-memory` skill to read and write memories as instructed.

### Step 1: Clarifying questions (one at a time)

**Ask questions one at a time** to understand:
- User goals and success criteria
- Scope boundaries (in/out)
- Technical constraints or preferences
- Integration points with existing systems
- Timeline/phasing constraints

Rules:
- **One question per message** - don't overwhelm with multiple questions
- **Prefer multiple choice** when possible, but open-ended is fine too
- If a topic needs more exploration, break it into multiple questions
- If external docs could help, spawn the `research` subagent (do not research yourself)

#### Clarity Score

After each question-answer exchange, estimate a **Clarity Score (0-100%)** indicating how clear, unambiguous, and complete the requirements are.  Show this score before asking the next question.

Format: `**Clarity: X%** - [brief reason for score]`

Requirements:
- **Minimum 3 questions** - Ask at least 3 questions regardless of initial clarity
- **100% required** - Continue asking questions until clarity reaches 100%
- Score should increase as ambiguity resolves and requirements solidify
- Be honest—don't inflate scores to end early

### Step 2: Explore approaches

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why
- If codebase context is needed, spawn the `claptrap-explore` subagent to gather it

### Step 3: Draft the design in validated sections

Present the design in sections of 200-300 words, validating with the user after each section:

1. **Intent** - What we're building and why
2. **Scope** - In scope / out of scope
3. **Acceptance Criteria** - Testable checkboxes
4. **Architecture Overview** - Components, package structure, core types, data flow
5. **Key Decisions** - Decision/Options/Choice/Rationale table
6. **Open Questions** - Items to resolve before or during implementation

Be ready to go back and clarify if something doesn't make sense.

### Step 4: Finalize

1. Generate `<feature-slug>` from the design title using kebab-case.
2. Create directory: `.claptrap/designs/<feature-slug>/`
3. Write the final design to: `.claptrap/designs/<feature-slug>/design.md`
   - Use the template at `templates/design.md`
   - Ensure ALL required headings exist
4. Add `## Next Steps` pointing to `/claptrap-propose`
5. Add `## OpenSpec Proposals` section with placeholder `- (none yet)`

### Step 5: Memory write (selective)

If any significant decisions were made:
1. Invoke `claptrap-memory` skill.
2. Propose 1-3 candidate memory entries.
3. Write only entries that would help a future agent avoid mistakes.
4. Never write secrets.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **Clarity before design** - Reach 100% clarity (minimum 3 questions) before proposing approaches
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Be willing to go back and clarify when something doesn't make sense
