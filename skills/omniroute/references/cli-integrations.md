# OmniRoute CLI Integrations

> How to point external coding CLIs and agents (Claude Code, Codex, Cline, OpenCode, Aider, Cursor CLI, Gemini CLI, …) at OmniRoute as their OpenAI/Anthropic-compatible backend.

**When you need this file:** wiring third-party CLI/agent tools to OmniRoute, using `omniroute setup-*`, choosing the right base URL/env vars, reading the CLI Code/Agents dashboard catalogs, or troubleshooting CLI detection/config.

Related: **cli-commands.md** (internal `omniroute` server CLI), **auth-and-api.md** (API-key issuance + endpoint detail), **config-and-env.md** (env vars), **providers.md** (provider auth types), **debugging.md** (connection failures).

---

## Consumption flow

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

## Catalogs: CLI Code vs CLI Agents vs ACP

Three dashboard pages, one source of truth (`src/shared/constants/cliTools.ts`):

| Page | Route | Concept | Count |
|------|-------|---------|-------|
| **CLI Code** | `/dashboard/cli-code` | Coding CLIs you point at OmniRoute | ~20+ (verify live) |
| **CLI Agents** | `/dashboard/cli-agents` | Autonomous agents, same flow, broader scope | ~7 (verify live) |
| **ACP Agents** | `/dashboard/acp-agents` | CLIs OmniRoute **spawns** as backend via stdio/ACP (reverse flow) | registry |

- **CLI Code (~20+)** (`§ CLI Code Catalog (L94)`): includes Claude Code, Codex, Cline, Kilo, Roo, Continue, Qwen, Aider, Forge, OpenCode, Copilot, Gemini CLI, Cursor CLI, Smelt, and others. `baseUrlSupport: partial` flags tools that need caveats.
- **CLI Agents (~7)** (`§ CLI Agents Catalog (L124)`): includes hermes-agent, openclaw, goose, interpreter, warp, agent-deck, and other agent-style clients.
- **ACP Agents** (`§ ACP Agents (L139)`): registry in `src/lib/acp/registry.ts` (≠ `CLI_TOOLS`). Spawnable: codex, claude, goose, gemini-cli, openclaw, aider, opencode, cline, qwen-code, forge, interpreter, cursor-cli, warp.
- **MITM backlog** (`§ MITM Backlog (L147)`): no native custom base URL, hidden from dashboard — windsurf, amp, amazon-q/kiro-cli, cowork.

Exact counts drift by release. Live check: `GET /api/cli-tools/all-statuses`; source: `src/shared/constants/cliTools.ts`. Batch detection: `GET /api/cli-tools/all-statuses` (`§ Batch Detection API (L162)`). Legacy routes 308-redirect: `/dashboard/cli-tools` → `/dashboard/cli-code`, `/dashboard/agents` → `/dashboard/acp-agents`.

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
