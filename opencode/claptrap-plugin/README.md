# Claptrap Plugin

An OpenCode plugin that helps agents accumulate knowledge across sessions. It nudges them to load relevant skills and recall memory before working, logs lightweight activity, and runs background reviews that turn verified procedures into reusable skills.

## Install

```bash
python3 ../../bootstrap/install.py
```

This symlinks everything here into `~/.config/opencode/`. Then merge these into `~/.config/opencode/opencode.json`:

```jsonc
{
  "instructions": ["~/.config/opencode/claptrap/instructions.md"],
  "plugin": ["./claptrap/plugin.ts"],
  "provider": {
    "9router": {
      "models": {
        "skill-gardener": { "name": "Skill Gardener" },
        "skill-harvester": { "name": "Skill Harvester" }
      }
    }
  }
}
```

Use `~/` or an absolute path for `instructions`. A relative entry like `./claptrap/instructions.md` resolves against your *project* directory, not the config file, so it silently loads nothing.

## Layout

| Path | Purpose |
| --- | --- |
| `plugin.ts` | Hooks, tools, event logging, background run scheduling |
| `logic.ts` | Pure logic, unit-tested |
| `instructions.md` | Injected into every session |
| `agents/` | `ct-gardener`, `ct-skill-harvester` |
| `commands/` | `/ct-status`, `/ct-run-gardener`, `/ct-learn-skill` |
| `tests/` | `bun test` |

## How it works

During a session, the plugin reminds the agent to recall memory before its first edit and to store anything durable before finishing. It records metadata — event type, skill name, tool name, project path, timestamp — to `~/.local/state/claptrap/events.jsonl`. Prompts, responses, and memory contents are never logged.

Two agents review that work in the background. **`ct-skill-harvester`** runs after a session goes idle, reads one transcript, and conservatively creates or updates at most one skill. **`ct-gardener`** runs weekly for library-wide upkeep: merging, splitting, simplifying, archiving, and restoring.

Generated skills are written outside this directory: repo-specific ones to `<project>/.agents/skills/claptrap/ct-*/`, cross-project ones to `~/.agents/skills/claptrap/ct-*/`. Project-scoped skills live in that project's own repository.

Both agents only touch skills carrying all three markers — a `skills/claptrap/` root, a `ct-` directory prefix, and `managed-by: ct-gardener` in frontmatter. Everything else is read-only, and archiving moves a skill to `skills-archive/claptrap/` rather than deleting it.

## Commands

- `/ct-status` — recent skill, memory, and background-run activity
- `/ct-run-gardener` — start the weekly review now
- `/ct-learn-skill` — capture learning from the current session

## Development

```bash
bun test
```

Keep testable logic in `logic.ts`; `plugin.ts` holds the OpenCode integration. Rerun the installer after renaming any file here, since the symlinks point at specific paths.
