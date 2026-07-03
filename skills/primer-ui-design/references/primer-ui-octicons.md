# Primer Octicons — Iconography Reference

> Load this file only when a task involves choosing, sizing, installing, or accessibly wiring up icons. Otherwise skip it.

Reference for GitHub's Primer Design System iconography. Sourced from `primer.style/octicons/*` (usage, design, and code guideline pages).

## What Octicons Are

Octicons are "a scalable set of icons handcrafted by GitHub" — the official SVG icon set of the Primer design system, built by GitHub for GitHub product and brand surfaces. The set contains ~336 icons. They are distributed as raw SVGs and as framework components (React, Rails).

## Sizes & Grids

Octicons ship in fixed, purpose-built sizes. **Do not resize between them** — each size is drawn on its own grid to preserve stroke width and legibility.

- **12px** — condensed UI contexts only (alerts, status indicators, chevrons). Special-case; only exists where a 16px icon can't be used.
- **16px** — the standard/default size; the largest library coverage.
- **24px** — larger variant with comparable coverage.
- **48px / 96px** — specialized, currently limited (e.g. Copilot icon).

Design specs (for authoring new icons):
- Always design a **16px and a 24px** version of each icon.
- **1.5px stroke width** for both 16px and 24px icons.
- **Round caps and joins.**
- **1px corner radius** by default (unless a different radius aids recognition); **0.25px** radius on small filled elements like filled arrowheads.
- **1px gap** to separate overlapping objects; **1.5px gap** around modifier elements (lines, arrows).
- Align the outer edge of shapes to pixel boundaries when possible.

## Usage & Selection Guidelines

- "Where possible use icons to supplement text, rather than replacing it."
- "Make sure that the meaning of icons is clear when used without accompanying text."
- Choose recognizable icons that accurately depict the concept or action.
- Maintain consistency in icon use across your product/brand.
- Avoid icons for complex or abstract concepts that may be confusing.
- Use icons only at their designated sizes to keep stroke width and legibility consistent.

### State pairs
Use predefined outline/filled (or slash) pairs to indicate state; use outline or slash variants for "off"/"empty" states, not filled:
- `heart` / `heart-fill` (sponsoring)
- `star` / `star-fill` (starred)
- `check-circle` / `x-circle-fill` (pass / fail)
- `bell` / `bell-slash` (subscribed / unsubscribed)

### Color
Use functional foreground colors so icons stay legible across color modes. Some icons have predetermined semantic colors:
- Info → `fg.accent`
- Check → `fg.success`
- X → `fg.danger`
- Alert → `fg.attention`

## Accessibility

- **Decorative icons** (convey no meaning): hidden from screen readers; omit `aria-label`. In `@primer/octicons-react`, icons are **decorative by default** — you do not need to add `aria-hidden`.
- **Meaningful icons** (convey information/action): require an accessible name. Add an `aria-label` with the text alternative (React/SVG applies `role="img"` behavior).
- **Contrast:** unless purely decorative, an icon must have a contrast ratio of **at least 3:1** against its background.

## Do's & Don'ts

| Do | Don't |
|----|-------|
| Keep icons at their original/designated size | Resize icons (distorts stroke width & readability) |
| Supplement text with icons | Replace text with icons where meaning could be unclear |
| Use recognizable, concrete icons | Use icons for abstract/complex concepts |
| Give meaningful icons an `aria-label` | Add `aria-label` to purely decorative icons |
| Use functional foreground colors / semantic pairs | Use filled variants for "off"/empty states |

## Install & Code Usage

### React — `@primer/octicons-react`
```
npm install @primer/octicons-react
```
```jsx
import {ArrowRightIcon} from '@primer/octicons-react'
const MyComponent = () => <ArrowRightIcon />
```
- **`size` prop** accepts a number of pixels. Default is **16**. Use only the supported sizes:
  ```jsx
  <AlertFillIcon size={12} />
  <AlertFillIcon size={16} />
  <AlertFillIcon size={24} />
  ```
- **Color:** icons use `currentColor` by default; override with `fill`:
  ```jsx
  <AlertFillIcon fill="var(--fgColor-attention)" />
  ```
- **Accessibility:** decorative by default (no `aria-hidden` needed). Add `aria-label` only when meaningful:
  ```jsx
  <AlertFillIcon aria-label="Build failed" />
  ```

Component names are PascalCase + `Icon` suffix (e.g. `git-pull-request` → `GitPullRequestIcon`).

### Rails — `primer_view_components`
```ruby
# Gemfile
gem "primer_view_components"
```
```erb
<%= render(Primer::Beta::Octicon.new(:"arrow-right")) %>
```
- **Size tokens:** `:xsmall`, `:small` (default, 16px), `:medium`.
- **Accessibility:** `aria: { label: "Build failed" }` when meaningful.

### Core SVGs — `@primer/octicons`
```
npm install @primer/octicons
```
Raw SVGs (also available directly from the `primer/octicons` GitHub repo) for manual/other-framework use. In JS, multi-word names use bracket notation: `octicons['arrow-right']`.

Related packages: `@primer/styled-octicons` (styled-components variant).

## Commonly Used Icon Names by Purpose

Icon slugs (kebab-case; append `-fill` for filled variants where available):

- **Navigation:** `home`, `search`, `three-bars` (menu), `chevron-down`, `chevron-right`, `chevron-left`, `chevron-up`, `arrow-left`, `arrow-right`, `arrow-up`, `arrow-down`, `link-external`, `sidebar-expand`, `sidebar-collapse`
- **Actions:** `plus`, `x`, `pencil` (edit), `trash`, `download`, `upload`, `copy`, `gear` (settings), `filter`, `sync`, `share`, `paste`, `kebab-horizontal` / `kebab-vertical` (overflow menus)
- **Status / feedback:** `check`, `check-circle` / `check-circle-fill`, `alert` / `alert-fill`, `info`, `bell` / `bell-slash`, `x-circle` / `x-circle-fill`, `stop`, `shield-check`, `clock`
- **Git / PR concepts:** `git-branch`, `git-pull-request`, `git-commit`, `git-merge`, `git-compare`, `repo`, `repo-forked`, `issue-opened`, `issue-closed`, `comment`, `comment-discussion`, `code`, `code-review`, `diff`, `tag`
- **Content / social:** `star` / `star-fill`, `heart` / `heart-fill`, `eye` / `eye-closed`, `bookmark`, `person`, `people`, `file`, `file-directory`

Verify exact slugs and availability at a given size in the gallery at `primer.style/octicons/icons` before use.

## Source pages
- `primer.style/octicons/usage-guidelines` — usage, accessibility, color, state pairs
- `primer.style/octicons/design-guidelines` — grids, stroke, radius, gaps
- `primer.style/octicons/code` — React/Rails install & usage
- Package refs: `@primer/octicons`, `@primer/octicons-react` (npm), `primer/octicons` (GitHub)
