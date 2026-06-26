# OmniRoute Configuration & Environment

> OmniRoute is configured by **environment variables + database feature-flag overrides**. There is **no single YAML config**; `.env` holds **secrets and operator knobs only**. ~200 env vars exist — this file covers the operationally important ones and points to the source doc for the long tail.

**When you need this file:** setting up a fresh instance, generating required secrets, choosing ports, hardening for production, tuning timeouts / circuit breakers / memory, or toggling runtime feature flags. For OAuth auth-type concepts see `providers.md`; for circuit-breaker *behavior* and resilience tuning see `debugging.md`; for how the CLI applies config see `cli-commands.md`; for pricing/usage see `logs-costs-usage.md`.

Source of truth: `docs/reference/ENVIRONMENT.md` (1105 lines) and `docs/reference/FEATURE_FLAGS.md`. Every documented var must also appear in `.env.example` (`npm run check:env-doc-sync` enforces this).

## The Config Model

| Layer | Where | Scope |
| --- | --- | --- |
| **Secrets + operator knobs** | `.env` file (env vars) | Process-wide, read at boot (some hot-reload) |
| **Feature flags** | DB `key_value` table, `feature_flags` namespace | Runtime toggles, **no redeploy**; override the same-named env var |
| **Per-provider / per-connection settings** | Dashboard → DB | Managed in UI, not `.env` |

There is **no `config.yaml`**. Payload-manipulation rules are the one JSON file (`OMNIROUTE_PAYLOAD_RULES_PATH`, default `./config/payloadRules.json`). Never commit `.env` (already in `.gitignore`).

## 1. Required Secrets

Set these **before first run** — without them the app refuses to start or runs with insecure defaults. Show NAMES + generation commands only; never store real values in docs.

| Variable | Required | Default | Purpose / generation |
| --- | --- | --- | --- |
| `JWT_SECRET` | **Yes** | _(none)_ | Signs dashboard session JWT cookies. `openssl rand -base64 48` |
| `API_KEY_SECRET` | **Yes** | _(none)_ | AES key encrypting stored API keys in SQLite. `openssl rand -hex 32` |
| `INITIAL_PASSWORD` | **Yes** | `CHANGEME` | Initial admin password (deliberately insecure default — **change before first use**, then rotate via Dashboard → Settings → Security). |
| `OMNIROUTE_WS_BRIDGE_SECRET` | **Yes (prod)** | _(unset)_ | Authenticates the internal Codex Responses WS bridge. **When unset in production, all WS bridge requests are rejected.** `openssl rand -base64 32` |
| `OMNIROUTE_PEER_STAMP_TOKEN` | No (auto) | _(auto/boot)_ | Per-process peer-IP stamp token (loopback/LAN gating). Auto-generated each boot — leave unset unless multi-process must share it. |

**Generate all at once:**

```bash
echo "JWT_SECRET=$(openssl rand -base64 48)"
echo "API_KEY_SECRET=$(openssl rand -hex 32)"
echo "INITIAL_PASSWORD=$(openssl rand -base64 16)"
echo "OMNIROUTE_WS_BRIDGE_SECRET=$(openssl rand -base64 32)"
```

Optional at-rest DB encryption: `STORAGE_ENCRYPTION_KEY` (`openssl rand -hex 32`) + `STORAGE_ENCRYPTION_KEY_VERSION` (`v1`, bump on rotation). **Back up the key — losing it = losing data.** Legacy aliases: `OMNIROUTE_CRYPT_KEY`, `OMNIROUTE_API_KEY_BASE64`.

## 2. Network & Ports

Default single port: **`20128`** (Dashboard UI + `/v1/*` API on one port).

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `20128` | Primary port (single-port mode: Dashboard + API). |
| `OMNIROUTE_PORT` | _(unset)_ | **Takes precedence over `PORT`** inside Electron/wrappers. |
| `API_PORT` / `API_HOST` | _(unset)_ / `0.0.0.0` | Serve `/v1/*` on a separate port + bind addr (split mode). |
| `DASHBOARD_PORT` | _(unset)_ | Serve Dashboard UI on its own port (split mode). |
| `PROD_DASHBOARD_PORT` / `PROD_API_PORT` | `20130` / `20131` | Host-published ports in `docker-compose.prod.yml`. |
| `LIVE_WS_PORT` / `LIVE_WS_HOST` | `20129` / `127.0.0.1` | Real-time dashboard WebSocket (loopback; `0.0.0.0`+`LIVE_WS_ALLOWED_ORIGINS` to expose). |
| `RELAY_IP_PER_MINUTE` | `30` | Per-(token,IP) relay rate limit (req/min, in-memory). `0` disables IP gate. |
| `NODE_ENV` / `HOST` | `production` / `0.0.0.0` | Logging/cache profile; Next.js bind address. |

**Port modes:** (1) **Single** — `PORT=20128` serves both. (2) **Split** — `DASHBOARD_PORT=20128` + `API_PORT=20129` + `API_HOST=0.0.0.0` (e.g. API on LAN, Dashboard on localhost). (3) **Docker prod** — `PROD_DASHBOARD_PORT`/`PROD_API_PORT` map container→host. Full table: `ENVIRONMENT.md §3 (L115)`.

## 3. Storage & Database

SQLite via `better-sqlite3`. Key vars: `DATA_DIR` (default `~/.omniroute/`; set `/data` for Docker volumes), `STORAGE_ENCRYPTION_KEY` (above), `DISABLE_SQLITE_AUTO_BACKUP` (`false`), `OMNIROUTE_SKIP_DB_HEALTHCHECK` (`0`→`1` for faster boot / short tasks), `OMNIROUTE_MAX_PENDING_MIGRATIONS` (`50`; raise to restore old backups). Batch/spend writer + backup knobs: `ENVIRONMENT.md §2 Storage & Database (L78)`.

## 4. Security & Authentication Hardening

| Variable | Default | Production minimum |
| --- | --- | --- |
| `AUTH_COOKIE_SECURE` | `false` | **`true`** behind HTTPS (else cookies leak). |
| `REQUIRE_API_KEY` | `false` | **`true`** — authenticate all `/v1/*` proxy calls. |
| `ALLOW_API_KEY_REVEAL` | `false` | Keep **`false`** — never expose keys in UI on shared hosts. |
| `CORS_ORIGIN` | `*` | Restrict to your domain. |
| `MAX_BODY_SIZE_BYTES` | `10485760` (10 MB) | Lower (e.g. 5 MB) to bound payloads. |
| `OUTBOUND_SSRF_GUARD_ENABLED` | `true` | Keep on — blocks calls to private/loopback IPs. |
| `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS` | `false` | **`true` REQUIRED for self-hosted providers** (Ollama, LM Studio, vLLM). |
| `MACHINE_ID_SALT` / `OMNIROUTE_CLI_SALT` | salts | Change per-deploy for isolation; rotating CLI salt rotates all CLI tokens. |
| `DEFAULT_RATE_LIMIT_PER_DAY` | `1000` | Per-key fallback budget (N/day, 5N/week, 20N/month). `0` = unlimited. |

**Hardening minimum:** `AUTH_COOKIE_SECURE=*** `REQUIRE_API_KEY=*** `ALLOW_API_KEY_REVEAL=*** `CORS_ORIGIN=https://your.domain`. Plus `NO_LOG_API_KEY_IDS` (GDPR): `ENVIRONMENT.md §4 (L167)`.

**Input sanitization / PII** (`§5, L196`, all default off): `INPUT_SANITIZER_ENABLED` + `INPUT_SANITIZER_MODE` (`warn`|`block`|`redact`), `PII_REDACTION_ENABLED` (request side), `PII_RESPONSE_SANITIZATION` + `_MODE` (response side). Enterprise compliance = all `true` with `block`.

## 5. Timeout Hierarchy (the knobs operators tune)

All ms. Centralized in `src/shared/utils/runtimeTimeouts.ts`. `REQUEST_TIMEOUT_MS` is the global override at the top.

```
REQUEST_TIMEOUT_MS (global override)
├─ FETCH_TIMEOUT_MS (upstream provider calls, 600000)
│   ├─ FETCH_HEADERS/BODY_TIMEOUT_MS, TLS_CLIENT_TIMEOUT_MS (inherit FETCH_TIMEOUT_MS)
│   ├─ FETCH_CONNECT_TIMEOUT_MS (30000, independent)
│   └─ FETCH_KEEPALIVE_TIMEOUT_MS (4000, independent)
├─ STREAM_IDLE_TIMEOUT_MS (600000 — max silence between SSE chunks)
├─ STREAM_READINESS_TIMEOUT_MS (80000 — time to first non-ping event)
└─ API_BRIDGE_PROXY_TIMEOUT_MS (30000)
    ├─ API_BRIDGE_SERVER_REQUEST_TIMEOUT_MS (300000)
    ├─ API_BRIDGE_SERVER_HEADERS_TIMEOUT_MS (60000)
    ├─ API_BRIDGE_SERVER_KEEPALIVE_TIMEOUT_MS (5000)
    └─ API_BRIDGE_SERVER_SOCKET_TIMEOUT_MS (0 = disabled)
```

Also: `SHUTDOWN_TIMEOUT_MS` (`30000` SIGTERM grace), `OMNIROUTE_DEFAULT_FETCH_TIMEOUT_MS` (`120000` fallback). Per-provider TLS-client timeouts `OMNIROUTE_{CHATGPT,CLAUDE,PPLX,GROK}_TLS_TIMEOUT_MS` (~60000) + `_GRACE_MS` (10000). **Common tunes:** long codegen `REQUEST_TIMEOUT_MS=900000`; fast-fail API `API_BRIDGE_PROXY_TIMEOUT_MS=10000`; extended-thinking `STREAM_IDLE_TIMEOUT_MS=300000`. Full table: `ENVIRONMENT.md §15 Timeout Settings (L552)`.

## 6. Circuit Breaker Thresholds

Provider-level breaker tuning (scaled for 500+ connections since v3.6). Behavior detail in `debugging.md`. Pattern: `OMNIROUTE_CIRCUIT_BREAKER_<TYPE>_THRESHOLD` (consecutive fails before trip) + `_RESET_MS` (reset window).

- **OAuth** providers: threshold `8`, reset `60000`.
- **API-key** providers: threshold `12`, reset `30000`.
- **Local** (Ollama, LM Studio): threshold `2`, reset `15000`.

Related: `PIN_DROP_BACKOFF_LEVEL` (`2`), `PIN_DROP_GRACE_MS` (`20000`). Proxy/retry resilience (`§21 Proxy Health, L779`): `REQUEST_RETRY` (`2`), `MAX_RETRY_INTERVAL_SEC` (`30`), `RATE_LIMIT_MAX_WAIT_MS` (`120000`), `PROVIDER_COOLDOWN_ENABLED` (opt-in), `STREAM_RECOVERY_ENABLED` / `STREAM_RECOVERY_MIDSTREAM_ENABLED` (opt-in truncated-stream recovery).

## 7. Logging

Read by `src/lib/logEnv.ts`; writes stdout + rotated files. `APP_LOG_LEVEL` (`info`; `debug`/`warn`/`error`), `APP_LOG_FORMAT` (`text`|`json`), `APP_LOG_TO_FILE` (`true`; `false` for air-gapped/CI), `APP_LOG_FILE_PATH` (`logs/application/app.log`), `APP_LOG_MAX_FILE_SIZE` (`50M`), `APP_LOG_RETENTION_DAYS`/`APP_LOG_MAX_FILES` (`7`/`20`), `CALL_LOG_RETENTION_DAYS` (`7`), `CALL_LOGS_TABLE_MAX_ROWS`/`PROXY_LOGS_TABLE_MAX_ROWS` (`100000`).

Chat-artifact truncation (`CHAT_LOG_*`) + pipeline capture: `ENVIRONMENT.md §16 (L635)`. **Debug vars** (`§22, L822`, e.g. `CURSOR_DEBUG`, `DEBUG_RESPONSES_SSE_TO_JSON`) are verbose and may leak data — **never enable in production.**

## 8. Memory Optimization & Compression

`OMNIROUTE_MEMORY_MB` (`512`; V8 heap limit, sets `--max-old-space-size` for Docker / `omniroute serve`), `PROMPT_CACHE_MAX_SIZE`/`_MAX_BYTES`/`_TTL_MS` (`50`/2 MB/5 min, system-prompt cache), `SEMANTIC_CACHE_MAX_SIZE`/`_MAX_BYTES`/`_TTL_MS` (`100`/4 MB/30 min, temp=0 response cache), `STREAM_HISTORY_MAX` (`50`, live-view buffer), `CONTEXT_LENGTH_DEFAULT` (`128000`, fallback max context), `OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` (flag `false`, compress MCP tool descriptions to save tokens).

**Low-RAM Docker:** `OMNIROUTE_MEMORY_MB=128`, `PROMPT_CACHE_MAX_SIZE=20`/`MAX_BYTES=524288`, `SEMANTIC_CACHE_MAX_SIZE=25`/`MAX_BYTES=1048576`, `STREAM_HISTORY_MAX=10`. Memory-engine embedding/vector knobs (`MEMORY_*`, `HF_HUB_ENDPOINT` for air-gapped HF mirror): `ENVIRONMENT.md §17 (L664)`.

**Pricing sync** (overlaps `logs-costs-usage.md`): `PRICING_SYNC_ENABLED` (`false`, opt-in), `PRICING_SYNC_INTERVAL` (`86400`s), `PRICING_SYNC_SOURCES` (`litellm`). `ENVIRONMENT.md §18 (L713)`.

## 9. OAuth Provider Credential Env Vars (names only)

Built-in client IDs work for **localhost dev**; for remote deployments register your own at each provider's console and set `NEXT_PUBLIC_BASE_URL` so redirect URIs match. The auth-type concept (public client vs client+secret vs PKCE vs token) lives in **`providers.md`** — this section is just the env var **names**.

- **Public client (ID only):** `CLAUDE_OAUTH_CLIENT_ID` (+ `CLAUDE_CODE_REDIRECT_URI`), `CODEX_OAUTH_CLIENT_ID`, `QWEN_OAUTH_CLIENT_ID`, `KIMI_CODING_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_ID`.
- **Needs `_SECRET` (Google, localhost-only by default):** `GEMINI_OAUTH_CLIENT_ID`/`_SECRET`, `GEMINI_CLI_OAUTH_CLIENT_ID`/`_SECRET`, `ANTIGRAVITY_OAUTH_CLIENT_ID`/`_SECRET`.
- **PKCE / configurable URLs:** `GITLAB_DUO_OAUTH_CLIENT_ID`/`_SECRET` + `GITLAB_DUO_BASE_URL` (legacy `GITLAB_OAUTH_*`); `QODER_OAUTH_CLIENT_ID`/`_SECRET`/`_AUTHORIZE_URL`/`_TOKEN_URL` (or `QODER_PERSONAL_ACCESS_TOKEN` to bypass OAuth).
- **Other:** `WINDSURF_FIREBASE_API_KEY`, `WINDSURF_API_KEY` (Windsurf/Devin — public, not secrets).

⚠️ **Google OAuth (Gemini, Antigravity) only works on localhost** — for remote, create a Web-application OAuth 2.0 Client ID in Google Cloud Console and add your server URL as an Authorized redirect URI. Treat all values as `[REDACTED]` in examples. Full list + User-Agent overrides (`{PROVIDER_ID}_USER_AGENT`): `ENVIRONMENT.md §11 (L413)`, `§12 (L462)`.

## 10. Feature Flags

Named runtime toggles (boolean/enum) persisted in the DB **without redeploy**. Single source of truth: `src/shared/constants/featureFlagDefinitions.ts`. **33 flags across 6 categories.**

**Catalog by category** (⟳ = `requiresRestart`; default in parens):

- **Security (7):** `REQUIRE_API_KEY` (`false`), `INPUT_SANITIZER_ENABLED` (`true`), `INJECTION_GUARD_MODE` enum `off`/`warn`/`block`/`redact` (`off`), `PII_REDACTION_ENABLED` (`false`), `PII_RESPONSE_SANITIZATION` + `_MODE` (`false`/`redact`), `OUTBOUND_SSRF_GUARD_ENABLED` (`true`).
- **Network (7):** `ENABLE_TLS_FINGERPRINT`⟳ (`false`), `ONEPROXY_ENABLED` (`true`), `PROXY_AUTO_SELECT_ENABLED` (`false`), `OMNIROUTE_CONTROL_PLANE_PROXY_DIRECT_FALLBACK` (`false`), `MITM_DISABLE_TLS_VERIFY`⟳ **(danger)** (`false`), `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS` (`false`), `ENABLE_CC_COMPATIBLE_PROVIDER`⟳ (`false`).
- **Policies (3):** `TOOL_POLICY_MODE` enum `disabled`/`warn`/`block` (`disabled`), `RATE_LIMIT_AUTO_ENABLE` (`false`), `ALLOW_MULTI_CONNECTIONS_PER_COMPAT_NODE`⟳ (`false`).
- **Runtime (10):** `OMNIROUTE_EMERGENCY_FALLBACK` (`true`, see below), `OMNIROUTE_MCP_ENFORCE_SCOPES` (`true`), `OMNIROUTE_MCP_COMPRESS_DESCRIPTIONS` (`false`), `OMNIROUTE_ENABLE_RUNTIME_BACKGROUND_TASKS` (`false`), `OMNIROUTE_DISABLE_BACKGROUND_SERVICES`⟳ (`false`), `OMNIROUTE_RTK_TRUST_PROJECT_FILTERS` (`false`), `OMNIROUTE_ENABLE_LIVE_WS`⟳ (`true`), `OMNIROUTE_CODEX_WS_ENABLED` (`true`), `MODEL_CATALOG_INCLUDE_NAMES` (`true`), `ARENA_ELO_SYNC_ENABLED` (`true`).
- **CLI (3):** `CLI_COMPAT_ALL`⟳ (`false`), `MODEL_ALIAS_COMPAT_ENABLED` (`false`), `PRICING_SYNC_ENABLED` (`false`).
- **Health (3):** `OMNIROUTE_DISABLE_LOCAL_HEALTHCHECK` (`false`), `OMNIROUTE_DISABLE_TOKEN_HEALTHCHECK` (`false`), `SKILLS_SANDBOX_NETWORK_ENABLED` (`false`).

⟳ flags are persisted instantly but re-read only at process restart (dashboard shows a **Restart Server** banner). Enum flags reject out-of-range values (400). Full catalog: `FEATURE_FLAGS.md §Flag Catalog (L47)`.

### Flag Resolution Order (exact, per doc)

`resolveFeatureFlag()` resolves the effective value with this precedence (**highest wins**):

1. **DB override** — value in `key_value` table, `feature_flags` namespace (set via dashboard or REST API).
2. **Environment variable** — `process.env[<KEY>]` if set and non-empty.
3. **Definition default** — `defaultValue` from `featureFlagDefinitions.ts`.

> Documented order is **DB override > env var > default** (`FEATURE_FLAGS.md §Resolution Order, L24`). The doc lists **no request-header tier** — most flags have a same-named env var, and the DB override always beats it. A boolean is "enabled" when its value is `"true"`, `"1"`, or `"yes"`.

### Toggling a Flag

- **Dashboard:** Settings → Feature Flags (`/dashboard/settings/feature-flags`). Search/filter, toggle/dropdown, a **source badge** (`DB`/`ENV`/`DEF`), per-flag **Reset** (DB-sourced only), **Reset All Overrides**.
- **REST API** (auth session required; single route `/api/settings/feature-flags`):
  - `GET` — all flags with `effectiveValue`, `source`, summary.
  - `PUT` `{"key":"REQUIRE_API_KEY","value":"true"}` — set override; omit `value` to remove it.
  - `DELETE` — clear **all** DB overrides at once.
- **DB override** — the persistence layer behind both (`src/lib/db/featureFlags.ts`). `requiresRestart` flags need `POST /api/restart`.

```bash
curl -X PUT http://localhost:20128/api/settings/feature-flags \
  -H "Content-Type: application/json" -d '{"key":"REQUIRE_API_KEY","value":"true"}'
```

### Emergency Budget Fallback

`OMNIROUTE_EMERGENCY_FALLBACK` (category `runtime`, default **`true`**): routes **budget-exhausted requests** to a free fallback provider/model instead of failing. Set `false`/`0` (dashboard toggle, DB override, or env) to let budget-exhausted requests fail outright. `FEATURE_FLAGS.md §Emergency Budget Fallback (L213)`.

## 11. Skills Sandbox (v3.8.0+)

Limits for sandboxed user automations (`src/lib/skills/`): `SKILLS_SANDBOX_TIMEOUT_MS` (`10000` hard cap), `SKILLS_EXECUTION_TIMEOUT_MS` (orchestration, falls back to sandbox timeout), `SKILLS_MAX_FILE_BYTES` (1 MB), `SKILLS_MAX_HTTP_RESPONSE_BYTES` (250 KB), `SKILLS_MAX_SANDBOX_OUTPUT_CHARS` (`100000`), `SKILLS_SANDBOX_NETWORK_ENABLED` (**`false`** — isolated by default; enabling opens egress, pair with SSRF guard), `SKILLS_ALLOWED_SANDBOX_IMAGES`, `SKILLS_SANDBOX_DOCKER_IMAGE`. `ENVIRONMENT.md §24 (L915)`.

## 12. Deployment Scenarios (compact recipes)

All four recipes need the **§1 required secrets** (`JWT_SECRET`, `API_KEY_SECRET`, `INITIAL_PASSWORD`, plus `OMNIROUTE_WS_BRIDGE_SECRET` in prod) — generate per §1, treat as `[REDACTED]`. Deltas below.

**Minimal local dev:** `PORT=20128`, `NODE_ENV=development`. (Defaults otherwise.)

**Docker production:**
```bash
STORAGE_ENCRYPTION_KEY=<generated>   DATA_DIR=/data   # mount a volume
PORT=20128   API_PORT=20129   NODE_ENV=production
AUTH_COOKIE_SECURE=true   REQUIRE_API_KEY=true   OMNIROUTE_MEMORY_MB=512
NEXT_PUBLIC_BASE_URL=https://omniroute.example.com   BASE_URL=http://localhost:20128
CORS_ORIGIN=https://your-frontend.example.com
```

**Air-gapped / CI** (ephemeral): `NODE_ENV=production`, `OMNIROUTE_DISABLE_BACKGROUND_SERVICES=true`, `APP_LOG_TO_FILE=false`, `DATA_DIR=/tmp/omniroute-test`, `HF_HUB_ENDPOINT=<mirror>`.

**VPS + nginx + Cloudflare** (reverse proxy):
```bash
STORAGE_ENCRYPTION_KEY=<generated>   PORT=20128
AUTH_COOKIE_SECURE=true   REQUIRE_API_KEY=true
NEXT_PUBLIC_BASE_URL=https://omniroute.example.com   # MUST match public URL or OAuth fails
BASE_URL=http://127.0.0.1:20128   CORS_ORIGIN=https://omniroute.example.com
ENABLE_TLS_FINGERPRINT=true   CLI_COMPAT_ALL=1
```

> Behind any reverse proxy, `NEXT_PUBLIC_BASE_URL` **must** be your public URL — otherwise OAuth `redirect_uri` won't match. Full scenarios: `ENVIRONMENT.md §Deployment Scenarios (L855)`.

## See Also

- `providers.md` — OAuth auth-type concept, per-provider connection setup.
- `debugging.md` — circuit-breaker behavior, stream recovery, resilience tuning.
- `cli-commands.md` — how the `omniroute` CLI applies this config (`serve`, `redis`).
- `auth-and-api.md` — API keys, dashboard auth, `/v1/*` request auth.
- `logs-costs-usage.md` — pricing sync + usage/cost reporting overlaps.
- Source: `docs/reference/ENVIRONMENT.md`, `docs/reference/FEATURE_FLAGS.md`.
