# Primer Foundations & Primitives Reference

> Load this file when a task involves color, typography, spacing, layout, responsive breakpoints, or design tokens. Skip it for pure component-selection or content-writing tasks.

Sourced from Primer product foundations and primitives pages.

## 1. Design principles

The four core principles (cohesive UX, accessibility & inclusivity, productivity & efficiency, responsive design) and the Zen of GitHub ethos live in the main `SKILL.md`, which is already in context when you read this file. Apply them; the sections below give the concrete tokens and values that implement them.

## 2. Color system

GitHub UI ships **two color modes — `light` and `dark`** — across **nine themes**. Every Primer pattern works across all color modes out of the box.

### Token architecture (three layers)
1. **Base tokens** — raw color values, e.g. `color-scale-pink-5`. **Never used directly in code.**
2. **Functional tokens** — global UI roles like text and borders, e.g. `borderColor-sponsors-emphasis`.
3. **Component / pattern tokens** — specific use cases, e.g. `focus-outlineColor`.

### Neutral scales
- Inverted gray scales, steps **0–13**, for light and dark. The light and dark scale directions are **inverted**: the light scale starts with white, the dark scale starts with black.
- **Usage by step:**
  - Steps **0–6**: background colors
  - Steps **7–8**: borders and dividers
  - Steps **9–10**: text and icons

### Semantic / functional color roles
Six primary roles communicate status:
- `accent` — links, selection, focus states
- `success` — primary buttons, positive messaging
- `attention` — warnings and active/in-progress processes
- `danger` — error states and destructive actions
- `open` / `closed` / `done` — issue/PR/task status
- `sponsors` — GitHub Sponsors elements

Each role provides background variants **`muted`** (subtle) and **`emphasis`** (strong), each with coordinating **foreground** tokens.

### Do's / Don'ts
- **Do** use functional/semantic tokens; **don't** use base scale tokens directly in code.
- **Do** rely on the built-in light/dark support rather than hard-coding colors per mode.

## 3. Typography

### Font families (token → value)
- **Sans Serif** — `--fontStack-sansSerif` = `'Mona Sans VF', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif`
- **Sans Serif Display** — `--fontStack-sansSerifDisplay` = same stack as above (`'Mona Sans VF', …`)
- **Monospace** — `--fontStack-monospace` = `ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace`

### Type scale (shorthand `font` tokens)
| Style | Token | Font size | Line height | Weight |
|-------|-------|-----------|-------------|--------|
| Display | `--text-display-shorthand` | 2.5rem | 1.375 | 500 |
| Title Large | `--text-title-shorthand-large` | 2rem | 1.5 | 600 |
| Title Medium | `--text-title-shorthand-medium` | 1.25rem | 1.625 | 600 |
| Title Small | `--text-title-shorthand-small` | 1rem | 1.5 | 600 |
| Subtitle | `--text-subtitle-shorthand` | 1.25rem | 1.625 | 400 |
| Body Large | `--text-body-shorthand-large` | 1rem | 1.5 | 400 |
| Body Medium | `--text-body-shorthand-medium` | 0.875rem | 1.5 | 400 |
| Body Small | `--text-body-shorthand-small` | 0.75rem | 1.625 | 400 |
| Caption | `--text-caption-shorthand` | 0.75rem | 1.25 | 400 |
| Code Block | `--text-codeBlock-shorthand` | 0.8125rem (13px) | 1.5 | 400 |
| Inline Code | `--text-codeInline-shorthand` | 0.9285em | — | 400 |

### Weight scale
- Light `--base-text-weight-light` = 300
- Normal `--base-text-weight-normal` = 400
- Medium `--base-text-weight-medium` = 500
- Semibold `--base-text-weight-semibold` = 600

### Line-height scale
- Tight 1.25 · Snug 1.375 · Normal 1.5 · Relaxed 1.625 · Loose 1.75
- Line-heights are **unitless** and aligned to a **4px grid**.

### Usage guidance / Do's & Don'ts
- Tokens use **`rem` units** so text scales with browser zoom (accessibility).
- Use shorthand `font` tokens to set size/family/weight/line-height in a single declaration.
- Stress efficient, clean reading; keep line length to **~80 characters** (W3C), left-align text as the standard.
- **Do** use the weight CSS variables rather than arbitrary numeric weights.
- **Do** use semantic markup with a proper heading hierarchy combined with styles; **don't** reorder heading tags purely for visual design.

## 4. Spacing / size scale (Primitives → Size)

### Base size scale (`--base-size-*`, rem-based)
- **Negative**: `--base-size-negative-48` … `--base-size-negative-2` (−3rem to −0.125rem)
- **Positive**: `--base-size-2` … `--base-size-128` (0.125rem to 8rem)
- Key px values in the scale: **4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 112, 128**.

### Border widths
- thin 1px · default 1px · thick 2px · thicker 4px

### Border radius
- small 3px · medium 6px · large 12px · full 9999px

### Layout spacing (stack gaps / padding densities)
- Condensed 0.5rem (8px) · Normal 1rem (16px) · Spacious 1.5rem (24px)

### Control sizes
- XSmall → XLarge, each with condensed / normal / spacious gap and padding variants.

### Overlay dimensions
- Widths Small→XLarge: 192px–960px · Heights: 256px–600px

## 5. Layout & responsive

Goal: consistent, accessible, responsive experiences that stay focused and uncluttered.

### Viewport ranges (3 categories)
- `narrow` (<768px) — single-column, mobile-focused
- `regular` (≥768px) — up to 2 columns, desktop
- `wide` (≥1400px) — optional third column

### Breakpoints
| Name | Value |
|------|-------|
| xsmall | 320px |
| small | 544px |
| medium | 768px |
| large | 1012px |
| xlarge | 1280px |
| xxlarge | 1400px |

### Content padding by breakpoint
- xsmall–large: 16px
- xlarge–xxlarge: 24px

### Page anatomy & regions
- **App header** (global + contextual nav, scrolls with page), **context region** (e.g. `:owner / :repository`), **App footer** (links, legal). Layout regions: header, content, left pane, right pane, footer.

### Page types
1. **Full pages** — centered, max-width typically `xlarge` (1280px)
2. **Split pages** — side navigation with an independently scrollable pane
3. **Interstitial pages** — sign-in/verification flows, typically 320px max-width

### Responsive behavior at narrow viewports
- Split into sequential pages · convert panes to bottom sheets · stack regions vertically.

## 6. Token / primitive principles (cross-cutting)

- Three-tier token model everywhere: **base → functional → component/pattern**; consume the semantic layer, never base values.
- Tokens are delivered as **CSS variables**; there is a documented "migrating to CSS variables" path.
- `rem`-based sizing/typography for zoom accessibility; 4px-grid line-heights and spacing scale.
- Naming: dedicated **Token Names** guidance governs consistency across color, size, and typography.

## Source pages
- `primer.style/product/getting-started/foundations/color-usage/`
- `primer.style/product/primitives/typography/`
- `primer.style/product/primitives/size/`
- `primer.style/product/getting-started/foundations/layout/`
