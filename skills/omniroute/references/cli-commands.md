# OmniRoute CLI Commands

> The `omniroute` binary (server lifecycle, setup, diagnostics, providers) **and** how to wire external coding CLIs (Claude Code, Codex, Cline, …) to route through OmniRoute on port **20128**.

When you need this file: operating the local OmniRoute server from the shell, or pointing a third-party CLI/agent at OmniRoute as its OpenAI/Anthropic-compatible backend.

Related: **auth-and-api.md** (API-key issuance + endpoint detail), **config-and-env.md** (env vars in depth), **providers.md** (provider management), **debugging.md** (doctor/diagnostics + troubleshooting), **logs-costs-usage.md** (`omniroute cost`/`usage`/`logs`).

---

## Internal `omniroute` CLI — quick reference

Entry point `bin/omniroute.mjs`. Most reached-for commands (`docs/reference/CLI-TOOLS.md §10 Internal OmniRoute CLI (L570)`):

| Command | Purpose |
|---------|---------|
| `omniroute` (or `omniroute serve`) | Start the server (default port **20128**) |
| `omniroute setup` | Interactive setup wizard (password, first provider) |
| `omniroute doctor` | Check config, DB, ports, runtime, memory, liveness |
| `omniroute status` | Comprehensive runtime status |
| `omniroute health` | Detailed health (breakers, cache, memory) |
| `omniroute providers list` | Configured provider connections |
| `omniroute providers test-all` | Test every active connection |
| `omniroute providers available` | Browse the OmniRoute provider catalog |
| `omniroute logs` | Stream request logs (`--follow`, `--search`, `--json`) |
| `omniroute reset-password` | Reset the admin password |
| `omniroute backup` / `restore` | Snapshot / restore config + DB |
| `omniroute models [provider]` | List models (`--json`, `--search`) |
| `omniroute keys add\|list\|remove` | Manage API keys |
| `omniroute tunnel list\|create\|stop` | Cloudflare / Tailscale / ngrok tunnels |
| `omniroute --version` / `--help` | Version / full command list |

### Setup & Initialization

```bash
omniroute setup                       # Interactive wizard
omniroute setup --non-interactive     # CI mode (reads env + flags)
omniroute setup --password '<value>'  # Set admin password directly
omniroute setup --add-provider --provider openai \
  --api-key '<value>' --test-provider # Add + test a provider in one shot
```

Non-interactive env vars: `OMNIROUTE_API_KEY` (provider key, bound to `--api-key`), `DATA_DIR` (override data dir). Everything else is a flag: `--password`, `--provider`, `--provider-name`, `--provider-base-url`, `--default-model` (`§ Setup & Initialization (L587)`).

### Diagnostics (doctor)

```bash
omniroute doctor                      # Full check
omniroute doctor --json               # Machine-readable
omniroute doctor --no-liveness        # Skip HTTP health probe
omniroute doctor --host 0.0.0.0       # Override liveness host
omniroute doctor --liveness-url <url> # Full health-endpoint override
```

Checks run: `Config`, `Database`, `Storage/encryption`, `Port availability`, `Node runtime`, `Native binary` (better-sqlite3), `Memory`, `Server liveness`. **Exits non-zero if any check fails** (`§ Diagnostics (L610)`). Deeper diagnostics workflow → **debugging.md**.

### Provider Management

```bash
omniroute providers available                  # Catalog
omniroute providers available --search openai  # Filter by id/name/alias/category
omniroute providers available --category api-key   # api-key, oauth, free, …
omniroute providers list                       # Configured connections
omniroute providers test <id|name>             # Test one connection
omniroute providers test-all                   # Test every active connection
omniroute providers validate                   # Local structural validation
```

`providers available` reads the OmniRoute catalog; `list/test/test-all/validate` read local SQLite directly and **do not need the server running** (`§ Provider Management (L624)`). Full provider lifecycle → **providers.md**.

### Recovery & Reset

```bash
omniroute reset-password                      # Reset admin password (legacy alias works)
omniroute reset-encrypted-columns             # Warn + dry-run for encrypted-credential reset
omniroute reset-encrypted-columns --force     # Actually null out encrypted credentials in SQLite
```

(`§ Recovery & Reset (L643)`)

### Other subcommands

Assume a running server unless noted (`§ Other subcommands (L651)`):

```bash
omniroute status                      # Runtime status
omniroute logs                        # Stream logs (--json, --search, --follow)
omniroute config show                 # Display current configuration
omniroute provider list               # Alias of `providers list`
omniroute provider add                # Register OmniRoute as a provider on a tool
omniroute keys add | list | remove    # API keys
omniroute models [provider]           # List models (--json, --search)
omniroute combo list|switch|create|delete   # Routing combos
omniroute backup | restore            # Snapshot / restore config + DB
omniroute health                      # Breakers, cache, memory
omniroute quota                       # Provider quota usage
omniroute cache | cache clear         # Cache status / clear semantic+signature caches
omniroute mcp status | restart        # MCP server
omniroute a2a status | card           # A2A server / agent card
omniroute tunnel list|create|stop     # Tunnels (cloudflare/tailscale/ngrok)
omniroute env show | get <k> | set <k> <v>   # Inspect/set env (temporary)
omniroute test                        # Provider connectivity smoke test
omniroute update                      # Check for updates
omniroute completion                  # Shell completion
```

> `omniroute cost` / `omniroute usage` reporting → **logs-costs-usage.md**.

### Common flags

| Flag | Description |
|------|-------------|
| `--no-open` | Don't auto-open the browser on start |
| `--port <n>` | Override API port (default **20128**) |
| `--mcp` | Run as MCP server over stdio (for IDEs) |
| `--non-interactive` | CI mode (no prompts; reads env/flags) |
| `--json` | Machine-readable output (doctor, providers, …) |
| `--help`, `-h` | Command-specific help |
| `--version`, `-v` | Print installed version |

### CLI binary tuning env vars

From `docs/reference/ENVIRONMENT.md §9 CLI Binary (omniroute) helpers`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `OMNIROUTE_LANG` | system | Force CLI output language (BCP-47, e.g. `en`, `pt-BR`) |
| `OMNIROUTE_SHOW_LOG` | unset | `1` forwards server stdout/stderr in supervised mode (= `--log`) |
| `OMNIROUTE_CLI_TOKEN` | unset | Machine-auth token sent as `x-omniroute-cli-token` |
| `OMNIROUTE_HTTP_TIMEOUT_MS` | `30000` | Per-attempt CLI→server HTTP timeout |
| `OMNIROUTE_VERBOSE` | `0` | `1` prints retry/backoff diagnostics to stderr |
| `OMNIROUTE_PLUGIN_PATH` | `~/.omniroute/plugins/` | CLI plugin (`omniroute-cmd-*`) discovery dir |
| `OMNIROUTE_PLUGINS_ALLOW_EXEC` | `0` | `1` lets plugins request `exec` permission |

Sidecar-discovery vars (`CLI_MODE`, `CLI_EXTRA_PATHS`, `CLI_CONFIG_HOME`, `CLI_ALLOW_CONFIG_WRITES`, `CLI_*_BIN`, `HERMES_HOME`) → **config-and-env.md**.

---

## API endpoints the CLI exposes/uses

Universal base: `http://localhost:20128/v1` (`§ Available API Endpoints (L699)`):

| Endpoint | Use for |
|----------|---------|
| `/v1/chat/completions` | All modern tools (standard chat) |
| `/v1/responses` | Codex, agentic workflows (OpenAI Responses) |
| `/v1/completions` | Legacy text completions (`prompt:`) |
| `/v1/embeddings` | RAG, search |
| `/v1/images/generations` | Image generation |
| `/v1/audio/speech` | Text-to-speech |
| `/v1/audio/transcriptions` | Speech-to-text |

Tokenized VS Code fallback (token embedded in URL, no custom header needed):
`http://localhost:20128/api/v1/vscode/<sk-token>/chat/completions` (and `/models`, `/responses`). Endpoint/auth detail → **auth-and-api.md**.

---

## Wiring external CLI tools to OmniRoute

Consumption flow: **Client → CLI → OmniRoute (`:20128/v1`) → Provider** (`§ How It Works (L23)`). Benefits: one API key for all tools, unified cost tracking, model switching without per-tool reconfig, works local or remote.

### Step 1 — Get an OmniRoute API key

1. Open `/dashboard/api-manager` → **Create API Key**
2. Name it (e.g. `cli-tools`), select all permissions
3. Copy the key (`sk-xxx…xxxx`) — needed by every CLI below

(`§ Step 1 (L261)`. Issuance internals → **auth-and-api.md**.)

### Step 2 — Install (npm tools need Node ≥20.20.2 / 22.22.2 / 24.x)

```bash
npm i -g @anthropic-ai/claude-code   # Claude Code
npm i -g @openai/codex               # OpenAI Codex
npm i -g opencode-ai                 # OpenCode
npm i -g cline                       # Cline
npm i -g kilocode                    # KiloCode
npm i -g @qwen-code/qwen-code        # Qwen Code
pip install aider-chat               # Aider
cargo install smelt                  # Smelt (Rust)
```

(`§ Step 2 (L271)`)

### Auto-configure with `setup-*`

Each `setup-*` reads the **live** model catalog from a running OmniRoute and writes that tool's own config (`§ Auto-configure (L48)`):

| Command | Command | Command |
|---------|---------|---------|
| `omniroute setup-codex` | `omniroute setup-claude` | `omniroute setup-opencode` |
| `omniroute setup-cline` | `omniroute setup-kilo` | `omniroute setup-continue` |
| `omniroute setup-cursor` | `omniroute setup-roo` | `omniroute setup-crush` |
| `omniroute setup-goose` | `omniroute setup-qwen` | `omniroute setup-aider` |
| `omniroute setup-gemini` | | |

Common flags: `--remote <url> --api-key <key>` (local tool → remote OmniRoute), `--dry-run` (preview), `--port`. Tools lacking model auto-discovery (Cline, Kilo, Roo, Goose, Qwen, Aider, Gemini) also take `--model <id>` and `--yes`. Launchers `omniroute launch` (Claude Code) and `omniroute launch-codex` (Codex) spawn the CLI with env injected and **write no config**. Master flag/behaviour table lives in `docs/guides/CLI-INTEGRATIONS.md`.

### Step 4 — Global env vars

```bash
export OPENAI_BASE_URL="http://localhost:20128/v1"
export OPENAI_API_KEY="sk-…"
export ANTHROPIC_BASE_URL="http://localhost:20128"   # no /v1 for Anthropic root
export ANTHROPIC_AUTH_TOKEN="sk-…"
export GEMINI_BASE_URL="http://localhost:20128/v1"
export GEMINI_API_KEY="sk-…"
```

Remote server: replace `localhost:20128` with `http://<server-ip>:20128` (`§ Step 4 Set Global Env Vars (L319)`).

### Per-tool config (manual)

`§ Step 4 Configure Each Tool (L336)`. Or use the dashboard card → **Apply Config**.

```bash
# Claude Code → ~/.claude/settings.json (Anthropic root, NO /v1)
{"env":{"ANTHROPIC_BASE_URL":"http://localhost:20128","ANTHROPIC_AUTH_TOKEN":"sk-…"}}

# OpenAI Codex → ~/.codex/config.yaml
model: auto
apiKey: sk-…
apiBaseUrl: http://localhost:20128/v1

# Cline (CLI) → ~/.cline/data/globalState.json
{"apiProvider":"openai","openAiBaseUrl":"http://localhost:20128/v1","openAiApiKey":"sk-…"}

# KiloCode (CLI)
kilocode --api-base http://localhost:20128/v1 --api-key sk-…

# Qwen Code → ~/.qwen/.env
OPENAI_API_KEY="sk-…"
OPENAI_BASE_URL="http://localhost:20128/v1"
OPENAI_MODEL="auto"
```

- **OpenCode**: `~/.config/opencode/opencode.json` → provider `omniroute` using npm `@ai-sdk/openai-compatible`, `baseURL: …/v1`. Thinking variants: `opencode run "…" --model omniroute/<model> --variant high`.
- **Continue**: `~/.continue/config.yaml` → `provider: openai`, `apiBase: …/v1`; restart VS Code.
- **VS Code Insiders**: `chatLanguageModels.json` with tokenized `url`/`modelsUrl` (`…/api/v1/vscode/<token>/…`) when custom headers aren't supported.
- **Kiro CLI** (Amazon): uses its own AWS SSO auth — OmniRoute not used as its backend; Kiro IDE uses the MITM endpoint.

---

## Catalogs: CLI Code's vs CLI Agents vs ACP

Three dashboard pages, one source of truth (`src/shared/constants/cliTools.ts`):

| Page | Route | Concept | Count |
|------|-------|---------|-------|
| **CLI Code's** | `/dashboard/cli-code` | Coding CLIs you point at OmniRoute | **19** |
| **CLI Agents** | `/dashboard/cli-agents` | Autonomous agents, same flow, broader scope | **6** |
| **ACP Agents** | `/dashboard/acp-agents` | CLIs OmniRoute **spawns** as backend via stdio/ACP (reverse flow) | registry |

- **CLI Code's (19)** (`§ CLI Code's Catalog (L94)`): claude, codex, cline, kilo, roo, continue, qwen, aider, forge, jcode, deepseek-tui, opencode, droid, copilot, gemini-cli, cursor-cli, smelt, pi, custom. `baseUrlSupport: partial` (droid, gemini-cli, cursor-cli) shows "⚠ Base URL parcial".
- **CLI Agents (6)** (`§ CLI Agents Catalog (L124)`): hermes-agent, openclaw, goose, interpreter, warp, agent-deck.
- **ACP Agents** (`§ ACP Agents (L139)`): registry in `src/lib/acp/registry.ts` (≠ `CLI_TOOLS`). Spawnable: codex, claude, goose, gemini-cli, openclaw, aider, opencode, cline, qwen-code, forge, interpreter, cursor-cli, warp.
- **MITM backlog** (`§ MITM Backlog (L147)`): no native custom base URL, hidden from dashboard — windsurf, amp, amazon-q/kiro-cli, cowork.

Batch detection: `GET /api/cli-tools/all-statuses` (`§ Batch Detection API (L162)`). Legacy routes 308-redirect: `/dashboard/cli-tools` → `/dashboard/cli-code`, `/dashboard/agents` → `/dashboard/acp-agents`.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | OmniRoute not running | `omniroute serve` |
| `401 Unauthorized` | Wrong API key | Check `/dashboard/api-manager` |
| `No combo configured` | No active routing combo | Set up in `/dashboard/combos` |
| CLI "not installed" | Binary not in PATH | `which <command>` |
| Dashboard "not detected" after install | Stale cache | Click "⟳ Refresh detection" |
| Old `/dashboard/cli-tools` link | Pre-v3.8.6 bookmark | Auto-redirects (308) |

(`§ Troubleshooting (L726)`.) Deeper diagnostics → **debugging.md**.
