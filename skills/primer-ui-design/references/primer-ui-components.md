# Primer (Product) Components — Reference

> Load this file when a task involves choosing or configuring specific UI components (buttons, forms, dialogs, menus, labels, etc.). Skip it for pure layout/token or content-writing tasks.

A decision-oriented reference to GitHub's Primer design system product components. Source: `primer.style/product/components/`. Covers the ~62 public components in the index.

## Table of Contents

- [How to choose a component](#how-to-choose-a-component)
- [Component Index (categorized)](#component-index-categorized)
- [Detailed component guidance](#detailed-component-guidance)
- [Cross-cutting accessibility rules](#cross-cutting-accessibility-rules)

---

## How to choose a component

Fast disambiguation for the choices people get wrong most often:

- **Status text**: `Label` (categorical metadata) vs `StateLabel` (issue/PR open/closed/merged) vs `CounterLabel` (a number) vs `Token` (removable, user-generated) vs `Banner`/`InlineMessage` (a message, not a tag).
- **Picking from options**: `ActionMenu` (quick actions/selection, simple) → `SelectPanel` (large lists needing filter/search + multi-select) → native `Select` (short single-select in a form). `Autocomplete` when the user types to filter.
- **Overlays**: `Dialog` (focused transient task, modal) vs `ConfirmationDialog` (yes/no confirm) vs `Popover` (non-modal pointer to UI) vs `Tooltip` (last-resort supplementary text) vs `AnchoredOverlay`/`Overlay` (build-your-own primitives).
- **Lists**: `ActionList` (actions/selection) vs `NavList` (page navigation) vs `TreeView` (hierarchical) vs `DataTable` (2D tabular data).
- **Empty/loading**: `Blankslate` (empty state) vs `Skeleton*` (content-shaped loading placeholders) vs `Spinner` (indeterminate) vs `ProgressBar` (determinate).

---

## Component Index (categorized)

### Actions & menus

| Component | Use when |
|---|---|
| **Button** | Initiate an action on a page or form. |
| **IconButton** | A button that shows only an icon (space-constrained actions). |
| **ButtonGroup** | Render a series of related buttons as one connected unit. |
| **ActionBar** | A horizontally aligned row of IconButtons (toolbar of quick actions). |
| **ActionList** | A vertical, single-column list of interactive actions/options. |
| **ActionMenu** | Quick actions and selections behind a button/trigger (dropdown). |
| **Link** | Apply link styling to hypertext for navigation. |
| **KeybindingHint** | Indicate the keyboard shortcut for an action. |

### Forms & inputs

| Component | Use when |
|---|---|
| **FormControl** | Wrap any input to attach a label, caption, validation, and ARIA wiring. |
| **TextInput** | Single-line free-text (or number) entry. |
| **Textarea** | Multi-line text entry. |
| **TextInputWithTokens** | Enter a list of values rendered as removable tokens. |
| **Autocomplete** | Type to filter and select from a set of options. |
| **Checkbox** / **CheckboxGroup** | One or many independent boolean selections. |
| **Radio** / **RadioGroup** | Choose exactly one from a short, mutually-exclusive set. |
| **Select** | Single option from a native dropdown in a form. |
| **SegmentedControl** | Pick one of a small set of related, always-visible choices. |
| **ToggleSwitch** | Immediately toggle a setting on/off (no submit). |

### Navigation

| Component | Use when |
|---|---|
| **Breadcrumbs** | Show and navigate the current page's hierarchy. |
| **NavList** | Vertical list of navigation links (e.g. a settings sidebar). |
| **UnderlineNav** | Horizontal tabbed navigation between views/pages. |
| **UnderlinePanels** | Tabbed panels of content within a single page. |
| **Pagination** | Navigate across paginated content. |
| **TreeView** | Hierarchical, expandable list (file trees, nested nav). |
| **PageHeader** | Top-level page heading region with title/actions/context. |

### Overlays & disclosure

| Component | Use when |
|---|---|
| **Dialog** | Modal floating surface for a focused transient task. |
| **ConfirmationDialog** | Confirm or cancel a user action (destructive or consequential). |
| **Popover** | Non-modal overlay pointing attention at a UI element. |
| **Tooltip** | Last-resort supplementary text on hover/focus of an interactive element. |
| **SelectPanel** | Dialog for selecting/filtering from a large list. |
| **AnchoredOverlay** | Primitive: open an overlay positioned relative to an anchor. |
| **Overlay** | Low-level floating-surface primitive for custom overlays. |
| **Details** | Enhance the native `<details>` disclosure element. |

### Feedback & status

| Component | Use when |
|---|---|
| **Banner** | Highlight prominent, page-level important information. |
| **InlineMessage** | Inform the user about the result of an action, inline. |
| **Spinner** | Indeterminate loading indicator. |
| **ProgressBar** | Show determinate completion or proportional composition. |
| **Blankslate** | Placeholder for missing/empty content (empty states). |
| **SkeletonText** / **SkeletonBox** / **SkeletonAvatar** | Content-shaped placeholders while loading. |
| **StateLabel** | Render issue/PR status (open, closed, merged, draft). |

### Data display & content

| Component | Use when |
|---|---|
| **Avatar** | Represent a user or organization with an image. |
| **AvatarStack** | Display multiple avatars inline (participants, teams). |
| **Label** | Add contextual, categorical metadata as a styled tag. |
| **LabelGroup** | Group multiple labels with layout constraints. |
| **CounterLabel** | Add a count to a navigation or UI element. |
| **Token** | Compact, often-removable representation of an object. |
| **CircleBadge** | Connect/associate third-party service logos. |
| **BranchName** | Display a git branch name as a link/mono tag. |
| **Card** | Styled container grouping related content. |
| **DataTable** | Present two-dimensional tabular data. |
| **Timeline** | Vertically connected sequence of items/events. |
| **RelativeTime** | Display a timestamp accessibly (e.g. "3 days ago"). |

### Layout & typography

| Component | Use when |
|---|---|
| **PageLayout** | Define page structure regions (header, content, pane, footer). |
| **SplitPageLayout** | Two-column layout with a sidebar/content split. |
| **Stack** | Create responsive vertical/horizontal flows with consistent gaps. |
| **Heading** | Define content hierarchy with semantic headings. |
| **Text** | Apply typographic styles to inline text. |
| **Truncate** | Shorten overflowing text with an ellipsis. |

---

## Detailed component guidance

This is a curated subset — the components people most often confuse or misuse. For any other component (DataTable, PageLayout, SelectPanel, Stack, TreeView, etc.), the categorized index above is enough to *choose* it; for full anatomy, props, and states to *configure* it, consult its page at `primer.style/product/components/<name>`.

### Button

**What it is:** A control that initiates an action on a page or form.

**Variants (visual priority):** **Primary** (highest-priority action; one per group), **Default** (general actions), **Invisible** (transparent/minimal UI), **Danger** (destructive actions).

**Sizes:** `small`, `medium` (default/recommended), `large` (sparingly, to emphasize).

**Key props:** `leadingVisual` / `trailingVisual` (icons), `trailingAction` (fixed at end, e.g. dropdown caret), `block` (full width), `loading` (spinner, sets `aria-disabled`), `labelWrap` (multi-line), `href` + `as="a"` (renders as a link).

**States:** Loading (spinner, focus preserved), Inactive (looks disabled but stays interactive — for system/error cases needing an explanatory tooltip/dialog), Disabled (avoid — breaks keyboard navigation).

**Accessibility:** Prefer *inactive* over *disabled* so the control keeps contrast and keyboard focus; loading state auto-preserves focus.

### IconButton

A `Button` that renders only an icon — for space-constrained actions and toolbars (`ActionBar` is a row of these). Choose it when the action is well-understood from its icon alone. Requires an `aria-label`; pair with a label-type `Tooltip` so sighted users get the name on hover/focus. Never rely on the icon alone for meaning.

### ActionList

A vertical, single-column list of interactive actions or options, with room for icons, descriptions, side info, and rich visuals. Use `ActionList` standalone; use `ActionMenu` when it should open from a trigger; use `NavList` when items are page navigation. Supports single/multi-select (checkbox/radio indicators), `LinkItem`, `ActionList.Group` with headings/dividers, leading/trailing visuals, trailing action buttons, and item states (disabled, loading, inactive-with-explanation, danger). Container role depends on use (`menu`/`listbox`/`list`) with matching item roles.

### ActionMenu

`ActionList` + `Overlay` composed into a dropdown for quick actions/selections. Use for simple menus opened from a button; step up to `SelectPanel` for large lists needing filter/search or heavy multi-select; use native `Select` for a simple single-select form field. Single-select (persistent label recommended) or multi-select (checkboxes). Triggers: `Button`/`IconButton`, right-click context menu, or `ActionMenu.Anchor`. `role="menu"`; items use `menuitemradio`/`menuitemcheckbox` with `aria-checked`.

### FormControl

A wrapper that renders a labelled input plus optional caption and validation text and manages the ARIA associations between them — the backbone for accessible forms in Primer. Wrap `TextInput`, `Textarea`, `Select`, `Checkbox`, `Radio`, `Autocomplete`, etc. Slots: `FormControl.Label` (as `<label>`/`<legend>`/`<span>`; can be visually hidden yet accessible), `FormControl.Caption`, `FormControl.Validation`, optional `LeadingVisual`. Key props: `required`, `disabled`, `layout` (`vertical` default, `horizontal` for checkbox/radio), `id`, `requiredIndicator`. Prefer it over hand-rolling `aria-describedby`.

### TextInput

A single-line text field (also `type="number"`). Use `Textarea` for multi-line, `TextInputWithTokens` for lists of values. Sizes `small`/`medium` (default)/`large`. Features: leading/trailing visuals, a trailing action button (e.g. clear), monospace option, loading state (`loaderText`), validation, `required`, `block`. Always pair with `FormControl.Label`; use `aria-label` only when no visible label exists.

### Dialog

A modal floating surface for transient content — confirmations, focused forms, selection. For a simple yes/no use `ConfirmationDialog`; for non-modal attention use `Popover`; if content feels like a page, prefer a dedicated page over Extra Large. Anatomy: Header (title, optional subtitle, close) · Body (scrolls) · Footer (optional actions). Sizes: Small 296px · Medium 320px (default) · Large 480px · Extra Large 640px. Positioning center/left/right/bottom; narrow viewports can render as bottom sheet or fullscreen. Focus returns to the trigger on close; Escape and close both fire `onClose`; role `dialog` or `alertdialog`.

### ConfirmationDialog

A specialized `Dialog` for confirming/cancelling an action. Use when an action is consequential or destructive and needs an explicit yes/no; use danger styling for destructive confirmations. For richer content or forms, use the base `Dialog`.

### Banner

A prominent surface for important page/section-level information. Variants (tone): `info` (default), `warning`, `critical`, `success`, `upsell`. Dismissible via `onDismiss`; `primaryAction`/`secondaryAction` slots; `flush` and compact layouts; custom leading visual; title can be visually hidden while staying accessible. Use `Banner` for page-level importance; `InlineMessage` for inline feedback about a specific action. Acts as a landmark region; `Banner.Title` accepts an `as` prop for correct heading hierarchy.

### Tooltip

Supplementary text on hover/focus of an interactive element — for labeling icon-only controls or short hints. **Last resort**: content is hidden by default, so never put critical info needed to operate the UI in a tooltip. Directions are compass points; defaults to south and auto-repositions. Must attach to interactive elements only. Two types: `label` (names the trigger) and `description` (extra info).

### Label

Styled text that adds contextual, categorical metadata (a "tag"). Use `Token` for user-generated/removable items, `StateLabel` for issue/PR status, `CounterLabel` for counts, `LabelGroup` to lay out a collection. Colors: Default, Primary, Secondary, Accent, Success, Attention, Severe, Danger, Done, Sponsors. Sizes Small (default)/Large. Color alone shouldn't carry meaning — the label text must convey the status/category.

### Avatar

An image representing a user or organization. Shape is meaningful: **circle** for individual people, **square** for non-human entities (bots, teams, orgs, AI agents). Sizes 16px–64px. `AvatarStack` shows multiple avatars inline. Provide `alt` text whenever the avatar isn't accompanied by a visible name.

---

## Cross-cutting accessibility rules

Recurring rules across Primer component docs:

- **Never rely on color alone** to convey status/meaning (Label, StateLabel, Banner) — text must carry it.
- **Icon-only controls need an accessible name** (`aria-label`) and ideally a label-type `Tooltip`.
- **Prefer inactive over disabled** for buttons/list items so keyboard users keep focus and get an explanation.
- **Wrap form inputs in `FormControl`** so labels, captions, validation, and ARIA associations are handled correctly.
- **Overlays manage focus**: return focus to the trigger on close, support Escape, use the right role (`dialog`/`alertdialog`/`menu`/`listbox`).
- **Tooltips are supplementary only** — never the sole carrier of essential information.
- **Loading states need descriptive text** (`loaderText`) so screen-reader users know what is loading.

*Source: `primer.style/product/components/` and individual component pages.*
