# Primer Content / UX-Writing Reference

> Load this file when writing or reviewing UI copy — button labels, headings, error and empty-state messages, tooltips, dates, or terminology. Skip it for purely visual/structural work.

Source: GitHub Primer Content foundations (`primer.style/product/getting-started/foundations/content/`).

## Voice & tone

GitHub content should be: Clear but not cold · Conversational but not jargon-y · Inclusive but not disingenuous · Helpful but not overly-prescriptive.

- **Do** write plain English, in **active voice**, and be brief (cut adjectives/adverbs and filler).
- **Do** target roughly a **7th–8th grade reading level** (check with Grammarly / Hemingway).
- **Humor** is fine in a light sprinkle, but **never** in errors, loading states, or failures.
- Always have someone else proofread.

## Capitalization

- **Sentence case** everywhere: titles, labels, buttons, headings. When in doubt, don't capitalize.
- Capitalize only proper nouns and product names. "pull request" stays lowercase unless it starts a sentence.
- Always capitalize **GitHub** correctly.
- A label starting with a number keeps the number, lowercase after ("2 references").

## Punctuation

- **No punctuation** in headings, labels, or buttons.
- Exclamation marks are rarely appropriate.
- Avoid semicolons — use a period.
- Use **"and"**, not "&" or "+".
- Times: **"am/pm"** (not "a.m."/"A.M.").
- Don't use `>` / `<` to indicate step flow.

## Buttons & labels

- Start action labels with an **imperative verb**; may shorten to adjective + noun ("New issue").
- No end punctuation. Sentence case.
- Prefer **"sign in"** over "log in".
- Example: "Save email preferences" (not "Save email preferences.").

## Links

- Use clear, unique, informative link text. **Never** "here" / "click here".
- Give image links context via accompanying text.
- Example: "Find out more about our [GitHub Universe site]" (not "Click here to learn more").

## Error messages

- **Do** be friendly and specific; avoid jargon; don't blame the user; minimize apologies.
- Examples:
  - "Enter a credit card number" (not "Field required")
  - "All checks failed" (not "Sorry, all checks failed" / "Oops, some checks failed")

## Feedback / status messages

- Match the terminology of the UI element that triggered it; avoid humor/jargon.
- Example: "Issue transfer in progress" (matches the **Transfer** button) — not "Moving the issue".

## Referring to UI

- Non-clickable UI section: **quotation marks** ("Email notification settings").
- Clickable button/link: **bold, no quotes** (**Save**).
- Folders/paths: **code style** (`docs`).
- On mobile contexts, use **"tap"** instead of "click".

## Subject & person

- Address the user as **"you"**; user-owned things are **"your/yours"** ("Update your profile", not "Update my profile").
- Exception: legal/destructive confirmations use first person ("I understand…").

## Inclusive & accessible language

- **Avoid gendered language.**
- Avoid slang and culturally-specific references.
- Don't call tasks "easy", "quick", or use "just" — it can feel dismissive.
- **Avoid directional language** ("above"/"below") — prefer "first/last", "previous/next" — since order changes for AT and small screens.
- Explain abbreviations on first use. Minimize truncation.

## Emojis

- Avoid in general. If used: only at the end of a sentence, well-recognized ones, no repetition, don't replace words, and ensure they work in dark and light mode.

## Dates & time (terminology)

- **Relative time** ("a minute ago", "20 days ago") for recent items; switch to precise dates beyond ~1 month.
- **Sensitive precise dates** (certs, expirations): "Thursday, 26 August 2021".
- **Elapsed time:** show all non-zero units ("2 minutes, 24 seconds").
- **Date intervals:** same year `MMM DD - MMM DD, YYYY`; spanning years `MMM DD, YYYY - MMM DD, YYYY`.

## Top-10 quick rules (Primer's own list)

1. Write plainly; avoid robotic language. 2. Be brief. 3. Active voice. 4. Sentence case; minimize capitalization. 5. Capitalize "GitHub" correctly. 6. Avoid gendered language. 7. No slang/cultural references. 8. Never "here"/"click here" in CTAs. 9. Humor sparingly. 10. Have someone proofread.

*Canonical base: `primer.style/product/getting-started/foundations/content/`.*
