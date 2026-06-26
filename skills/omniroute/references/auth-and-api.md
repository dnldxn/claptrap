# OmniRoute — Auth & HTTP API Reference

> OpenAI-compatible gateway API (Bearer `OMNIROUTE_API_KEY`, default port **20128**) plus a large dashboard/management REST surface under `/api/*`.

**When you need this file:** authenticating to OmniRoute, picking the right `/v1/*` or `/api/*` endpoint, setting custom headers (compression, cache, session), or making a chat/embeddings/image/audio request via curl.

All endpoint payload specs live in `docs/reference/API_REFERENCE.md` (v3.8.2, 1362 lines) — sections are cited inline as `§Name (Lxx)`. For model-id routing (`auto/…`, `cc/…`, combos) see **routing-and-combos.md**; provider auth types see **providers.md**; usage/cost detail see **logs-costs-usage.md**; env vars see **config-and-env.md**; CLI see **cli-commands.md**.

## Authentication

Three auth surfaces:

1. **Data plane (`/v1/*`)** — `Authorization: Bearer <OMNIROUTE_API_KEY>`. Only enforced when `REQUIRE_API_KEY=true`; otherwise any key (or none) works locally. Keys are issued/managed in the dashboard via `/api/keys*`. Per-key scoping (Files, Batches, budgets) uses `getApiKeyRequestScope`. `§Authentication (L1356)`.
2. **Management plane (`/api/*`, dashboard)** — dashboard `auth_token` cookie (login via `/api/auth/login`, password hash w/ `INITIAL_PASSWORD` fallback) **or** a management-scoped API key. `requireLogin` toggles via `/api/settings/require-login`. As of **v3.8.0** the agent-tasks and cooldown routes require management auth (else `401`).
3. **CLI machine token (localhost only)** — the CLI injects header `x-omniroute-cli-token` = `HMAC-SHA256(machine-id, salt)` (64-char hex; salt default `omniroute-cli-auth-v1`, rotate via `OMNIROUTE_CLI_SALT`). Accepted **only from loopback** (`127.0.0.1`/`::1`), timing-safe compared, never logged. Gives zero-config localhost CLI access without a key. Disable with `OMNIROUTE_DISABLE_CLI_TOKEN=true`. An explicit `Authorization: Bearer` (from `--api-key`/`OMNIROUTE_API_KEY`) always takes precedence. `/api/shutdown` + `/api/settings/database` always require JWT. See `docs/security/CLI_TOKEN_AUTH.md`, `docs/security/CLI_TOKEN.md`.

**Headerless / URL-embedded keys** (when a client can't send headers): query string `?token=` / `?apiKey=` / `?api_key=` / `?key=`, or the tokenized `/api/v1/vscode/{token}/…` aliases (see below). URL tokens leak into proxy logs/history — prefer the Bearer header. `§Compatibility (L210)`, `§Tokenized Aliases (L663)`.

### Auth example (chat completion)

```bash
curl -X POST http://localhost:20128/v1/chat/completions \
  -H "Authorization: Bearer $OMNIROUTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "cc/claude-opus-4-6",
    "messages": [{"role": "user", "content": "Write a function to reverse a string"}],
    "stream": true
  }'
```

Base URL = `http://localhost:20128` (use `https://` in production). OpenAI SDK base: `http://localhost:20128/v1`.

## Custom request/response headers

`§Custom Headers (L61)`. Most useful on `/v1/chat/completions` and other data-plane routes:

| Header | Dir | Purpose |
|--------|-----|---------|
| `x-omniroute-compression` | req | Per-request compression override (highest precedence). See below. |
| `X-OmniRoute-No-Cache` | req | `true` bypasses semantic cache |
| `x-omniroute-no-memory` | req | `true` skips memory + skills injection (saves token/cost overhead) |
| `x-omniroute-disabled-guardrails` | req | Per-call opt-out of guardrails (PII / prompt-injection / vision) |
| `X-OmniRoute-Progress` | req | `true` emits progress events |
| `X-Session-Id` / `x_session_id` | req | Sticky session affinity (nginx: `underscores_in_headers on;`) |
| `Idempotency-Key` / `X-Request-Id` | req | Dedup key, 5s window |
| `X-OmniRoute-Cache` | resp | `HIT`/`MISS` (non-streaming) |
| `X-OmniRoute-Cost-Saved` | resp | USD saved on a cache HIT |
| `X-OmniRoute-Version` | resp | Build version (always present) |

**Cost telemetry (response):** non-streaming success carries `X-OmniRoute-Response-Cost` (USD, 10 decimals), `-Tokens-In/-Out`, `-Model`, `-Provider`, `-Latency-Ms`, `-Cache-Hit`, `-Fallback-Attempts`, `-Request-Id`. Emitted by chat, `/v1/responses`, `/v1/messages`, and media endpoints. On a cache HIT the incremental cost is `0` and the avoided cost is in `-Cost-Saved`. Detail → **logs-costs-usage.md**.

### `x-omniroute-compression` (L86)

Per-request compression plan override — beats routing-combo override, active profile, auto-trigger, and panel Default. Values: `off` | `default` (panel default profile) | `engine:<id>` (e.g. `engine:rtk`) | `<combo>` (by name, case-insensitive, then id). Unknown values are ignored (never rejected). The master compression switch is a hard gate. Applied plan echoed back as `X-OmniRoute-Compression: <mode>; source=<request-header|routing-override|active-profile|auto-trigger|default|off>`.

## Data-plane endpoint catalog (`/v1/*`)

Auth = Bearer API key on all. `§` cites payload specs.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/chat/completions` | OpenAI chat (primary) — `§L45` |
| POST | `/v1/messages` | Anthropic format |
| POST | `/v1/messages/count_tokens` | Anthropic token count |
| POST | `/v1/responses` | OpenAI Responses API |
| POST | `/v1/embeddings` · GET to list | Embeddings (Nebius/OpenAI/Mistral/Together/Fireworks/NVIDIA/OpenRouter/GitHub) — `§L114` |
| POST | `/v1/images/generations` · GET to list | Image gen (OpenAI/xAI/Together-FLUX/Fireworks/Nebius/Hyperbolic/NanoBanana/OpenRouter/SD-WebUI/ComfyUI) — `§L136` |
| POST | `/v1/images/edits` | Image edit/inpaint (multipart `image`,`prompt`,`mask`) |
| POST | `/v1/videos/generations` | Video gen (provider-prefixed id, e.g. `runway/gen-3`) |
| POST | `/v1/music/generations` | Music gen (e.g. `suno/v3.5`) |
| POST | `/v1/audio/speech` | TTS → audio body (e.g. `openai/tts-1`) |
| POST | `/v1/audio/transcriptions` | STT, multipart (`deepgram/nova-3`, `assemblyai/best`) — `§L613` |
| POST | `/v1/rerank` | Cohere/Voyage-style rerank |
| POST | `/v1/moderations` | OpenAI moderations (always cost `0`) |
| GET | `/v1/models` | All chat/embed/image models + combos (OpenAI fmt) — `§L159` |
| GET | `/v1beta/models` · POST `/v1beta/models/{...path}` | Gemini list / `generateContent` — `§L569` |
| POST | `/v1/api/chat` · GET `/api/tags` | Ollama chat / tags — `§L649` |
| GET/POST | `/v1/search` · GET `/v1/search/analytics` | Web search (Tavily/Brave/Exa/Serper) — `§L274` |
| * | `/v1/files`, `/v1/files/[id]`, `/v1/files/[id]/content` | Files API (upload 512 MiB / list / get / delete / stream), per-key scoped — `§L242` |
| * | `/v1/batches`, `/v1/batches/[id]`, `/v1/batches/[id]/cancel` | Batches API (create/list/get/delete/cancel) — `§L258` |
| GET/POST | `/v1/quotas/check` · `/v1/issues/report` | Pre-check quota / report key-issuance failure to GitHub — `§L361` |
| * | `/v1/registered-keys[/id][/revoke]` | Auto-managed key issue/list/revoke; returns raw key once, `429` on quota — `§L817` |
| GET/DELETE | `/api/cache/stats` | Semantic cache stats / clear-all — `§L372` |

**Compatibility table** (full): `§Compatibility Endpoints (L180)`. Bodies are Zod-validated (`v1RerankSchema`, `v1ModerationSchema`, `v1AudioSpeechSchema`…); schema failure → 4xx.

### Dedicated provider routes (L230)

`POST /v1/providers/{provider}/chat/completions` · `/embeddings` · `/images/generations`. Provider prefix auto-added if missing; mismatched model → `400`.

### No-thinking model variants (L168)

`/v1/models` advertises a no-thinking alias for thinking-capable Claude models:
`claude-3-omniroute-no-thinking/<provider>/<model>`. Selecting it resolves to the real model with reasoning suppressed (`thinking:{type:"disabled"}` on `/v1/messages`; `reasoning`/`reasoning_effort` dropped on chat). Only listed for Claude models that support **and** honor `disabled`. Force per-model via `ModelSpec.noThinkingAlias`.

### WebSocket streaming (L288)

- `GET /v1/ws?handshake=1` — validate WS upgrade; Bearer key during handshake. Real frames handled by the bundled WS server (`server-ws.mjs`).
- **Responses API over WS — codex only (L298):** `ws://localhost:20128/v1/responses?api_key=<KEY>` (also `/responses`, `/api/v1/responses`). First frame must be `{"type":"response.create","model":"gpt-5.5","input":[…]}`. Tunnels to `wss://chatgpt.com/backend-api/codex/responses`. **Use the bare ChatGPT model id** (e.g. `gpt-5.5`, NOT `codex/gpt-5.5`). Non-codex models → `codex_ws_provider_required`. Quota-share routing: `model:"qtSd/<group>/codex/<model>"`. Codex CLI config: `~/.codex/config.toml` with `base_url="http://localhost:20128/v1"`, `wire_api="responses"`, `supports_websockets=true`, `env_key="OMNIROUTE_API_KEY"`.

### Tokenized VS Code / headerless aliases (L663)

Embed the key in the URL when headers aren't possible (reuses the same handlers):
`GET /api/v1/vscode/{token}/` · `/models`, `POST …/chat/completions` · `…/responses`, `POST …/api/chat` · `GET …/api/tags`. Treat as compatibility only (tokens leak into logs).

## Dashboard / Management API (`/api/*`)

`§Dashboard & Management (L401)`. Auth = management session cookie or management-scoped key (`requireManagementAuth`) unless noted. Groups:

| Group | Key endpoints | §L |
|-------|---------------|-----|
| **Auth** | `/api/auth/login`, `/api/auth/logout`, `/api/settings/require-login` | L403 |
| **Provider mgmt** | `/api/providers[/id][/test][/models]`, `/api/providers/validate`, `/api/provider-nodes*`, `/api/provider-models` | L411 |
| **OAuth flows** | `/api/oauth/[provider]/[action]` | L423 |
| **Routing & config** | `/api/models/alias`, `/api/models/catalog`, `/api/combos*`, `/api/keys*`, `/api/pricing`, `/api/model-combo-mappings[/id]` | L429 / L784 |
| **Usage & analytics** | `/api/usage/history`, `/usage/logs`, `/usage/request-logs`, `/usage/[connectionId]`, `/usage/token-limits`, `/usage/budget` → **logs-costs-usage.md** | L439 |
| **Settings** | `/api/settings[/proxy][/proxy/test][/ip-filter][/thinking-budget][/system-prompt][/compression]`, `/api/settings/purge-request-history` | L449 |
| **Context & compression** | `/api/compression/preview\|language-packs\|rules`, `/api/context/caveman/config`, `/api/context/rtk/*`, `/api/context/combos[/id][/assignments]`, `/api/context/analytics` | L462 |
| **Monitoring** | `/api/sessions`, `/api/rate-limits`, `/api/monitoring/health`, `/api/cache/stats` | L479 |
| **Backup / export-import** | `/api/db-backups` (GET/PUT/POST), `/db-backups/export\|import\|exportAll` | L488 |
| **Cloud sync** | `/api/sync/cloud`, `/api/sync/initialize`, `/api/cloud/*` | L499 |
| **Tunnels** | `/api/tunnels/cloudflared`, `/api/tunnels/ngrok` (GET status / POST `action=enable\|disable`) | L507 |
| **CLI tools** | `/api/cli-tools/{claude,codex,droid,openclaw}-settings`, `/api/cli-tools/runtime/[toolId]` | L516 |
| **ACP agents** | `/api/acp/agents` (GET/POST/DELETE) | L528 |
| **Resilience & rate-limits** | `/api/resilience[/reset][/model-cooldowns]`, `/api/rate-limits`, `/api/rate-limit` | L538 |
| **Evals** | `/api/evals` (GET/POST) | L551 |
| **Policies** | `/api/policies` (GET/POST/DELETE) | L557 |
| **Compliance** | `/api/compliance/audit-log` | L563 |
| **v1beta (Gemini)** | `/v1beta/models[/{...path}]` | L569 |
| **Internal/system** | `/api/init`, `/api/tags`, `/api/restart`, `/api/shutdown`, `/api/system/env/repair` | L578 |
| **OAuth env repair** | `POST /api/system/env/repair` `{provider}` → `{repaired[], backupPath}` (v3.6.1+) | L590 |
| **Webhooks** | `/api/webhooks[/id][/test]` | L800 |
| **Guardrails** | `/api/guardrails`, `/api/guardrails/test` | L1339 |

Other surfaces in the full doc: Budget (`/api/usage/budget`, L718), Token Limits (`/api/usage/token-limits`, L740 — `429` when exceeded), Telemetry (L698), Agents Protocol / Management Proxies (L833/L858), Skills/Memory/MCP/A2A servers (L908–L1018), Cloud/Evals/Assess (L1022), ACP management (L1041), Analytics & Observability (L1089).

## Quotas & issue reporting

`GET /v1/quotas/check?provider=&accountId=` pre-validates quota before issuing a registered key. `POST /v1/issues/report` files a quota/key failure to GitHub (needs `GITHUB_ISSUES_REPO` + token). Both Bearer-authed. `§Quotas & Issues (L361)`.

## Request processing pipeline

Client → `/v1/*` handler → model resolved (direct or alias/combo) → credentials selected from local DB → cache check + compression (chat) → upstream provider → response translated back → usage/analytics/logs recorded → fallback on error per combo rules. `§Request Processing (L767)`. Architecture: `docs/architecture/ARCHITECTURE.md`.
