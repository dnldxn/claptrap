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

## Toasts

Every toast is also written to the OpenCode log. All stay visible for 5 seconds (`TOAST_MS` in `plugin.ts`).

| Trigger | Message | Variant |
| --- | --- | --- |
| `skill` tool call | `CT: loaded Skill <name>` | info |
| Managed Skill edited — via `file.edited`, or a bash command with a write indicator before a `skills/claptrap/ct-*` path | `CT: changed managed Skill <name>` | info |
| Background agent started | `CT: <agent> started in background` | info |
| Background agent result seen at next startup or idle | `CT: <agent> completed; run /ct-status` | success |
| Background agent failed, or a dead run reconciled | `CT: <agent> failed; check <agent>.log` | warning |
| Recall gate — first mutating tool with no `mnemosyne_recall` yet this session | `CT: mutating files without a Mnemosyne recall this session` | warning |
| Store gate — session idles after mutating without a `mnemosyne_remember` | `CT: session mutated files without storing a Mnemosyne memory` | warning |

Both gates fire at most once per session and never inside gardener or harvester runs. Routine Mnemosyne calls are recorded to `events.jsonl` and counted by `/ct-status`, but deliberately do not toast — they fire on every recall and store.

## Transcript lines

A toast disappears after 5 seconds. Four notices are important enough to also leave a permanent `CT: ...` line in the conversation history.

| Notice | How it lands | Rate limit |
| --- | --- | --- |
| Recall gate | appended to the triggering tool result | once per session |
| `CT: updated managed Skill <name>` | appended to the triggering tool result | once per skill per session |
| `CT: files changed with no Mnemosyne memory stored` | standalone message at idle | once per session |
| `CT: <agent> completed / failed` | standalone message at next idle | once per background run |

Everything else stays toast-only. Transcript text is permanent context — it is re-sent to the model on every later turn — so each line is one short sentence, and high-frequency events (skill loads, Mnemosyne recalls and stores) are deliberately excluded.

Standalone lines are posted with `session.promptAsync({ noReply: true })`. The text must not be marked `synthetic`: synthetic parts are stored and sent to the model but filtered out of every TUI render path, so they would be invisible to the user. Verified against a live server on OpenCode 1.18.11.

## Commands

- `/ct-status` — recent skill, memory, and background-run activity
- `/ct-run-gardener` — start the weekly review now
- `/ct-learn-skill` — capture learning from the current session

## Development

```bash
bun test
```

Keep testable logic in `logic.ts`; `plugin.ts` holds the OpenCode integration. Rerun the installer after renaming any file here, since the symlinks point at specific paths.
