---
name: primer-design
description: >-
  Design and build product UI that conforms to GitHub's Primer Design System —
  its principles, foundations (color, typography, spacing, layout tokens),
  components, UI patterns, Octicons, accessibility, and content guidelines. Use
  this skill whenever a task involves Primer, GitHub-style UI, `@primer/*`
  packages (primer/react, primer/css, primer-view-components), Octicons, or when
  the user wants an interface that follows Primer's look, tokens, and behavior —
  even if they only say "make it look like GitHub", "match GitHub's UI", or name
  a specific piece (a Primer Button, Banner, Dialog, Blankslate, form pattern,
  etc.). Also use when reviewing or auditing existing UI for Primer compliance.
  Do NOT use for a project whose own design system is not Primer (e.g. a repo
  with its own token/CSS conventions) unless the user explicitly asks for Primer.
---

# Primer Design System

Primer is **GitHub's design system**: an open-source common language of principles, foundations, components, and patterns for building cohesive, accessible, responsive, efficient product UI, no matter where in the platform you work. This skill helps you design and build interfaces that conform to it.

## How to use this skill (read this first)

The detail lives in **reference files under `references/`**. They are large. To stay fast and token-efficient, **load only the reference file(s) your current task actually needs, and no others.** Skim the routing table below, decide what's relevant, then read just those files.

| If your task involves… | Load this file |
|---|---|
| Color, typography, spacing, layout, breakpoints, design tokens/primitives | `references/primer-ui-foundations.md` |
| Choosing or configuring a specific component (Button, Dialog, ActionMenu, Label, forms, etc.) | `references/primer-ui-components.md` |
| Composing components into flows (forms, saving, loading, empty states, notifications, navigation, disclosure, onboarding, degraded states, data viz) | `references/primer-ui-patterns.md` |
| Icons — choosing, sizing, installing, or accessibly wiring up Octicons | `references/primer-ui-octicons.md` |
| Accessibility — contrast, keyboard/focus, ARIA, alt text, motion, testing | `references/primer-ui-accessibility.md` |
| Writing or reviewing UI copy — labels, errors, empty-state text, dates, terminology | `references/primer-ui-content.md` |

Most real tasks touch two or three of these (e.g. "build a settings form" → components + patterns + accessibility + content). Pull those in; skip the rest. Accessibility is a Primer default, not an add-on, so reach for `primer-ui-accessibility.md` on most non-trivial UI work.

## Design principles

Primer's four core principles — let them guide every decision:

1. **Cohesive user experience.** Consistency across the whole platform so pages feel familiar. Reuse shared patterns and components rather than inventing per-page UI; familiar behavior lets people focus on the task, not on parsing new UI.
2. **Accessibility & inclusivity.** Accessibility is a core concern considered from the *start* of a project — retrofitting it later is a hard, expensive retrofit. It shapes the design, the behavior, and the implementation. Assume a global audience diverse in ability, device, and connectivity.
3. **Productivity & efficiency.** GitHub is a platform for productivity. Encourage flow and focus; keep the experience fast and compact; "remove as much friction as possible between the human and the software."
4. **Responsive design.** Adapt across viewports *without* downgrading the desktop experience into a mobile-first solution — preserve the strength of desktop while adapting to smaller screens.

Guiding ethos: **The Zen of GitHub** — e.g. "Responsive is better than fast," "Practicality beats purity," "Encourage flow."

## How the system is structured

- **Foundations** — cross-cutting fundamentals: color usage, content, icons, layout, responsive design, typography.
- **Primitives** — the design tokens themselves: color, size/spacing, typography, token naming, delivered as CSS variables.
- **Components** — 60+ UI components (Button, Dialog, DataTable, forms, navigation, overlays…) with accessible, responsive defaults baked in.
- **UI Patterns** — reusable solutions to common problems (forms, empty states, loading, saving, navigation, notifications, progressive disclosure, degraded experiences, data viz).
- **Octicons** — GitHub's handcrafted SVG icon set.
- **Guides / Contributing** — how to adopt Primer and contribute back.
- **Implementation surfaces** — React (`@primer/react`), Rails (`primer_view_components`), CSS utilities, plus Figma libraries.

## The working method

Whatever you're building, follow this order — it's how Primer is meant to be consumed:

1. **Start from foundations and tokens, never raw values.** Never hard-code a color, size, or type value when a token exists. Consume the *functional/semantic* token layer (e.g. `--fgColor-accent`, `--text-body-shorthand-medium`), never base scale values. Tokens carry light/dark/high-contrast support for free.
2. **Reach for an existing component before building custom.** The component library encodes accessible, responsive defaults — "every pattern in Primer is built to work across all color modes out of the box." If you're hand-rolling a dropdown, dialog, or form field, stop and check `primer-ui-components.md` first.
3. **Apply the matching UI pattern for the flow.** Forms, loading, saving, empty states, and errors all have prescribed Primer patterns. Don't reinvent the interaction; compose the components the pattern calls for.
4. **Bake in accessibility and content quality as you go.** WCAG 2.1 AA, keyboard operability, non-color status cues, sentence-case plain-language copy — these are requirements, not polish. Verify against `primer-ui-accessibility.md` and `primer-ui-content.md`.
5. **Verify responsiveness across the viewport ranges** (narrow <768px, regular ≥768px, wide ≥1400px) without degrading desktop.

## When implementing in code

- **React:** `@primer/react` components + `@primer/octicons-react` for icons; theme via Primer's ThemeProvider so tokens resolve per color mode.
- **Rails:** `primer_view_components` + `Primer::Beta::Octicon`.
- **Any stack:** consume Primer's CSS variables directly; do not hard-code hex values, px type sizes, or arbitrary font weights when a token exists.

## Guardrails (apply everywhere)

These recur across every part of Primer — worth internalizing before you open a reference file:

- **Never convey meaning by color alone** — pair with text, an icon, or a shape.
- **Prefer semantic HTML over ARIA**; use native `<button>`/`<a>` so focus and naming come for free.
- **Prefer an inactive state over `disabled`** for buttons/controls, so keyboard users keep focus and get an explanation — and **don't disable submit buttons**; use validation feedback instead.
- **Sentence case, plain language, no trailing punctuation** in labels/buttons/headings; imperative verbs for actions.
- **Every interactive element is keyboard-operable** with a visible focus indicator.
- **Tooltips are a last resort** — never the sole carrier of essential information.

*Sources: `primer.style/product/getting-started/` and the linked foundations, components, patterns, Octicons, accessibility, and content pages. Reference files carry per-topic source URLs.*
