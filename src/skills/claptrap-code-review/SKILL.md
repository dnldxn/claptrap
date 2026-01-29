---
name: "claptrap-code-review"
description: Generic methodology for reviewing code changes against requirements, specs, or proposals. Produces structured, actionable feedback.
---

# Code Review Skill

Review code changes against requirements to identify real issues while respecting simplicity-first trade-offs. Surface risks and correctness problems, not stylistic preferences.

## Core Principles

| Principle | Description |
|-----------|-------------|
| **Focus on Real Risk** | Bugs, regressions, security issues, and maintainability problems |
| **Alignment** | Verify changes match the approved requirements and intent |
| **Actionable Feedback** | Be specific; cite locations and explain *why* a change is needed |
| **Pragmatic Quality** | Avoid theoretical perfection and minor style preferences |
| **Constructively Critical** | Assume the implementation is imperfect; disagree when substantive issues exist |
| **Approve Good Work** | Don't block solid changes; acknowledge the specific value of good contributions |

## Tone

Be constructive, professional, and friendly. Criticism should help, not discourage.

## Review Process

### 1. Understand Intent

Before reviewing code, understand what the change is supposed to accomplish:

- What requirements or specifications does this change address?
- What is the expected behavior after the change?
- What is explicitly out of scope?

### 2. Verify Alignment

Compare the implementation against the requirements:

- Does the code implement all required functionality?
- Are there any deviations from the specification?
- Are edge cases from the requirements handled?

### 3. Assess Quality

Evaluate the implementation for:

| Category | Questions |
|----------|-----------|
| **Correctness** | Does it work as intended? Are there logic errors? Is error handling appropriate? |
| **Safety** | Are there security risks? Data integrity issues? |
| **Robustness** | How does it handle edge cases and failures? |
| **Maintainability** | Is it readable and well-structured? Will it be easy to modify later? |
| **Efficiency** | Are there obvious performance bottlenecks or resource inefficiencies? |

### 4. Prioritize Findings

Not all issues are equal. Categorize by impact:

| Priority | Criteria | Action |
|----------|----------|--------|
| **Must Fix** | Bugs, security issues, spec violations, data integrity risks | Block merge until resolved |
| **Should Fix** | Maintainability concerns, missing tests for risky code, unclear logic | Recommend fixing before merge |
| **Nice to Have** | Minor improvements, style suggestions, optional optimizations | Note for consideration |

### 5. Suggest Alternatives

When a meaningfully different approach exists:

- Describe the alternative briefly
- List pros and cons compared to current implementation
- Let the author decide (unless must-fix)

## Review Rules

**Do:**
- Cite specific locations (file paths, function names, line references)
- Explain the impact of each finding
- Suggest the smallest change that fixes the issue
- Recommend tests only when risk or complexity warrants it
- Review against project code conventions if provided

**Don't:**
- Block changes for stylistic preferences
- Propose scope expansion beyond requirements
- Rewrite code in the review (focus on direction, not implementation)
- Nitpick obvious or trivial issues
- Mark disagreement for minor preferences

## Output Format

Produce a structured review in this format:

```markdown
# Review: <change-title>

## Summary
[1-3 sentences on overall assessment and key risks]

## Must Fix
- [ ] **[Location]**: Finding description. Impact: [what goes wrong]. Fix: [suggested approach].

## Should Fix
- [ ] **[Location]**: Finding description. Impact: [consequence]. Recommendation: [approach].

## Nice to Have
- [ ] **[Location]**: Optional improvement description.

## Alternative Approaches
- **[Approach name]**: Brief description.
  - Pros: [advantages]
  - Cons: [disadvantages]
```

### Output Notes

- Omit empty sections (e.g., if no "Must Fix" items, exclude that section)
- Use checkbox format for trackable findings
- Include enough context in each finding to be actionable without re-reading the code

## Handling Insufficient Context

If the provided context is insufficient for a thorough review:

1. Identify what specific information is missing
2. Explain why that information is needed
3. Request the missing context before proceeding
4. Do not guess at requirements or intent

## Self-Correction Checklist

Before finalizing the review:

- [ ] Did I focus on real risks, not style preferences?
- [ ] Is every finding actionable with clear location and fix?
- [ ] Did I verify alignment with the stated requirements?
- [ ] Are findings correctly prioritized by impact?
- [ ] Would I approve this if the must-fix items were resolved?
