# Claptrap Plugin

## Commands

```bash
bun test                     # run from this directory
python3 ../../bootstrap/install.py   # relink after moving/renaming files here
```

## Constraints

- `plugin.ts` and `logic.ts` must stay siblings — `plugin.ts` imports `./logic`, resolved against the symlink's real path in this repo. Only `plugin.ts` is symlinked; `logic.ts` must not get its own link.
- Keep pure, testable logic in `logic.ts`. `tests/` imports from `../logic.ts` only; `plugin.ts` is not unit-tested.
- Install targets are fixed: `instructions.md` and `plugin.ts` link to `~/.config/opencode/claptrap/`, while `agents/` and `commands/` link to `~/.config/opencode/{agents,commands}/claptrap`. Renaming a file here breaks the link until `install.py` is rerun.
- Managed skills are never stored in this directory. They are written to `<project>/.agents/skills/claptrap/ct-*/` or `~/.agents/skills/claptrap/ct-*/`, which are the only roots `scanSkillRoot` counts. Adding a skills directory here would be invisible to the plugin.
- Managed skills require all three markers: a `skills/claptrap/` or `skills-archive/claptrap/` root, a `ct-` directory prefix, and `managed-by: ct-gardener` in frontmatter. `ct-gardener` is the literal value even for skills the harvester writes; anything else silently drops the skill from ownership.
- Agents in `agents/` need a matching `9router/<alias>` model registered in `~/.config/opencode/opencode.json`, or a detached run fails with no visible diagnostic.
- Log only metadata to `events.jsonl` — event type, skill/tool name, project path, timestamp. Never prompts, responses, skill contents, or memory contents.

## Runtime state (outside this repo)

`~/.local/state/claptrap/` holds `events.jsonl`, `{gardener,harvester}.log`, `last-{gardener,harvester}-summary.md`, and `*.lock` directories.
