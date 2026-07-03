# Primer Accessibility Reference

> Load this file when a task involves accessibility — contrast, keyboard/focus, ARIA/semantic HTML, alt text, forms a11y, motion, tooltips, or a11y testing. GitHub treats accessibility as a design default, so pull this in for most non-trivial UI work.

Source: GitHub Primer Accessibility docs (`primer.style/accessibility/`).

## Core principles

- GitHub targets **WCAG 2.1 Level AA** (both Level A and AA success criteria).
- Never convey meaning by **color alone** — pair with text, an icon, a shape, or a pattern.
- Prefer **semantic HTML** over ARIA. "Use ARIA sparingly; most use cases can be covered by HTML or JS."
- Every interactive element must be **operable by keyboard alone**.
- Content must **reflow and remain usable** from 50% to 400% zoom, at any screen size/orientation, with a single scroll direction.

## Color & contrast

| Element | Minimum ratio |
|---|---|
| Normal text (labels, entered text, meaningful button text, validation) | **4.5:1** |
| Large text | **3:1** |
| Non-text: input borders/boundaries, borderless input bg vs. surrounding | **3:1** |
| Selection indicators (checkmarks, radios) | **3:1** |
| Functional icons (icon-only buttons) | **3:1** |
| Validation icons (when the icon is the only indicator) | **3:1** |

- **Do** add a non-color cue (icon, text, pattern) for state changes, statuses, and chart/graph series.
- **Do** verify contrast against design tokens across light, dark, and high-contrast modes.
- **Exempt:** disabled button states and decorative icons accompanying a text label (but still consider low-vision visibility).

## Keyboard & focus

- **WCAG 2.1.1 (Keyboard):** every interactive element reachable and activatable via keyboard. Test `Tab`/`Shift+Tab`; arrow keys for composite widgets (toolbars, menus); also `Space`, `Enter`, `Esc`.
- **WCAG 2.4.7 (Focus Visible):** every interactive element shows a visible focus indicator meeting contrast in all color modes; must not be obscured.
- **Never remove the focus outline** unless replaced with another visible indicator. Use `:focus-visible` so keyboard users get the indicator without it showing on mouse click.
- **WCAG 2.4.3 (Focus Order):** tab order follows logical DOM/content order; no jumping; never trap focus unexpectedly; focus must never be lost to `<body>`.
- **Deliberate focus management:**
  - **Modals:** move focus in on open, trap within, return to trigger on close.
  - **Adding content:** move focus to the first newly added item.
  - **Removing content:** move focus to a logical neighbor — not to `<body>`.
  - **Filtering:** keep focus on the filter control while applying; manage only when a filter is removed.
- No keyboard shortcut may conflict with browser/AT shortcuts.

## Semantic HTML & ARIA

- Prefer native elements (`<button>`, `<a>`) so behavior/focus/name come for free.
- **One `<h1>` per page**; consecutive heading levels, don't skip (no H2 → H4); nest for specificity.
- One `main` landmark and one `footer` landmark per page.
- ARIA is a last resort. Don't use `role="link"` in place of an anchor, don't strip `href`, don't rely on role substitutions.

## Alternative text

- **Informative image:** describe what it shows concisely; include important text baked into the image.
- **Decorative image:** empty `alt=""` (raster) or `aria-hidden="true"` + `focusable="false"` (SVG). Passes the "removal test" — deleting it loses no information.
- **Every `<img>` needs an `alt` attribute** (empty or descriptive).
- **Don't** include words like "image", "button", "link" (AT announces the role); don't keyword-stuff or write long irrelevant descriptions.
- Functional images and unlabeled icon buttons must have descriptive accessible names. Don't embed important text inside graphics.

## Links vs. buttons

- **Links (`<a>`):** navigate to a destination, jump within page, skip-links, download resources. Don't use links to open dialogs, save/delete, or submit.
- **Buttons (`<button>`):** submit, save/delete, open/close dialogs, toggle state. Don't use buttons for navigation or downloads.
- **Accessible names:** unique, concise, descriptive. Links hint at destination ("Our product offerings"); buttons use verb-noun ("Submit comment", "Delete repository"). Avoid "Click here", "Learn more", "Read more".
- Accessible-name priority: (1) visible text, (2) visually-hidden `sr-only` text, (3) `aria-labelledby`, (4) `aria-label` (last resort).
- Icon-only button pattern: icon + `<span class="sr-only">Star repository</span>`.
- **Don't** use `target="_blank"` by default; both links and buttons must be Tab-focusable with visible focus and hover states.

## Forms

- **Visible labels and instructions** for every input; sentence case, **no colons** on labels.
- **Avoid placeholder text** as the label — purpose must be clear without it.
- Design **error states**: field-level errors near the field; form-level error summary at top/bottom linking to the offending fields.
- Don't re-request data the user already gave (auto-populate or "same as" checkbox).
- **Don't disable submit buttons.** Prefer validation feedback. If a control must be disabled, prefer `aria-disabled="true"` (keeps it focusable) over `disabled`, and explain why.

## Motion / reduced-motion

- Auto-moving or auto-scrolling content must be **pausable/stoppable/playable**.
- Respect user preferences: **reduced motion**, color scheme, contrast (e.g. `prefers-reduced-motion`).
- **Flashing content: no more than 3 times per second.**

## Tooltips

- Tooltips are **rarely appropriate** — first consider not using one. Use only as a last resort on **interactive** elements (e.g. IconButton), never on `div`/`span`/`p`.
- **Never** put critical information in a tooltip; don't rely on them on mobile.
- Hover content must be **dismissible** (without moving pointer/focus), **hoverable** (pointer can move onto it), **persistent** (doesn't auto-dismiss), and available on **focus**.
- Keep text minimal; annotate semantics correctly (label vs. description).

## Testing & tooling

- **Keyboard pass:** Tab/Shift+Tab — reach everything, logical order, visible focus, no traps.
- **Screen reader pass:** verify accessible names, alt text, heading structure, page language.
- **Zoom:** test 50–400% reflow without overlap.
- **Target size:** hit areas at least **24×24 CSS px**.
- Tools: **axe DevTools** (Deque), **HeadingsMap** extension, GitHub **Alt-text bot**; integrate accessibility linters into **CI/CD**. Primer provides Designer and Engineering checklists.

*Canonical base: `primer.style/accessibility/` (sub-pages under `/design-guidance/`, `/patterns/`, `/tools-and-resources/checklists/`).*
