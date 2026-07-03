# Primer UI Patterns Reference

> Load this file when composing components into flows — forms, saving, loading, empty states, notifications, navigation, disclosure, onboarding, degraded states, or data viz. Skip it for single-component or token-only tasks.

Reusable solutions to common product design problems from `primer.style/product/ui-patterns/`. Each entry states the problem, the recommended approach, and key do's/don'ts.

## Table of Contents

1. [Forms](#1-forms)
2. [Saving](#2-saving)
3. [Loading](#3-loading)
4. [Empty States](#4-empty-states)
5. [Notification Messaging](#5-notification-messaging)
6. [Navigation](#6-navigation)
7. [Progressive Disclosure](#7-progressive-disclosure)
8. [Feature Onboarding](#8-feature-onboarding)
9. [Degraded Experiences](#9-degraded-experiences)
10. [Data Visualization](#10-data-visualization)

---

## 1. Forms

**Problem:** Minimize the effort and cognitive load required to complete a task that needs data input.

**Anatomy (FormControl):** Label (required), required-field indicator, input, caption, validation message.

**Recommended approach:**
- **Labels:** Every control needs a descriptive, concise label (aim ≤3 words), sentence case (e.g. "Repository name"). Never use placeholder text as a substitute for a label.
- **Required indicators:** Visibly mark required fields when not all are mandatory (exception: login forms). Fields marked required visually must also be required in code. Individual checkboxes/radios can't be marked required — validate the group instead.
- **Captions:** Augment the label with helpful context; keep brief. Remove captions that repeat the label or a validation message.
- **Input method:** Text fields for open-ended values; ActionMenu, CheckboxGroup, RadioGroup, Select, or autocomplete for values from a finite list.
- **Layout:** Default to vertically stacked FormControls for scannability. Order fields by importance, group related fields, place keyboard-input fields near each other. Size controls to fit their expected value.
- **Progressive disclosure:** Show/hide controls based on selections; nested controls may omit visible labels only if the parent gives sufficient context (still include a visually hidden label for screen readers).

**Validation:**
- Use Primer validation UI, not browser-native (native messages aren't screen-reader accessible).
- Prefer **validation on submit**. On failure — show an interactive error summary if 3+ errors, otherwise focus/scroll the first invalid input into view; mark inputs `aria-invalid=true`; connect errors via `aria-describedby`; rely on focus management rather than live regions.
- **Inline validation:** only after the user's first interaction with a field; never before they finish. Show a loading indicator if validation takes >1 second.
- Error messages must explain why validation failed and how to fix it. Success messages optional.

**Do:** Vertically stack controls; show one validation message per group; hide redundant captions when a validation message appears.
**Don't:** Use multi-column layouts just to save vertical space; validate each grouped input separately; disable the submit button (disabled buttons don't communicate what's needed to proceed).

---

## 2. Saving

**Problem:** Represent content and configuration changes accurately, quickly, and obviously.

**Explicit vs. automatic saving:**
- **Explicit (default):** User clicks submit or presses Enter. Use for declarative controls where intent must be confirmed — text inputs, checkbox groups, radio groups, multi-select dropdowns.
- **Automatic:** Changes apply instantly. Use for imperative controls where immediate feedback is expected — ToggleSwitches, SegmentedControls, single-select dropdowns.
- **Critical rule:** Never mix explicit and automatic save on a single page with multiple forms, and never within a single form.

**Feedback:**
- **Success:** InlineMessage if no page refresh; Banner if the page refreshes/redirects. Auto-saved fields should make saved state obvious without needing text.
- **Failure:** Preserve the user's data and give clear feedback.
- **Navigating away with unsaved changes:** Optionally warn via `beforeunload`.

**Buttons:**
- **Text:** Descriptive active verb (Create, Save, Delete, Update); avoid vague labels like "Done". Add the item's name when unclear.
- **State:** Always keep the save button enabled — don't disable when invalid or unchanged (disabled buttons can't be Tab-focused).
- **Placement:** Bottom-left for standard forms; bottom-right for dialogs/comments. Only one save button per page.
- **Appearance:** Primary for form-wide saves, secondary for segment-specific; primary save / secondary cancel when paired.

**Error forgiveness:** Confirm before destructive submissions. Offer undo after save when possible.

---

## 3. Loading

**Problem:** Without loading indicators users may assume a process failed silently. Maintain visible system status.

**Indicator types:** Spinner (indeterminate, most versatile) · Progress bar (determinate, best ≥3s) · Content skeletons (SkeletonText/Avatar/Box, improve perceived speed) · Animated icons/illustrations (branding moments only, sparingly).

**Timing thresholds:**
| Duration | Recommendation |
|---|---|
| <1s | Show no loading state (distracting) |
| 1–3s | Indeterminate indicator |
| 3–10s | Determinate indicator when possible |
| >10s | Determinate + treat as background task if possible |

**Approach:** Load incrementally — show each item as soon as it loads. Prioritize important data first. Position indicators nearest the content they stand in for to avoid layout shift. Consolidate adjacent loaders.

**Do:** Use specific accessibility labels ("loading status checks", not "loading"); subtle animation only.
**Don't:** Show an indicator for every piece of content; use flashy/large animations; announce every skeleton; semantically disable buttons during loading via `aria-disabled`.

---

## 4. Empty States

**Problem:** Handle spaces with no content yet (or temporarily unavailable), helping users understand purpose and how to proceed.

**Three scenarios:** feature not yet used; temporarily empty by design; error state.

**Anatomy (Blankslate):** graphic, primary text (title), secondary text (optional), primary action, secondary action (optional link), border (invisible by default).

**Approach:**
- **Graphic:** delight or preview the feature — except errors, where it reinforces something went wrong, not playful.
- **Primary text:** titles the state and explains purpose.
- **Primary action:** brief, descriptive; starts a creation flow for unused states, or offers a solution for errors.
- **First-time users:** welcoming, human language and illustrations.
- **Errors:** be specific without over-detailing ("Form could not be submitted. Some required fields were empty" beats "There was a problem"). Avoid overly technical language.

**Do:** Default to GitHub marketing icons; provide recovery paths; push users forward via alternative paths until a genuine dead end.
**Don't:** Use obscure error codes; vague error messages; paths that redirect users away from their task; playful graphics for errors.

---

## 5. Notification Messaging

**Problem:** Give essential feedback, contextual info, and product updates through appropriately placed/styled messages.

**Components:** **Banner** (high-prominence, page-level) and **InlineMessage** (localized, tied to a specific action or field). Toast notifications are not recommended.

**Message types:** System updates (Banner; not dismissible until resolved), Feedback (Banner or InlineMessage by scope), Awareness (either).

**Severity states:** Info · Warning · Critical · Success · Unavailable (degraded/permission) · Upsell.

**Placement:**
- **Top of body (most common):** page/section-wide relevance; Banners fill container width.
- **Inline:** InlineMessages near the related action, especially form validation.
- **Inside dialogs:** Banner below the dialog header, full width; prioritize showing action messaging inside the dialog.

**Do:** Keep messages close to where the interaction occurred; use InlineMessage for immediate action feedback; use success messaging sparingly.
**Don't:** Put dialog-related Banners at the top of the page; place messaging far from the user action; show a success message when success is already obvious (an edit that updates visually). Success messaging is warranted when success isn't otherwise obvious (copy-to-clipboard, multi-issue creation).

---

## 6. Navigation

**Problem:** Keep users oriented — aware of their location and paths — while balancing clear options against cognitive overload.

**Core principles:** Clear orientation; streamlined choices; contextual transitions (clarity about context switches without excessive interruption).

**Types:** NavList (vertical links, sidebars, URL changes) · TreeView (hierarchical) · Tabs — UnderlineNav (URL changes) or UnderlinePanels (same page, no URL change) · ActionMenu · Breadcrumbs (URL changes) · Pagination · SegmentedControl (short-list filter/sort/format).

**Tabbed navigation decision:** UnderlineNav when clicking changes the URL; UnderlinePanels when it only toggles visibility; SegmentedControl only if standard tabs don't fit.

**Structure:** Use PageHeader for titles showing location; section headings (h3–h6) reflecting hierarchy. Responsive: on narrow viewports show back links/breadcrumbs for detail pages; convert filter sidebars to ActionMenu or bottom-sheet dialogs.

**Do:** Place nav elements near the content they affect (pagination directly below a collection); keep tab order matching visual order; provide skip links; warn about unsaved changes before navigating away.
**Don't:** Mix URL-changing tabs with panel-toggling tabs; use full page reloads for same-page state changes; exceed ~15 items in an ActionMenu (use a bottom-sheet dialog instead).

---

## 7. Progressive Disclosure

**Problem:** Reduce information overload by hiding and showing content based on user interaction.

**Principles:** Maintain context — don't drastically disorient focus. Pair disclosure icons with descriptive text.

**Techniques:**
- **Chevron icon** — toggles collapsed content (up/down). Pair with text like "Show more".
- **Fold/unfold icon** — reveals text content (e.g. code-editor expansion); should stand alone, not paired with lengthy text.
- **Ellipsis icon** — truncated inline text; distinct from the kebab (overflow-menu) icon.
- **Text-only toggles** — discouraged; icons offer better accessibility.

**Do:** Add clarifying text; use chevrons with text; use fold/unfold for expandable code.
**Don't:** Use a chevron to trigger a dropdown or for pagination/directional actions; pair fold/unfold with long text; confuse ellipsis with kebab; use text-only when an icon is available.

---

## 8. Feature Onboarding

**Problem:** Help users discover and adopt new features — a "virtual unboxing experience" — without disrupting existing workflows.

**Techniques & when to use:**
- **Teaching bubbles (popovers):** highlight a new feature the user can immediately use. Headline + ~160-char message; obvious dismissal; one at a time. Don't point to hidden elements.
- **Page banners:** announce a major page-level feature/change; not for minor features.
- **Empty states:** onboard where users hit blank content areas.
- **Inline banners:** short intros during multi-step flows or settings.
- **Dashboard feature bulletins:** right-sidebar announcements (~160 chars).
- **Feature preview dialog:** opt-in previews — no feature stays in preview >2 months unmonitored.
- **Lifecycle labels:** Private Preview, Public Preview, GA.

**Restraints:** Keep onboarding close to where the feature lives. No more than 2 alerts at a time. Define clear triggers, timebox campaigns, cap impressions. Preserve context (open CTAs in a new tab). Make dismissal clear. Never leave announcement campaigns running forever.

---

## 9. Degraded Experiences

**Problem:** Keep the app functional when optional dependencies fail. "Don't try to conceal or downplay that something is wrong. Communicate that there is a problem and guide users around it."

**Primary vs. secondary:** Primary experiences are essential (issue title/description); secondary enrich but aren't essential (notification counters). Degrade secondary; protect primary.

**Approaches:**
- **Global system notifications:** Banner at top, `warning` variant, link to status/support.
- **Small/inline elements:** replace with a brief error message + warning icon (`fg.warning`). Don't over-use warning color.
- **Larger panels:** Blankslate with an alert icon (`fgColor-muted`), optional title, secondary text + workaround link.
- **Partial data / missing counts:** hide the number rather than show broken UI.
- **Navigation:** never suppress the entire global header — remove only affected items; hide count badges if data is missing.
- **Dialogs:** non-critical — prevent opening / remove the trigger; critical — replace content with a Blankslate.
- **Non-functional buttons:** removing disorienting? No → remove. Yes → responds with an explanation on hover/click? Yes → inactive state; No → disabled state. (Never hide "Request changes".)
- **ActionLists/menus:** use the inactive item state to keep options visible but non-functional.

**Constraints:** Limit to 5 or fewer outage messages per page. Never disable interactive controls for availability issues — use the inactive state. Maintain accessible contrast on inactive labels. Never remove critical UI (comment boxes, submit buttons, "Request changes").

---

## 10. Data Visualization

**Problem:** Communicate complex information accessibly and engagingly (dashboards, insights).

**Chart types:** Supported — bar, line, area, progress bars. Not currently supported — donut charts, sparklines.

**Anatomy & labeling:** Header (required), axis labels (required, self-understandable, `4.5:1` contrast), legend (required for multiple datasets; omit for single), tooltip on hover (required), toolbar menu (table preview + CSV download — required for most charts). Axes need `3:1` contrast using `--borderColor-default` tokens.

**Recommended limits:** Line ≤5 lines; stacked area max 3 (hard limit 5); bar/column up to 10 bars, grouped ≤4 per group, stacked ≤5 segments; pie/donut ≤5 slices.

**Color & accessibility:** Never rely on color alone — you can't keep `3:1` between all colors across the color-blindness spectrum. All marks meet `3:1` against background; text `4.5:1`. Differentiate lines with stroke style (solid/dashed/dotted) and varied markers. Muted colors only with an outline. 2px width for mark and plot lines.

**Do:** Use muted colors with outlines; vary line styles and markers; keep to recommended limits.
**Don't:** Use muted colors without outlines; rely solely on color; exceed recommended limits.

*Source: all 10 pages under `primer.style/product/ui-patterns/`.*
