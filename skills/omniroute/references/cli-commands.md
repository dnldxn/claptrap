# OmniRoute CLI Commands

> The internal `omniroute` binary for server lifecycle, setup, diagnostics, provider management, keys, models, combos, tunnels, logs, cost, and usage.

**When you need this file:** operating the local OmniRoute server from the shell, diagnosing it with `omniroute doctor`, managing providers/API keys/models/combos/tunnels, or checking logs/cost/usage from the CLI.

Related: **cli-integrations.md** (wire external coding CLIs to OmniRoute), **auth-and-api.md** (API-key issuance + endpoint detail), **config-and-env.md** (env vars), **providers.md** (provider lifecycle), **debugging.md** (diagnostics), **logs-costs-usage.md** (`omniroute cost`/`usage`/`logs`).

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
| `--json` | Machine-readable output where supported (for example logs/models; not `doctor`) |
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
