---
name: ct-manage-state-file
description: Use when a Claptrap workflow needs to update or resync `.planning/state.html` after spec, plan, implementation, review, merge, or archive changes.
---

Update `.planning/state.html` to reflect the current workflow state. Describe, in natural language, what just happened in the workflow. Infer the values for the template below from what just happened in the workflow. Use these guidelines:

- Which workflow state the project is now in.  Examples: `design`, `planning`, `implementation`, `code review`, `done`, etc.
- A short phrase describing what just happened, ideally with a filename or branch.  Examples: `wrote spec 2026-05-14-foo-spec.md`, `wrote plan 2026-05-14-01-foo-bar.md`, `started branch feature/foo`, `finished plan 2026-05-14-01-foo-bar.md`, `merged branch feature/foo`, etc.
- 1-2 sentence summary of the current situation.

If invoked manually with no context, only resync the file lists, branch, and timestamp; leave the existing state, last action, and summary unchanged.

## Update Procedure

1. If `.planning/state.html` is missing, create it from the template below. Ensure `.planning/state.html` is listed in the project root `.gitignore`.
2. Fill out the "State", "Last action", "Last updated", and "Branch" fields based on the most recent workflow event.
3. Rebuild file sections from disk:
   - Open specs: `.planning/specs/*.md`
   - Open plans: `.planning/plans/*.md`
   - Archived specs: `.planning/_archive/specs/*.md`
   - Archived plans: `.planning/_archive/plans/*.md`
4. For each listed file, use its title/header line (usually H1) plus first paragraph to write one sentence. If no H1 title, use the filename slug. Drop references to missing files; do not add deleted markers.
5. Generate very simple, basic, utilitarian HTML that is still clearly formatted and easy for humans to scan. Use inline CSS only; do not add JavaScript.
6. Put the lists of specs and plans in HTML tables (for both Open and Archived sections). Keep columns as `File` and `Summary`.

## state.html Template

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Workflow State</title>
  <style>
    :root { color-scheme: light dark; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
      line-height: 1.45;
      background: #f6f7f9;
      color: #1f2937;
    }
    main {
      max-width: 960px;
      margin: 2rem auto;
      padding: 1.25rem;
      background: #fff;
      border: 1px solid #d1d5db;
      border-radius: 8px;
    }
    h1, h2 { margin: 0 0 0.75rem; }
    dl {
      display: grid;
      grid-template-columns: 11rem 1fr;
      gap: 0.35rem 0.75rem;
      margin: 0 0 1rem;
    }
    dt { font-weight: 600; }
    dd { margin: 0; }
    p { margin: 0 0 1.25rem; }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 0 0 1.25rem;
      font-size: 0.95rem;
    }
    th, td {
      border: 1px solid #d1d5db;
      text-align: left;
      vertical-align: top;
      padding: 0.5rem 0.6rem;
    }
    thead th { background: #e5e7eb; }
    tbody tr:nth-child(even) td { background: #f9fafb; }
    .section-row td {
      font-weight: 600;
      background: #eef2f7;
    }
    code {
      font-family: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
      font-size: 0.9em;
    }
  </style>
</head>
<body>
  <main>
    <h1>Workflow State</h1>
    <dl>
      <dt>State</dt><dd>&lt;design | planning | implementation | code review | done | etc&gt;</dd>
      <dt>Last action</dt><dd>&lt;3-8 words; include filename or branch where relevant&gt;</dd>
      <dt>Last updated</dt><dd>&lt;Timestamp with this format: YYYY-mm-dd H:M:S &gt;</dd>
      <dt>Branch</dt><dd>&lt;current git branch&gt;</dd>
    </dl>

    <h2>Summary</h2>
    <p>&lt;1-2 sentences describing the current situation.&gt;</p>

    <h2>Open</h2>
    <table>
      <thead>
        <tr><th>File</th><th>Summary</th></tr>
      </thead>
      <tbody>
        <tr class="section-row"><td colspan="2">Specs</td></tr>
        <tr><td><code>&lt;filename&gt;</code></td><td>&lt;one-sentence summary&gt;</td></tr>
        <tr class="section-row"><td colspan="2">Plans</td></tr>
        <tr><td><code>&lt;filename&gt;</code></td><td>&lt;one-sentence summary&gt;</td></tr>
      </tbody>
    </table>

    <h2>Archived</h2>
    <table>
      <thead>
        <tr><th>File</th><th>Summary</th></tr>
      </thead>
      <tbody>
        <tr class="section-row"><td colspan="2">Specs</td></tr>
        <tr><td><code>&lt;filename&gt;</code></td><td>&lt;one-sentence summary&gt;</td></tr>
        <tr class="section-row"><td colspan="2">Plans</td></tr>
        <tr><td><code>&lt;filename&gt;</code></td><td>&lt;one-sentence summary&gt;</td></tr>
      </tbody>
    </table>
  </main>
</body>
</html>
```

When inserting dynamic text from files, escape HTML special characters (at minimum `&`, `<`, `>`, `"`, and `'`).
