# Forgetful MCP - Research Summary

**Repository:** https://github.com/ScottRBK/forgetful  
**Author:** ScottRBK  
**License:** MIT  
**Current Version:** v0.2.0 (as of Jan 15, 2026)  
**Language:** Python 3.12+  
**Discord:** https://discord.gg/ngaUjKWkFJ

---

## Overview

**Forgetful** is an open-source storage and retrieval system designed specifically for AI agents. It implements the Model Context Protocol (MCP) to provide persistent memory capabilities to MCP clients such as Claude Code, Claude Desktop, Cursor, Codex, Gemini CLI, and custom agents.

The core problem it solves: AI agents forget context between sessions. Forgetful provides a shared knowledge base that persists across different agents and sessions, enabling continuity in AI-assisted workflows.

### Key Differentiator

What sets Forgetful apart from other memory MCP servers is its **opinionated approach based on the Zettelkasten principle** - each memory must be atomic (one concept per note). This, combined with automatic semantic linking, creates an "Obsidian for AI Agents" experience where knowledge graphs are built automatically.

---

## Purpose & Problem Statement

From the author:
> "Having them respond to my tirades about the dangers of microservices by hallucinating that my own AI framework was Langchain for the 22nd time I think finally made me act."

The tool addresses:
1. **Agent amnesia** - LLMs forgetting context between sessions
2. **Cross-agent continuity** - Sharing knowledge between different AI tools (brainstorm in Claude Desktop, implement in Claude Code)
3. **Context window efficiency** - Reducing token usage through smart retrieval and a meta-tools pattern

---

## Capabilities & Features

### Core Features

| Feature | Description |
|---------|-------------|
| **MCP Server** | Full MCP protocol implementation via FastMCP framework |
| **Transport Modes** | STDIO (recommended for local) and HTTP (for Docker/remote) |
| **Storage Backends** | SQLite (zero-config default) or PostgreSQL (for scale) |
| **Vector Search** | Semantic search via FastEmbed embeddings (384-dimensional vectors) |
| **Cross-Encoder Reranking** | Improved recall and precision for memory retrieval |
| **Auto-Linking** | Automatically links semantically similar memories (configurable threshold) |
| **Token Budget Management** | Configurable budget (default 8K tokens) to prevent context overflow |

### Resource Types

Forgetful manages 6 categories of resources (42 tools total):

| Category | Tools | Description |
|----------|-------|-------------|
| **Memory** | 7 | Create, query, update, link, mark obsolete |
| **Project** | 5 | Organize knowledge by context/scope |
| **Entity** | 15 | Track people, orgs, devices; build knowledge graphs |
| **Code Artifact** | 5 | Store reusable code snippets |
| **Document** | 5 | Store long-form content (>400 words) |
| **User** | 2 | Profile and authentication |

### Meta-Tools Pattern

Only **3 tools** are exposed to the MCP client (preserving context window), while **42 tools** are accessible via `execute_forgetful_tool`. This saves approximately 25k tokens compared to exposing all tools directly.

### Authentication Support

- Opaque Bearer Token (RFC 7662)
- Authorization Code flow (RFC 6749)
- Dynamic Client Registration (RFC 7591)

### Embedding Providers

| Provider | Status |
|----------|--------|
| FastEmbed | Supported (default, local) |
| Google | Supported |
| Azure OpenAI | Supported |
| OpenAI | Planned |
| Ollama | Planned |
| OpenRouter | Planned |

### Client Integrations

Documented connectivity guides exist for:
- Claude Code
- Claude Desktop
- Cursor
- Codex
- Gemini CLI (with custom commands)
- Copilot CLI (with custom agents and skills)
- OpenCode (with custom commands and skills)

---

## Popularity & Project Health

### Metrics (as of Jan 2026)

| Metric | Value |
|--------|-------|
| GitHub Stars | 102 |
| Forks | 8 |
| Contributors | 3 |
| Releases | 17 |
| Commits | 162 |
| Open Issues | 1 |
| Open PRs | 0 |

### Activity Level

**Very Active** - The project has had multiple commits in January 2026 alone, with features like:
- Graph API pagination and sorting
- SSE events for real-time updates
- Activity tracking for memory operations
- Provenance tracking for memory creation/updates

---

## Custom Agents/Commands/Skills

Forgetful provides pre-built integrations for several environments:

### Copilot CLI
Located in `docs/copilot-cli/`:
- Custom agents
- Custom skills

### Gemini CLI
Located in `docs/gemini-cli/`:
- Custom commands

### OpenCode
Located in `docs/opencode/`:
- Custom commands
- Custom skills

---

## Alignment with Claptrap Project Goals

This section analyzes how Forgetful aligns with the goals defined in `GOALS.md`.

### Goals Forgetful Supports

| Goal | Alignment | Notes |
|------|-----------|-------|
| **1. Simple** | Partial | Zero-config SQLite default is simple. However, the system itself (embeddings, cross-encoders, auto-linking) adds complexity. Not minimal, but not unreasonable. |
| **2. Provider/Model Agnostic** | Strong | Works with Claude, Codex, Gemini, Cursor, Copilot. Multiple embedding providers supported. MCP is provider-neutral by design. |
| **3. IDE/CLI/Environment Agnostic** | Strong | Documented support for Claude Code CLI, Cursor IDE, VS Code (via Copilot), Gemini CLI, OpenCode. Common MCP interface works everywhere. |
| **4. Easy to Install and Use** | Strong | `uvx forgetful-ai` runs immediately with no config. Docker options for production. Installation takes under 5 minutes. |
| **5. Modular** | Strong | Clean separation: transport (STDIO/HTTP), storage (SQLite/PostgreSQL), embeddings (multiple providers), authentication (multiple flows). |
| **6. Easy to Maintain and Update** | Strong | PyPI package with versioning. Active development with clear release notes. 17 releases indicate stable release cadence. |
| **7. Built on Popular Open-Source Foundations** | Strong | Built on FastMCP, FastEmbed, pgvector, Alembic. All actively maintained open-source projects. |
| **8. Project Memory System** | Strong | This is literally what Forgetful does. File-based memories with manual curation possible. Markdown-style atomic notes. |

### Goals Forgetful May Not Fully Support

| Goal | Concern | Notes |
|------|---------|-------|
| **1. Simple** | Medium | While installation is simple, the underlying system (vector embeddings, cross-encoders, graph building) is conceptually complex. More moving parts than a pure file-based approach. |
| **8. No Secrets/Sensitive Data** | Potential Risk | Forgetful stores data in a database. Care must be taken not to store sensitive information in memories. The tool doesn't appear to have built-in secret detection. |

### Potential Integration Points

If integrated with Claptrap:

1. **Memory Skill Enhancement**: Forgetful could replace or augment the current file-based memory skill with richer semantic search and auto-linking.

2. **Cross-Session Continuity**: Agents working in Claptrap workflows could persist decisions, patterns, and lessons learned across sessions.

3. **Knowledge Graph for Agents**: The entity relationship system could track project components, team members, and architectural decisions.

4. **Custom Commands/Skills**: Forgetful's existing integrations (Copilot CLI, Gemini CLI, OpenCode) could serve as templates for Claptrap adapters.

### Recommendation

**Forgetful is a strong candidate for integration** with the Claptrap workflow, particularly for the Project Memory System goal. Key considerations:

- **Pro**: Aligns well with 7 of 8 goals
- **Pro**: Already supports multiple environments Claptrap targets
- **Pro**: Actively maintained with responsive maintainer
- **Con**: Adds infrastructure complexity (database, embeddings) vs. pure file-based approach
- **Con**: Relatively new project (102 stars) - less battle-tested than some alternatives

---

## Community Feedback

### Reddit

**r/mcp and r/VibeCodeDevs**

The author posted about Forgetful, describing the motivation and technical approach. Key themes:

- Addresses real developer pain points around agent amnesia
- Cross-platform compatibility praised
- Zettelkasten approach resonates with note-taking enthusiasts
- Context window efficiency (meta-tools pattern) is innovative

**Notable Quote:**
> "I knew that this would be a new paradigm in Agent Utilisation, I would implore anyone to go out and look at a memory tool."

### GitHub Discussions

The pinned discussion shows active, collaborative engagement:

- Maintainer is responsive to questions
- Community contributions accepted (e.g., Gemini CLI commands from CharlieBytesX)
- Documentation gaps being addressed through community feedback

**User Quote:**
> "Thanks!! Now it makes much more sense. I just added as commands to gemini cli and encode-repo works great!!"

### Other Platforms

| Platform | Status |
|----------|--------|
| Hacker News | Not submitted |
| DEV.to | No articles found |
| Medium | No articles found |
| YouTube | No dedicated videos |
| Twitter/X | Unable to access |
| Discord | Server exists, content unknown |

### Overall Sentiment

**Positive but limited in volume** due to project newness. Those who have used it report it solving real problems effectively. The maintainer is highly responsive.

---

## Roadmap & Future Features

### Formal Roadmap

From `docs/features_roadmap.md`:

#### Planned Features (Priority Order)

**1. Multimodal Resources**
- Audio support (planned)
- Image support (planned)
- Video support (planned)

**2. Additional Embedding Adapters**
- OpenAI (planned)
- Ollama (planned)
- OpenRouter (planned)

**3. Observability**
- OpenTelemetry forwarding (planned)

**4. API Routes**
- Additional REST endpoints (planned)

### Recent Development Direction (Jan 2026)

Based on recent commits, active work includes:

- **Event-driven architecture**: SSE streaming, activity tracking
- **Graph API enhancements**: Subgraph traversal, new node types, pagination
- **Provenance tracking**: Recording who/what created/updated memories
- **Integration documentation**: Expanding support for more CLI tools

### Release Cadence

- 17 releases in project lifetime
- Latest: v0.2.0 (Jan 15, 2026)
- Active commit frequency (multiple per week)

---

## Technical Architecture

### Storage Layer

```
┌─────────────────────────────────────┐
│           MCP Clients               │
│  (Claude, Cursor, Codex, etc.)     │
└─────────────┬───────────────────────┘
              │ MCP Protocol
              ▼
┌─────────────────────────────────────┐
│         Forgetful Server            │
│  ┌─────────────────────────────┐   │
│  │    FastMCP Framework        │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │    Embedding Layer          │   │
│  │  (FastEmbed/Google/Azure)   │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │    Cross-Encoder Reranker   │   │
│  └─────────────────────────────┘   │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│         Storage Backend             │
│   SQLite (local) or PostgreSQL      │
│        + pgvector extension         │
└─────────────────────────────────────┘
```

### Memory Workflow

1. **Create Memory**: Agent submits title, content, tags, context
2. **Generate Embedding**: Content converted to 384-dim vector
3. **Similarity Search**: Find top semantically-related memories (threshold 0.7)
4. **Auto-Link**: Create bidirectional links to top 3-5 matches
5. **Query**: Natural language queries return primary results + 1-hop linked memories
6. **Token Management**: Results prioritized by importance then recency, truncated to budget

---

## Installation Quick Reference

### Simplest (PyPI)
```bash
uvx forgetful-ai
```

### Docker (Production)
```bash
cd docker
cp .env.example .env
docker compose -f docker-compose.postgres.yml up -d
```

### MCP Client Configuration

**STDIO (local):**
```json
{
  "mcpServers": {
    "forgetful": {
      "type": "stdio",
      "command": "uvx",
      "args": ["forgetful-ai"]
    }
  }
}
```

**HTTP (remote/Docker):**
```json
{
  "mcpServers": {
    "forgetful": {
      "type": "http",
      "url": "http://localhost:8020/mcp"
    }
  }
}
```

---

## Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_TOKEN_BUDGET` | 8000 | Max tokens for query results |
| `EMBEDDING_MODEL` | BAAI/bge-small-en-v1.5 | Embedding model |
| `MEMORY_NUM_AUTO_LINK` | 3 | Auto-link count (0 to disable) |
| `SERVER_PORT` | 8020 | HTTP server port |
| `DATABASE` | SQLite | Storage backend |

---

## Comparable Tools

Other memory/knowledge MCP servers in the ecosystem:

- **mem0** - Memory layer for AI applications
- **basic-memory** - Simpler file-based MCP memory
- **MemoryMesh** - Knowledge graph focused
- Various project-specific memory implementations

Forgetful differentiates through:
1. Zettelkasten-inspired atomic memory design
2. Automatic knowledge graph construction
3. Meta-tools pattern for context efficiency
4. Multi-environment pre-built integrations

---

## Conclusion

Forgetful is a **well-designed, actively maintained** memory system for AI agents that aligns strongly with provider/environment agnostic development workflows. Its Zettelkasten approach and automatic knowledge graph building offer meaningful differentiation from simpler memory solutions.

**Best suited for:**
- Developers working across multiple AI agents/environments
- Projects requiring persistent context across sessions
- Teams wanting to build shared knowledge bases for AI assistants

**Considerations:**
- Adds database infrastructure (vs. pure file-based approaches)
- Relatively new project still building community
- Requires trust in the embedding/retrieval approach

---

*Research compiled: January 2026*
