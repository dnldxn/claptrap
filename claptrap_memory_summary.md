Here’s the proposed “Option 1” memory upgrade, end-to-end: **capture-anything (high recall) → score + threshold (high precision) → persist durable playbooks**, enforced by hooks so the agent can’t “forget to remember.” It runs **entirely inside your Claude subscription** for the deciding/scoring; the storage is plain Markdown files in-repo.

---

## Goal

Create a lightweight, repo-native memory system that:
- captures candidate “lessons learned” continuously (not only failures),
- curates them deterministically via a scoring rubric + threshold,
- persists only high-value, verifiable, repo-relevant entries,
- prevents memory bloat via update-over-add,
- blocks “stop” if there are uncurated candidates,
- is portable across other agent environments via adapters.

---

## Data model (canonical and portable)

These two files are the durable interface and should remain identical across all environments:

- `.claptrap/memory_inbox.md` — **high-recall** candidate inbox (cheap, structured, noisy allowed)
- `.claptrap/memories.md` — **high-precision** durable memory store (small, verifiable, actionable, newest-first)

This separation fixes the core failure mode of single-file memory: either you save junk, or you save nothing.

---

## Two-skill design

### Skill A: Memory Capture (high recall)
**Job:** write candidate blocks to `.claptrap/memory_inbox.md` as you notice potentially durable knowledge—*not just on incidents*.

Key constraints:
- Candidate **must** include `Trigger` + `Action`.
- `Verify` can be `unknown` but usually won’t survive curation.
- Never store secrets.

### Skill B: Memory Curator (high precision)
**Job:** score candidates (0–12) and:
- persist winners (≥ 8) to `.claptrap/memories.md`,
- keep borderline (6–7) in inbox for later confirmation,
- drop weak (≤ 5) candidates,
- update existing entries instead of duplicating.

This makes “important” a deterministic decision rather than a vague “would it help?”

---

## Plugin package layout (Claude Code)

This is the recommended distribution shape (shareable, namespaced):

```text
claptrap-memory/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── hooks.json
├── skills/
│   ├── memory-capture/
│   │   └── SKILL.md
│   └── memory-curate/
│       └── SKILL.md
├── commands/
│   ├── memory-capture.md
│   └── memory-curate.md
└── scripts/
    ├── ensure_memory_files.py
    ├── session_start_context.py
    ├── stop_gate.py
    └── utils_memory.py
```

---

## Claude Code plugin files (full content)

### 1) `.claude-plugin/plugin.json`

```json
{
  "name": "claptrap-memory",
  "description": "High-recall memory capture + deterministic curation for .claptrap/memories.md",
  "version": "1.0.0",
  "author": { "name": "You" }
}
```

---

### 2) `hooks/hooks.json`

Hooks do four things:

- `SessionStart`: inject a short “memory briefing” (top memories + operating rules)
- `UserPromptSubmit`: ensure memory files exist + add a lightweight reminder
- `PostToolUseFailure`: provide a small nudge to capture candidates when a non-obvious insight emerges
- `Stop`: **block** stop if uncurated candidates exist, forcing a curate pass

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}\"/scripts/session_start_context.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}\"/scripts/ensure_memory_files.py"
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}\"/scripts/stop_gate.py --mode nudge"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}\"/scripts/stop_gate.py --mode gate"
          }
        ]
      }
    ]
  }
}
```

**Behavioral notes (no code):**
- `ensure_memory_files.py` creates `.claptrap/` and initializes both Markdown files if missing.
- `session_start_context.py` reads the newest memory headings from `.claptrap/memories.md` and prints additional context so the agent “starts primed.”
- `stop_gate.py`:
  - in `--mode gate`: checks if inbox has any candidates; if yes, returns a JSON “block” decision with next-step instructions
  - avoids infinite recursion by honoring the stop hook’s “already active” flag
- `utils_memory.py` contains small helpers: parse candidates, read/write files, extract a memory briefing.

---

### 3) `skills/memory-capture/SKILL.md`

```md
---
description: High-recall capture of candidate memories into .claptrap/memory_inbox.md
---

# Memory Capture

You maintain a lightweight memory system:
- Durable memories: `.claptrap/memories.md`
- Candidate inbox: `.claptrap/memory_inbox.md` (high recall, low precision)

## Your job
Continuously capture *candidate* lessons while working, not only on failures.

### Trigger signals (broad)
Capture a candidate when ANY of these happen:
- A non-obvious decision/tradeoff/convention is chosen
- A “gotcha” is discovered (env/tooling/CI/build/docs)
- The user corrects a misconception or states a preference that should persist
- A pattern or anti-pattern emerges while implementing
- A multi-step procedure is performed that is easy to forget
- You discover a constraint that future changes could violate

### Candidate format (required fields)
Write candidates to `.claptrap/memory_inbox.md` with **this exact shape**:

## Candidate: <short title>
Context: <area/module>
Trigger: <when this applies; include a recognizable signature/error/message if possible>
Action: <what to do / what to avoid>
Verify: <how to confirm; command or observable result; use "unknown" if not available>
Why it matters: <1 sentence>
Tags: <comma list>

Rules:
- If you cannot state BOTH Trigger and Action, do NOT capture.
- If Verify is unknown, still capture but mark it `Verify: unknown` (curation will likely reject).
- Never store secrets or sensitive data (keys, tokens, customer data, private logs).

### Behavior
- Prefer 1–3 high-quality candidates over many weak ones.
- Capture candidates as soon as the insight appears (don’t wait until the end).
- Do NOT write to `.claptrap/memories.md` in this skill; only to the inbox.
```

---

### 4) `skills/memory-curate/SKILL.md`

```md
---
description: Score candidates in .claptrap/memory_inbox.md and persist winners to .claptrap/memories.md
---

# Memory Curator

You curate candidate memories into durable entries.

## Inputs
- Candidates: `.claptrap/memory_inbox.md`
- Durable store: `.claptrap/memories.md`

## Scoring rubric (0–12)
Score each candidate:

- Recurrence (0–3): 0 one-off; 1 might recur; 2 likely; 3 recurring already
- Impact (0–3): 0 minor; 1 annoyance; 2 hours saved / prevents regressions; 3 high-stakes (data loss, prod break, security)
- Specificity (0–2): 0 generic; 1 somewhat concrete; 2 concrete signature + precise action
- Verifiability (0–2): 0 no verify; 1 plausible; 2 explicit test/command/output
- Repo-locality (0–2): 0 generic; 1 partly repo-specific; 2 clearly repo-specific

Threshold decisions:
- Score >= 8  => persist to `.claptrap/memories.md`
- Score 6–7   => keep candidate (needs better Trigger/Verify), do NOT persist yet
- Score <= 5  => drop candidate

## Persisted memory format (required)
Each saved memory must be short, durable, and action-oriented.

---
## <descriptive title>
Type: decision | pattern | anti-pattern | lesson | solution | architectural decision
Date: YYYY-MM-DD | Confidence: low|med|high | Scope: repo|project|general | Tags: tag1, tag2

Trigger: <when it applies>
Action: <what to do / avoid>
Verify: <how to confirm it worked>
---

Rules:
- Require Trigger + Action + Verify for persisted memories.
- If a memory already exists on the same concept/trigger, UPDATE it instead of adding a new entry:
  - Replace Action with better guidance
  - Add/upgrade Verify if you learned a better check
  - Update Date and Confidence if warranted
- Keep each entry 3–7 lines total (avoid essays).
- Newest entries at the top (after the file header).
- Never store secrets.

## End state after curating
- Winners moved into `.claptrap/memories.md`
- Dropped candidates removed from inbox
- “Needs work” candidates kept in inbox
```

---

### 5) Manual commands (optional)

`commands/memory-capture.md`

```md
---
description: Capture 1–3 candidate memories from the most recent work into the inbox
---

Run the /claptrap-memory:memory-capture skill now.

- Generate 1–3 candidates based on the most recent work in this session.
- Write them to .claptrap/memory_inbox.md in the required candidate format.
- Do not persist to memories.md in this step.
```

`commands/memory-curate.md`

```md
---
description: Curate candidates into durable memories using the scoring rubric
---

Run the /claptrap-memory:memory-curate skill now.

- Score each candidate using the rubric and thresholds.
- Persist only winners (>=8) into .claptrap/memories.md in the required format.
- Update existing entries instead of duplicating when applicable.
- Remove dropped candidates from inbox; keep 6–7 score candidates for later.
```

---

## Project-local configuration (if you don’t use the plugin)

If you’re not deploying a plugin, this is the equivalent hook config:

### `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session_start_context.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/ensure_memory_files.py"
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop_gate.py --mode nudge"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop_gate.py --mode gate"
          }
        ]
      }
    ]
  }
}
```

Then copy the four Python scripts into `.claude/hooks/` (same names).

---

## How this meets your “capture anything important” requirement

- Capture isn’t tied to tool failures: it triggers on *any durable insight* (decisions, gotchas, conventions, procedures, corrections).
- Curation is deterministic: a numeric rubric + threshold replaces vague “would it help?”
- Persisted entries require `Trigger + Action + Verify` so they’re usable during future debugging.
- Hook “Stop gate” enforces that curation happens; it’s not optional.

---

# Adapter system to deploy across environments

You’re right: the main variance is **hook syntax + lifecycle events**, not the underlying policy or file model.

## Adapter system concept

Maintain a single “core” memory kit, then deploy an environment-specific adapter that provides:
- hook wiring,
- skill/instruction placement,
- command equivalents.

### Canonical core (shared everywhere)
- `.claptrap/memory_inbox.md` + `.claptrap/memories.md`
- capture/curate rubrics (the SKILL.md content, re-used verbatim)
- the Python scripts (unchanged), or equivalent scripting language if needed

### Adapters (thin)
Each environment adapter provides:
- hook config file(s) in that environment’s expected location
- environment-specific variables/paths to invoke scripts
- any mapping necessary for lifecycle events (“session start”, “stop/end”, “tool failure”)
- optional “command” wrappers (slash commands, prompt files, etc.)

## Adapter deployment requirements

1) **Environment detection**
   - Detect environment via presence of config roots:
     - `.claude/` (Claude Code)
     - `.cursor/` (Cursor)
     - `.opencode/` (OpenCode)
     - `.github/` with Copilot instruction support (GitHub Copilot)
   - Support explicit `--env` override.

2) **Idempotent install**
   - Running install multiple times should not duplicate entries or break config.
   - Preserve user customizations; only modify managed sections.

3) **Path abstraction**
   - Adapters must compute correct paths to core scripts:
     - plugin root vs project dir vs global config dir
   - Avoid absolute paths; use environment variables where supported.

4) **Event mapping**
   - Map core events to environment equivalents:
     - `SessionStart` → start-of-session context injection
     - `Stop/SessionEnd` → final gate (“must curate”)
     - `PostToolUseFailure` → optional nudge
     - optional future: `PreCompact` → reinject rubric before context compaction
   - Provide best-effort fallbacks for environments lacking a “block stop” capability.

5) **Instruction integration**
   - Ensure capture and curate instructions are loaded reliably:
     - In plugin-based envs: ship as skills
     - In instruction-file envs: write to a standard instructions file
     - In prompt-file envs: install capture/curate prompt templates

6) **Cross-platform execution**
   - Scripts must run on macOS/Linux/WSL; adapter must handle:
     - `python3` availability
     - executable bit or explicit `python3 file.py`
     - line endings

7) **Safety controls**
   - Ensure “no secrets” rule is included in every environment’s instruction set.
   - Optional: add a lightweight redaction step before writing candidates (adapter-configurable).

8) **Uninstall / disable**
   - Provide a clean way to remove or disable the adapter:
     - delete managed hook config sections
     - leave `.claptrap/memories.md` untouched (it’s user data)

## Environment capability expectations

- Claude Code: supports hooks + stop blocking + plugins (best enforcement).
- Cursor: supports hooks; adapter mostly translates hook config.
- OpenCode: supports plugins; adapter may reimplement gating via its plugin event model.
- GitHub Copilot: supports instructions/prompt files; may not support deterministic stop-blocking, so enforcement may be “soft” (reminders + command prompts).

---

# System requirements for the proposed solution

## Functional requirements

1) **Two-file memory model**
   - Must maintain both inbox and durable memory store.
   - Durable store must remain small and high signal.

2) **Capture-anything candidate generation**
   - Agent must capture candidates not limited to failures/incidents.
   - Candidate must include at minimum `Trigger` and `Action`.

3) **Deterministic curation**
   - Must score each candidate using the 0–12 rubric.
   - Must enforce threshold decisions (≥8 persist, 6–7 keep, ≤5 drop).

4) **Verifiable durable entries**
   - Persisted memories must include `Trigger + Action + Verify`.
   - Persisted entry format must be consistent and parsable (heading + metadata + 3 lines).

5) **Update over duplication**
   - System must prefer updating an existing memory over creating duplicates.
   - Must maintain newest-first ordering in `memories.md`.

6) **Stop-gate enforcement (where supported)**
   - If uncurated candidates exist, system must prevent ending the session until curated.
   - Must avoid infinite recursion (respect “already ran” flags).

7) **Session-start briefing**
   - Must surface a compact summary of recent memories at session start.

8) **Manual overrides**
   - Must provide explicit capture/curate commands for user-driven forcing.

## Non-functional requirements

1) **Low noise / low overhead**
   - Capturing candidates should be cheap and fast.
   - Curation should usually take <2 minutes.

2) **Portability**
   - Core model and rubrics must be environment-agnostic.
   - Adapters must be thin and easy to maintain.

3) **Security**
   - Must never store secrets or sensitive data.
   - Should minimize writing raw logs; prefer stable signatures.

4) **Idempotency**
   - Installing adapters multiple times must not duplicate config.
   - Memory files must not be corrupted.

5) **Auditability**
   - All memories are plain-text in git and reviewable in diffs/PRs.
   - Easy to prune or refactor.

6) **No external dependencies required for decision-making**
   - Importance scoring must work entirely within the agent’s reasoning (subscription-only).
   - External systems (e.g., Mem0, Letta) remain optional future enhancements.
