# OpenSpec Research

> Research date: January 2026  
> Source: [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)

## Summary

**OpenSpec** is an open-source tool for **Spec-Driven Development (SDD)** designed to align humans and AI coding assistants by defining explicit specifications *before* code is written. It provides a lightweight specification workflow that locks intent before implementation, reducing ambiguity and improving predictability when working with AI assistants.

### Purpose

OpenSpec solves the problem of AI/human misalignment around vague prompts or undocumented intent. It enforces a structured workflow around proposals, spec deltas, tasks, and review loops—ensuring everyone agrees on what's being built before any code is written.

Works for both:
- **Greenfield projects**: New features from scratch
- **Brownfield projects**: Modifying existing systems where multiple specs/features may be affected

### Core Capabilities

| Capability | Description |
|------------|-------------|
| **CLI Tool** | `openspec init`, `list`, `show`, `validate`, `archive`, `view` |
| **Two-Folder Model** | `openspec/specs/` (current truth) + `openspec/changes/` (proposed changes) |
| **Change Artifacts** | Each change includes `proposal.md`, `tasks.md`, optional `design.md`, and spec deltas |
| **Delta Format** | Structured diffs: `## ADDED Requirements`, `## MODIFIED`, `## REMOVED` |
| **Scenario Syntax** | `#### Scenario:` with `WHEN`/`THEN` blocks for acceptance criteria |
| **Multi-Tool Integration** | Native slash commands for Claude Code, Cursor, CodeBuddy, Codex, OpenCode, RooCode, Gemini CLI, and more |
| **AGENTS.md Fallback** | For tools without native support, provides instructions AI assistants can follow |
| **OPSX Experimental** | Fluid, hackable workflow with customizable artifacts, schemas, and no phase gates |

### Popularity & Adoption

- **GitHub Stars**: ~17,700+ stars
- **Forks**: ~1,200+
- **Latest Version**: v0.20.0 (January 2026)
- **Release Cadence**: Frequent updates (multiple releases per month)
- **npm Downloads**: Thousands weekly
- **License**: MIT (permissive, commercial-friendly)
- **Community**: Active Discord, open to contributions

---

## Alignment with Development Workflow Goals

Based on the goals in `GOALS.md`, here's how OpenSpec aligns:

### ✅ Goals OpenSpec Supports Well

| Goal | How OpenSpec Supports It |
|------|--------------------------|
| **Provider/model agnostic** | Strong support. OpenSpec integrates with Claude, Codex, Gemini, and others via native commands or AGENTS.md fallback. Works across providers. |
| **IDE/CLI/Environment agnostic** | Excellent. Supports Cursor, VS Code (via Copilot), OpenCode CLI, and others. The AGENTS.md pattern works anywhere. |
| **Easy to install and use** | Yes. Single npm install, `openspec init` to start. No API keys required. Minimal setup friction. |
| **Based on popular, actively developed tools** | OpenSpec itself is popular (17.7k stars), actively maintained, and explicitly mentioned as a target platform in GOALS.md. |
| **Not overly complex** | Intentionally lightweight. Core workflow is simple: propose → implement → archive. Complexity is optional (OPSX). |
| **Opinionated** | Yes. Enforces spec format (SHALL/MUST wording), scenario structure, task organization. Provides guardrails. |
| **Free and open source** | MIT license. No cost, no vendor lock-in. |
| **Previously completed changes/tasks and their results** | Strong support. Archived changes in `openspec/changes/archive/` create a historical record of all changes, tasks, and outcomes over time. |

### ⚠️ Goals with Partial Support

| Goal | Assessment |
|------|------------|
| **Easy to extend and customize** | Partially supported. OPSX experimental workflow allows custom artifacts/schemas. However, extending beyond the built-in workflow requires understanding the schema system. |
| **Easy to maintain and update** | Good. Running `openspec update` refreshes agent instructions. But staying current with releases requires manual attention. |
| **Project structure and organization memory** | Partial. Specs document behavior, not codebase structure. You'd need to maintain structure docs separately. |
| **Goals tracking** | Partial. Specs capture requirements, but high-level project goals need separate documentation. |
| **What works/doesn't work (lessons learned)** | Not built-in. OpenSpec tracks *what* changed, not retrospective learnings. You'd add this manually to proposal or design docs. |

### ❌ Goals OpenSpec Does NOT Address

| Goal | Gap |
|------|-----|
| **Specialized sub-agents** | OpenSpec doesn't provide sub-agent orchestration. It's a specification workflow, not an agent framework. You'd need to combine with something like claude-flow for multi-agent patterns. |
| **Fresh context window initialization** | No built-in context window management or sub-agent spawning. This is outside OpenSpec's scope. |
| **Automatic memory that learns over time** | No automatic learning/adaptation. OpenSpec is deterministic—it stores what you explicitly write, but doesn't infer or learn patterns. |

---

## Future Features & Direction

### Recently Added (v0.18.0 – v0.20.0)

- **OPSX Experimental Workflow**: Fluid, hackable alternative to standard workflow
  - `/opsx:new`, `/opsx:continue`, `/opsx:ff` (fast-forward), `/opsx:apply`, `/opsx:archive`
  - Per-change schema metadata via `.openspec.yaml`
  - Customizable artifact templates
- **Verify Command**: New in v0.20.0 for validation
- **Shell Completions**: Bash, Fish, PowerShell support
- **New Tool Integrations**: Continue, Gemini CLI, RooCode, Auggie, Crush, Cline
- **Cross-Platform Fixes**: Windows compatibility, path normalization

### Roadmap / Planned Features

Based on documentation and the OpenSpec website:

| Feature | Status |
|---------|--------|
| **Spec generation for existing codebases** | Exploring—would auto-generate specs from code |
| **Team/large-scale features** | In progress—multi-repo, microservices support |
| **Deeper schema customization** | Active via OPSX |
| **Agent skills system** | Experimental—schema-aware agent behaviors |

### Inferred from Recent Activity

- Continued cross-platform hardening (glob patterns, paths)
- UX improvements (list sorting, timestamps, better error messages)
- Expanding tool integrations as new AI assistants emerge

### Not Yet Addressed

- No public long-term roadmap document
- No built-in test generation from specs
- No automatic enforcement that code matches specs (beyond review)

---

## Other Interesting Notes

### Technical Requirements
- Node.js ≥ 20.19.0
- No external API keys required
- Works offline/locally

### Design Philosophy
- Uses RFC-style requirement language (SHALL/MUST)
- Every requirement needs at least one scenario with WHEN/THEN
- Strict validation enforces format consistency
- "Two-folder model" keeps current truth separate from proposed changes

### Comparison to Alternatives

| Tool | Difference |
|------|------------|
| **spec-kit** | OpenSpec's two-folder model scales better for brownfield/evolving features |
| **Kiro.dev** | OpenSpec groups all change artifacts together; Kiro spreads across spec folders |
| **No specs** | Without specs, AI generates from vague prompts with unpredictable results |

### Telemetry
- Collects anonymous usage stats (command names, version only)
- No content, paths, or PII
- Opt-out: `OPENSPEC_TELEMETRY=0` or `DO_NOT_TRACK=1`
- Auto-disabled in CI

### Integration Pattern
For tools without native slash commands, OpenSpec generates an `AGENTS.md` file that teaches AI assistants the workflow. This "AGENTS.md convention" is becoming a de facto standard for cross-tool AI instructions.

---

## Recommendations for This Project

OpenSpec is a strong fit for the **spec-driven planning** aspects of the workflow goals. Specifically:

1. **Use OpenSpec for**: Change proposals, task tracking, spec documentation, archived change history
2. **Combine with other tools for**: Sub-agent orchestration (claude-flow), automatic memory/learning (needs custom solution), project structure documentation

The project already uses OpenSpec (`openspec/` directory exists). To maximize value:
- Leverage archived changes as project memory of completed work
- Use OPSX experimental features for more flexible workflows
- Maintain separate docs for lessons learned and project structure that OpenSpec doesn't cover

---

## References

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec Website](https://openspec.dev/)
- [OpenSpec Releases](https://github.com/Fission-AI/OpenSpec/releases)
- [npm Package](https://www.npmjs.com/package/@fission-ai/openspec)
