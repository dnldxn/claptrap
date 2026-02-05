# Installer Revamp Design

**Date:** 2025-02-04
**Status:** Approved

## Overview

Revamp the claptrap installer to be drastically simpler while supporting all 6 environments: Claude Code, OpenCode, GitHub Copilot, Codex, Gemini, and Cursor.

## Goals

1. **Minimal code** - The installer should be ~50-80 lines of logic
2. **Single config file** - All environment differences in one YAML file
3. **Multi-environment sync** - Single install to all environments
4. **Clean file management** - Add/remove files properly without touching user files
5. **Central model registry** - Source files use aliases, config maps to environment-specific values

## Non-Goals

- Project-level installation (global only)
- Agentic installation approach
- Supporting TOML command format (Gemini commands skipped)

## Architecture

### File Structure

```
bootstrap/
├── claptrap.yaml          # Single declarative config
├── install.py             # Minimal installer (~80 lines)
├── lib/
│   └── output.py          # Colored terminal output (existing)
└── templates/
    └── agents_md.txt      # AGENTS.md injection template (existing)

src/
├── agents/*.md            # Model alias: "model: sonnet"
├── commands/*.md          # Model alias: "model: opus"
└── skills/*/SKILL.md      # No model (skills are universal)
```

### Target Structure (per environment)

```
~/.config/opencode/                    # Example: OpenCode
├── claptrap/                          # Staging area (transformed files)
│   ├── agents/
│   │   └── code-reviewer.md
│   ├── commands/
│   │   └── claptrap-refactor.md
│   └── skills/
│       └── claptrap-memory/
│           └── SKILL.md
│
├── agents/
│   ├── code-reviewer.md → ../claptrap/agents/code-reviewer.md
│   └── user-agent.md                  # User's own file (untouched)
│
├── commands/
│   └── claptrap-refactor.md → ../claptrap/commands/claptrap-refactor.md
│
└── skills/
    ├── claptrap-memory/ → ../claptrap/skills/claptrap-memory/
    └── user-skill/                    # User's own skill (untouched)
```

## Configuration Schema

```yaml
# bootstrap/claptrap.yaml

source_dir: src
skip_patterns: ["**/AGENTS.md", "**/README.md", "**/_archive/**", "**/templates/**"]

# Model alias registry - source files use these aliases
models:
  sonnet:
    opencode: anthropic/claude-sonnet-4-5
    claude: sonnet
    cursor: anthropic/claude-sonnet-4.5
    github-copilot: claude-sonnet-4.5
    codex: gpt-5.1-codex
    gemini: gemini-2.5-pro
  
  opus:
    opencode: anthropic/claude-opus-4-5
    claude: opus
    cursor: anthropic/claude-opus-4.5
    github-copilot: claude-opus-4.5
    codex: gpt-5.2
    gemini: gemini-2.5-pro
  
  gpt5-codex:
    opencode: openai/gpt-5.1-codex
    github-copilot: gpt-5.1-codex
    codex: gpt-5.1-codex

# Common hook definitions (canonical event names)
hooks:
  session_end:
    command: "./scripts/capture-learnings.sh"
    matcher: "*"
  
  post_tool:
    command: "npm run lint:fix ${FILE}"
    matcher: "Write|Edit"

# Default feature configuration
defaults:
  agents:
    dir: agents
    suffix: .md
  commands:
    dir: commands
    suffix: .md
  skills:
    dir: skills

# Environment-specific overrides (only specify what differs)
environments:
  opencode:
    root: ~/.config/opencode
    hooks:
      file: opencode.jsonc
      events:
        session_end: session.idle
        post_tool: tool.execute.after
  
  claude:
    root: ~/.claude
    hooks:
      file: settings.json
      events:
        session_end: Stop
        post_tool: PostToolUse
  
  github-copilot:
    root: ~/.copilot
    agents:
      suffix: .agent.md
    commands:
      dir: prompts
      suffix: .prompt.md
    hooks:
      file: copilot-hooks.json
      events:
        session_end: sessionEnd
        post_tool: postToolUse
  
  cursor:
    root: ~/.cursor
    skills: false  # Not supported
    hooks:
      file: hooks.json
      events:
        session_end: stop
        post_tool: postToolUse
  
  codex:
    root: ~/.codex
    agents: false  # Not supported
    commands:
      dir: prompts
    hooks: false  # Not supported
  
  gemini:
    root: ~/.gemini
    agents: false  # Not supported
    commands: false  # Uses TOML, skip
    hooks:
      file: settings.json
      events:
        session_end: SessionEnd
        post_tool: AfterTool
```

## Source File Format

Source files use simple model aliases instead of per-environment mappings:

**Before (current):**
```yaml
---
name: "code-reviewer"
description: "Reviews code changes"
model: claude-sonnet-4.5
models:
    cursor: anthropic/claude-sonnet-4.5
    github-copilot: Claude Sonnet 4.5
    claude: sonnet
    opencode: openai/gpt-5.2-codex
    gemini: gemini-2.5-pro
    codex: gpt-5.1-codex
---
```

**After:**
```yaml
---
name: code-reviewer
description: Reviews code changes
model: sonnet
---
```

**Skills:** No `model:` field - skills are a universal standard per [agentskills.io/specification](https://agentskills.io/specification).

## Installer Logic

### Install Process

1. **Load config** - Parse `claptrap.yaml`, merge defaults into environments
2. **For each environment:**
   a. Clean up existing symlinks pointing to `{root}/claptrap/`
   b. Delete `{root}/claptrap/` staging directory
   c. Copy and transform files to `{root}/claptrap/`
   d. Create symlinks from feature dirs into staging
   e. Generate hooks JSON (if supported)

### Cleanup Algorithm

```python
def cleanup(root: Path):
    """Remove claptrap symlinks and staging directory."""
    staging = root / "claptrap"
    
    # Remove symlinks pointing into staging
    for feature_dir in [root / "agents", root / "commands", root / "skills"]:
        if not feature_dir.exists():
            continue
        for item in feature_dir.iterdir():
            if item.is_symlink():
                try:
                    item.resolve().relative_to(staging)
                    item.unlink()
                except ValueError:
                    pass  # Not our symlink
    
    # Delete staging directory
    shutil.rmtree(staging, ignore_errors=True)
```

### Model Transform

```python
def transform_model(content: str, env: str, models: dict) -> str:
    """Replace model alias with environment-specific value."""
    def replace(m):
        alias = m.group(1)
        if alias in models and env in models[alias]:
            return f"model: {models[alias][env]}"
        return ""  # Remove line if no mapping
    return re.sub(r"^model:\s*(\S+)\s*$", replace, content, flags=re.MULTILINE)
```

### Symlink Creation

- **Agents/Commands:** File symlinks (e.g., `agents/code-reviewer.md → claptrap/agents/code-reviewer.md`)
- **Skills:** Directory symlinks (e.g., `skills/claptrap-memory/ → claptrap/skills/claptrap-memory/`)

Skills use directory symlinks because they can contain multiple files (SKILL.md, scripts/, references/).

## Hooks Generation

Each environment uses different event names and JSON structure. The installer:

1. Reads common hook definitions from config
2. Maps canonical event names to environment-specific names
3. Generates the appropriate JSON structure
4. Writes to the hook config file

**Example output for Claude (`~/.claude/settings.json`):**
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "./scripts/capture-learnings.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "npm run lint:fix ${FILE}" }
        ]
      }
    ]
  }
}
```

## Migration Plan

### Files to Delete

- `bootstrap/lib/providers.py` - Replaced by YAML config
- `bootstrap/lib/frontmatter.py` - Simplified inline

### Files to Keep

- `bootstrap/lib/output.py` - Colored terminal output
- `bootstrap/lib/memory.py` - Memory system setup (may simplify later)
- `bootstrap/templates/agents_md.txt` - AGENTS.md injection

### Files to Create

- `bootstrap/claptrap.yaml` - Declarative config
- `bootstrap/install.py` - New minimal installer (replaces existing)

### Source File Updates

Update all files in `src/agents/` and `src/commands/` to use model aliases:
- Remove `models:` dict
- Change `model:` value to alias (e.g., `sonnet`, `opus`, `gpt5-codex`)

## Minimal Installer Code

```python
#!/usr/bin/env python3
"""Claptrap Installer - Installs agents, commands, skills to all environments."""

import json
import re
import shutil
import yaml
from pathlib import Path

CONFIG = yaml.safe_load(Path(__file__).parent.joinpath("claptrap.yaml").read_text())
MODELS = CONFIG["models"]
DEFAULTS = CONFIG["defaults"]
SKIP = {"AGENTS.md", "README.md"}

def transform_model(content: str, env: str) -> str:
    def replace(m):
        alias = m.group(1)
        return f"model: {MODELS[alias][env]}" if alias in MODELS and env in MODELS[alias] else ""
    return re.sub(r"^model:\s*(\S+)\s*$", replace, content, flags=re.MULTILINE)

def cleanup(root: Path):
    staging = root / "claptrap"
    for feature in ["agents", "commands", "skills"]:
        feature_dir = root / feature
        if not feature_dir.exists():
            continue
        for item in feature_dir.iterdir():
            if item.is_symlink():
                try:
                    item.resolve().relative_to(staging)
                    item.unlink()
                except (ValueError, OSError):
                    pass
    shutil.rmtree(staging, ignore_errors=True)

def install_feature(src_dir: Path, staging_dir: Path, feature_dir: Path, suffix: str, env: str, is_skill: bool):
    staging_dir.mkdir(parents=True, exist_ok=True)
    feature_dir.mkdir(parents=True, exist_ok=True)
    
    for src in src_dir.rglob("*"):
        if not src.is_file() or src.name in SKIP or "_archive" in src.parts:
            continue
        rel = src.relative_to(src_dir)
        
        # Determine staging path
        if is_skill:
            staged = staging_dir / rel
        else:
            staged = staging_dir / (rel.stem + suffix) if suffix != ".md" else staging_dir / rel
        
        # Copy with transform (skills don't have models)
        staged.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text()
        staged.write_text(content if is_skill else transform_model(content, env))
        
        # Create symlink
        if is_skill:
            # Symlink entire skill directory
            skill_name = rel.parts[0]
            link = feature_dir / skill_name
            target = staging_dir / skill_name
            if not link.exists() and target.is_dir():
                link.symlink_to(target.relative_to(feature_dir))
        else:
            link = feature_dir / staged.name
            link.symlink_to(staged.relative_to(feature_dir))

def main():
    src_root = Path(CONFIG["source_dir"])
    
    for env, cfg in CONFIG["environments"].items():
        root = Path(cfg["root"]).expanduser()
        staging = root / "claptrap"
        
        cleanup(root)
        
        for feature in ["agents", "commands", "skills"]:
            feat_cfg = cfg.get(feature, DEFAULTS.get(feature))
            if feat_cfg is False:
                continue
            is_skill = feature == "skills"
            suffix = ".md" if is_skill else feat_cfg.get("suffix", ".md")
            install_feature(
                src_root / feature,
                staging / feature,
                root / feat_cfg["dir"],
                suffix,
                env,
                is_skill
            )
        
        print(f"Installed to {root}")

if __name__ == "__main__":
    main()
```

## Decisions

1. **Existing install.py features** - Keep global skills installation (`npx skills add`), `.claptrap/` setup, gitignore updates, MCP checks.

2. **Hook JSON handling** - Overwrite the hooks file entirely (don't merge with existing).

3. **Windows compatibility** - Not needed. On Windows, installer runs in WSL (Linux).

## Success Criteria

- [ ] Config file captures all environment differences
- [ ] Installer is under 100 lines of logic
- [ ] Adding new environment = add config block only
- [ ] Clean reinstall works (no dangling symlinks, no orphan files)
- [ ] User files are never touched
- [ ] Model transforms work correctly
- [ ] Skills copy without transformation
