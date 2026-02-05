# Claptrap Memory System Design

**Date**: 2025-02-02  
**Status**: Design Complete, Implementation Pending  
**Author**: Claude + User collaboration

## Problem Statement

AI coding agents under-capture durable project knowledge. Current single-file memory approaches fail because:

1. **Wrong timing**: Only captures at end-of-work, missing in-the-moment insights
2. **Vague filtering**: No clear criteria for what's worth keeping
3. **No enforcement**: Nothing ensures agents actually capture learnings

**Result**: Context is lost between sessions, leading to repeated mistakes and rediscovery.

## Solution Overview

A **two-file, two-skill memory system** with **hard enforcement via hooks**:

```
┌─────────────────────────────────────────────────────────────┐
│                    During Work                               │
│  Agent detects learning → Writes to memory_inbox.md         │
│  (High recall, captures candidates liberally)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Periodically                              │
│  Curator skill reviews inbox → Promotes to memories.md      │
│  (High precision, applies quality rubric)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Session End                               │
│  Enforcement hook checks: work done + inbox empty?          │
│  If yes → Blocks until agent reviews learnings              │
└─────────────────────────────────────────────────────────────┘
```

## Data Model

### File Structure

```
.claptrap/
├── memory_inbox.md      # Capture candidates (high recall)
├── memories.md          # Durable memories (high precision)
└── enforcement.py       # Hook enforcement script
```

### memory_inbox.md Format

```markdown
## [YYYY-MM-DD] - [Brief Title]
- **Trigger**: What prompted this learning
- **Action**: What to do (or avoid) in future
- **Context**: When this applies
```

### memories.md Format

```markdown
## [Category] - [Clear Title]

**When**: [Specific trigger condition]
**Do**: [Specific action to take]
**Why**: [Brief rationale if not obvious]
```

**Categories**: Architecture, Patterns, Anti-patterns, Conventions, Dependencies, Testing, Performance

## Two-Skill Design

### Skill A: Memory Capture

**Purpose**: Capture learnings during work sessions

**Triggers**:
- Made a non-obvious technical decision
- Discovered something that would help future sessions
- Identified a pattern worth repeating
- Encountered an anti-pattern to avoid
- Gained context that isn't in the code

**Output**: Entries in `.claptrap/memory_inbox.md`

### Skill B: Memory Curator

**Purpose**: Review inbox and promote quality entries

**Rubric** (0-8 scale):

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| **Recurrence** | One-time | Occasional | Definite |
| **Impact** | Minor | Moderate | Significant |
| **Actionability** | Vague | Somewhat clear | Crystal clear |

**Thresholds**:
- ≥6: Promote to memories.md
- 4-5: Keep in inbox for more context
- ≤3: Remove from inbox

## Enforcement Strategy

### Soft Enforcement (All 6 Environments)

SKILL.md-based prompts that remind agents to capture learnings:
- During-work triggers
- Session-end checklist

### Hard Enforcement (5/6 Environments)

Hook-based gate at session end:

```python
def session_end_gate():
    activity = get_session_activity()
    inbox_entries = get_inbox_entry_count()
    
    # If work was done but inbox empty, block
    if activity["has_changes"] and inbox_entries == 0:
        return 2  # Block with prompt
    return 0  # Allow
```

**Hook Events by Environment**:

| Environment | Session End Event | Post-Tool Event | Supported |
|-------------|-------------------|-----------------|-----------|
| Claude Code | `Stop` | `PostToolUse` | ✅ |
| OpenCode | `session.idle` | `tool.execute.after` | ✅ |
| Cursor | `stop` | `postToolUse` | ✅ |
| GitHub Copilot | `sessionEnd` | `postToolUse` | ✅ |
| Gemini | `SessionEnd` | `AfterTool` | ✅ |
| Codex | N/A | N/A | ❌ (soft only) |

## Architecture

### Single Source of Truth

All environments share:
- ONE `enforcement.py` script
- ONE hooks config generator
- ONE provider configuration

```
bootstrap/
├── install.py           # Main installer
└── lib/
    ├── providers.py     # Provider config with hooks metadata
    ├── memory.py        # Memory installation logic
    ├── enforcement.py   # Enforcement script (copied to .claptrap/)
    ├── frontmatter.py   # YAML frontmatter utilities
    └── output.py        # Terminal output helpers
```

### Provider Configuration

Each provider includes hooks metadata in `lib/providers.py`:

```python
"claude": {
    "name": "Claude",
    "dir": ".claude",
    "hooks_config_path": "settings.json",
    "hooks_events": {
        "session_end": "Stop",
        "post_tool": "PostToolUse",
    },
}
```

### Installation Flow

```
install.py
    │
    ├── Step 4: Memory System Setup
    │   ├── Create memory_inbox.md (from template)
    │   ├── Create memories.md (from template)
    │   ├── Copy enforcement.py to .claptrap/
    │   └── Generate & install hooks config for provider
    │
    └── Step 5: Copy skills (includes memory-capture, memory-curator)
```

## Implementation Checklist

### Completed

- [x] Research hooks across all 6 environments
- [x] Document hooks in `docs/*.md` for each environment
- [x] Design two-file data model
- [x] Design two-skill system with rubric
- [x] Design enforcement strategy (soft + hard)
- [x] Create `bootstrap/lib/` module structure
- [x] Implement `lib/providers.py` with hooks metadata
- [x] Implement `lib/memory.py` installation logic
- [x] Implement `lib/enforcement.py` script
- [x] Integrate into `bootstrap/install.py`
- [x] Create `memory_inbox_md.txt` template
- [x] Create `src/skills/memory-capture/SKILL.md`
- [x] Create `src/skills/memory-curator/SKILL.md`
- [x] Update `src/skills/claptrap-memory/SKILL.md`

### Remaining

- [ ] Test installation across environments
- [ ] Add memory system to AGENTS.md template

## Superpowers Compatibility

The memory system integrates with [Superpowers](https://github.com/obra/superpowers):

1. **Skills follow conventions**: SKILL.md format with proper frontmatter
2. **Loadable via Skill tool**: `Use the memory-capture skill`
3. **Non-conflicting**: Data in `.claptrap/`, separate from environment dirs
4. **Composable**: Other skills can reference memory files

## Open Questions

1. **Inbox pruning**: Should old un-promoted entries auto-expire?
2. **Memory search**: Should there be a skill to search memories?
3. **Cross-project**: Should some memories be global (in `~/.claptrap/`)?

## References

- Original proposal: `/Users/ddixon/projects/claptrap/claptrap_memory_summary.md`
- Environment docs: `docs/claude-code.md`, `docs/opencode.md`, etc.
- Existing skill: `src/skills/claptrap-memory/SKILL.md`
