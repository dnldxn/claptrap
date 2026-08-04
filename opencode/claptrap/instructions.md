## Continuous learning with OpenCode Skills and Mnemosyne

Before substantive work on any non-trivial, resumed, unfamiliar, or failure-prone task:

1. Inspect the available OpenCode Skills.
2. Load every Skill that could plausibly help. When uncertain between loading a concise Skill and skipping it, load it.
3. Before your first file edit, write, or mutating bash command in a session, you must have called `mnemosyne_recall` at least once, or explicitly state in your response why the task needs no prior context. The Claptrap plugin verifies this and will inject a reminder if skipped. Retrieve only a small set of relevant memories.
4. Treat current code, tests, configuration, and documentation as more authoritative than recalled memories.

During and after the work:

- Before your final message in a session where you made a durable decision, root-caused a bug, verified a reusable procedure, or changed a convention, call `mnemosyne_remember` — or explicitly state there is nothing worth storing.
- Do not store temporary status, obvious facts, complete transcripts, secrets, credentials, or information already clear in current project files.
- When the current work produces a verified reusable procedure, update an existing managed `ct-*` Skill or create one. Prefer improving an existing managed Skill over creating a near-duplicate. Background skill-harvester now reviews sessions after idle, but still create/update a `ct-*` Skill yourself for clearly verified procedure rather than deferring everything.
- Put repository-specific procedures in `<repo>/.agents/skills/claptrap/ct-*/SKILL.md`.
- Put genuinely cross-project procedures in `~/.agents/skills/claptrap/ct-*/SKILL.md`.
- Never modify a Skill unless it is under a `skills/claptrap/` or `skills-archive/claptrap/` root, its immediate directory starts with `ct-`, and its metadata contains `managed-by: ct-gardener`.
- It is valid to conclude that nothing is worth storing or turning into a Skill.

Always state briefly when you load a Skill, recall or store Mnemosyne memory, or create, update, merge, split, archive, or restore a managed Skill.
