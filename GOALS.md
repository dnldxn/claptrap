# Goals

## Purpose
To create an AI-powered development workflow that is provider/model agnostic, environment agnostic, easy to use, and built on open-source foundations.

## Core Principles
When goals conflict, prioritize in this order:
1. **Agnostic** - Works across providers and environments
2. **Simple** - Minimal complexity, clear patterns
3. **Modular** - Easy to plug in new adapters and capabilities
4. **Maintainable** - Sustainable for long-term use
5. **Popular** - Based on popular higher-level AI-based development tools/platforms (e.g. OpenSpec, claude-flow, etc.) that have frequent updates and are actively developed.

## Key Goals

### 1. Simple
Minimizes complexity, moving parts, dependencies, and abstractions to the essential minimum.

### 2. Provider/Model Agnostic
Works with multiple AI providers through their subscription plans (Cursor, GitHub Copilot, Claude, Codex, etc.) rather than per-request API billing. Best-effort compatibility across providers.

### 3. IDE/CLI/Environment Agnostic
Runs in multiple environments (Cursor, VS Code, OpenCode CLI, Codex CLI). Common features work everywhere; optional capabilities can be environment-specific.

### 4. Easy to Install and Use
Install in under 5 minutes with clear documentation, sensible defaults, and minimal configuration.

### 5. Modular
Easy to plug in new adapters and capabilities.  Adapters should be focused, self-contained, with minimal dependencies and easy to maintain.

### 6. Easy to Maintain and Update
Version pinning, documented upgrades, adapter smoke tests, and minimal complexity.

### 7. Built on Popular, Highly-Regarded, Open-Source Foundations
Builds on existing tools (OpenSpec, claude-flow) that are open-source, actively maintained, not overly complex, and opinionated about workflow structure.

### 8. Project Memory System
File-based memory (markdown files for decisions, lessons, patterns) with manual curation and limited automation. No secrets or sensitive data.
