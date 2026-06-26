# OmniRoute Debugging, Resilience & Monitoring

> A model request FAILED — diagnose it fast. Triage table → per-failure fixes → resilience knobs (circuit breaker / cooldown / lockout) → how to read provider health.

**When you need this file:** a request errored or got skipped, a provider is stuck OPEN, 429s won't clear, OAuth/`fetch failed`/`Language model did not provide messages` errors, audio/translator/Docker/cloud breakage, or you need to check `/dashboard/health` and the autopilots. For LOGS, COSTS, USAGE & QUOTA see **logs-costs-usage.md**. For fallback/self-healing routing see **routing-and-combos.md**; for resilience/timeout/circuit-breaker env vars see **config-and-env.md**; for provider OAuth/health see **providers.md**.

Default port **20128**; dashboard at **/dashboard**.

---

## Triage: failure → likely cause → fix

| Symptom / error | Likely cause | Fix (fast path) |
|---|---|---|
| `429 Too Many Requests` / "Rate limit exceeded" | Subscription/key quota exhausted | Wait 1 min, or add fallback tiers in a combo, or `model:"auto"`. Cheap backup: GLM/MiniMax. |
| `"Language model did not provide messages"` | **Provider quota exhausted** | Check `/dashboard/quota`; route via combo with fallback tiers; switch to cheaper/free tier. |
| `401 Unauthorized` / "Invalid API key" | Bad/expired credential or unsynced cloud key | Re-copy key from provider; for OAuth: Dashboard → Provider → **Reconnect**; cloud: mint fresh key + Sync Now. |
| `"Invalid API key"` on **cloud** despite connected | Old/non-synced key | Create key at `/api/keys`, Enable Cloud → **Sync Now** (old keys still 401). |
| Provider validation / token refresh `"fetch failed"` | Proxy not applied to validate/refresh path | Update to **v3.5.5+** (validate routes through `runWithProxyContext`; token health resolves proxy per connection). |
| SOCKS5 `"invalid onRequestStart method"` | undici@8 vs Node 22 `fetch()` | **v3.5.5+** uses undici's own `fetch()` under a proxy dispatcher. |
| Provider skipped, **circuit OPEN** | ≥ failure threshold of `[408/500/502/503/504]` | Settings → Resilience → **Reset All** (only if provider truly up), or wait reset timeout. |
| Circuit **keeps** tripping | Real upstream failures / high latency / re-auth needed | Dashboard → Health → Provider Health for pattern; raise failure threshold; re-auth; check latency telemetry. |
| All keys for a provider skipped | Breaker OPEN **and/or** every connection in cooldown | Check breaker state **AND** each connection's `rateLimitedUntil`/`testStatus`. |
| One key fails, others work | Single bad connection | Connection **cooldown** (not breaker) handles it — let it self-recover. |
| Only one **model** fails (others ok) | Per-model quota/permission (429/404) | **Model lockout**, not connection cooldown. Re-enable via Settings → Model Cooldowns. |
| Model stuck in cooldown after expiry | Stale cooldown entry | Dashboard → Settings → Model Cooldowns → **Re-enable**; or `DELETE /api/resilience/model-cooldowns`. |
| Cloud `stream=false` → **500** (`Unexpected token 'd'`) | Upstream SSE while client wants JSON | Use `stream=true` for cloud direct calls (local runtime has SSE→JSON fallback). |
| `"CLI tool not installed"` (Docker) | Binary not found / failed healthcheck | `curl …/api/cli-tools/runtime/<tool>`; use `runner-cli` image or mount host bin + `CLI_EXTRA_PATHS`. |
| Audio "Unsupported model" / empty | Wrong prefix or bad format/size | Use `deepgram/nova-3`/`assemblyai/best`; formats mp3/wav/m4a/flac/ogg/webm, < 25 MB. |
| "Provider healthy but requests fail" | Hidden model lockout or upstream rate limit | Check autopilot issues + recent errors; test connection; upstream limits aren't visible locally. |

> Provider statuses `401/403/429` are **account-level** (→ cooldown/lockout) and do **not** trip the provider circuit breaker. See `docs/architecture/RESILIENCE_GUIDE.md §Provider Circuit Breaker (L15)`.

---

## Common failure modes

### Rate limiting / 429
Subscription quota exhausted. Add fallback tiers, e.g. `cc/claude-opus-4-6 → glm/glm-4.7 → if/kimi-k2-thinking`; GLM/MiniMax as cheap backup. Auto rate-limit applies **only to API-key providers** (not OAuth/subscription) and needs `429`/`Retry-After` upstream — enable under **Settings → Resilience → Provider Profiles**. ModelScope emits provider-specific `Retry-After`; on v3.8.0+ enable `useUpstream429BreakerHints`. `docs/getting-started/TROUBLESHOOTING.md §Rate Limiting (L143)`, `§Resilience Settings (L329)`.

### OAuth token expired
Auto-refreshes. If it persists: **Dashboard → Provider → Reconnect**, or delete + re-add. Kiro multi-account: pre-v3.8.0 connections share one OIDC client (refreshing one invalidates the other) — delete + re-import on v3.8.0+ for per-connection isolation. `§OAuth Token Expired (L152)`. See **providers.md**.

### "fetch failed" (proxy / validation)
Provider-validation (`POST /api/providers/validate`) and background token refresh previously bypassed proxy config. Fixed in **v3.5.5+** (validate uses `runWithProxyContext`; token health resolves proxy per connection; SOCKS5 on Node 22 also fixed). `§Proxy Issues (L107)`.

### "Language model did not provide messages"
= provider quota exhausted. Check the dashboard quota tracker, use a combo with fallback tiers, or switch to a cheaper/free tier. `§Provider Issues (L131)`.

### Circuit breaker stuck OPEN / keeps tripping
**OPEN** = requests blocked until cooldown expires; combo routing skips the provider. Reset: **Dashboard → Settings → Resilience** → breaker card → **Reset All** (verify the provider is up first), or wait for the reset timeout. If it **keeps** tripping: inspect Health → Provider Health for the failure pattern, raise the failure threshold under Settings → Resilience → Provider Profiles, re-authenticate, and review latency telemetry (timeouts trip it). `§Circuit Breaker Issues (L267)`. A provider permanently excluded *after* the window usually means code read raw `state` instead of `getStatus()`/`canExecute()` (`RESILIENCE_GUIDE.md §Debugging (L212)`).

### Cloud issues
- **Sync errors** — `BASE_URL` must point to your running instance (e.g. `http://localhost:20128`); `CLOUD_URL` to your cloud endpoint; keep `NEXT_PUBLIC_*` aligned with server values.
- **`stream=false` → 500** — use `stream=true` for cloud direct calls.
- **"Invalid API key"** — mint a fresh key, Enable Cloud → Sync Now; old/non-synced keys still 401.
`§Cloud Issues (L183)`.

### Docker: CLI tool "not installed"
`curl -s http://localhost:20128/api/cli-tools/<tool>-settings | jq '{installed,runnable,commandPath,runtimeMode,reason}'` (codex/claude/openclaw). Portable mode → image target **`runner-cli`** (bundled CLIs). Host-mount → set `CLI_EXTRA_PATHS` and mount the host bin read-only. `installed=true` + `runnable=false` = found but failed healthcheck. `§Docker Issues (L205)`.

### Audio transcription
Use the correct prefix (`deepgram/nova-3`, `assemblyai/best`); confirm the provider is connected. Empty/failure → check formats (`mp3/wav/m4a/flac/ogg/webm`), file size (typically < 25 MB), and key validity. `§Audio Transcription (L291)`.

### Translator debugging
**Dashboard → Translator** has four modes: **Playground** (compare in/out formats side by side), **Chat Tester** (live request/response + headers), **Test Bench** (batch across format combos), **Live Monitor** (real-time flow). Common: thinking tags missing (check provider thinking support + budget), tool calls dropped (verify in Playground), system prompt missing (Claude/Gemini differ). Most legacy format bugs (`x_groq` validation, `system` role on GLM/ERNIE, `developer` role, Gemini `json_schema`) are auto-handled on v3.x+. `§Translator Debugging (L306)`.

### v3.8.0 known issues (quick hits)
Windsurf OAuth 401 → set `WINDSURF_FIREBASE_API_KEY` + `WINDSURF_API_KEY`, restart, reconnect. Devin CLI auth → install CLI, set `CLI_DEVIN_BIN`. Command Code 403 → `omniroute providers` to re-trigger OAuth. WS bridge 401 in prod → set `OMNIROUTE_WS_BRIDGE_SECRET` (`openssl rand -hex 32`). Responses API `background:true` degrades to sync (by design). `§v3.8.0 Known Issues (L386)`.

## Resilience knobs (3-layer model)

OmniRoute has **three distinct** resilience layers — keep them separate when debugging. `docs/architecture/RESILIENCE_GUIDE.md`.

### 1. Provider circuit breaker — scope: whole provider
States: `CLOSED` (normal) → `DEGRADED` (still serving, elevated failures tracked) → `OPEN` (blocked, combos skip it) → `HALF_OPEN` (probe after reset timeout). **Lazy recovery**: state refreshes to `HALF_OPEN` on read (`getStatus()`/`canExecute()`) — no background timer. Defaults (Dashboard → Settings → Resilience):

| Class | Degraded at | Opens at | Reset timeout |
|---|---|---|---|
| OAuth | 5 failures | 8 failures | 60s |
| API-key | 7 failures | 12 failures | 30s |
| Local | derived | 2 failures | 15s |

Trips **only** on provider-level `[408, 500, 502, 503, 504]`. `degradationThreshold` → DEGRADED; `failureThreshold` → OPEN. Status: `GET /api/monitoring/health`; reset: `POST /api/resilience/reset`. `§Provider Circuit Breaker (L15)`.

### 2. Connection cooldown — scope: one connection/key
Skips one bad key while other connections for the same provider keep serving. Fields: `rateLimitedUntil`, `testStatus:"unavailable"`, `lastError`/`lastErrorType`/`errorCode`, `backoffLevel`. Default base cooldowns: **OAuth 5s, API-key 3s**; API-key 429 prefers upstream `Retry-After`/reset headers. Backoff = `baseCooldownMs * 2 ** failureIndex`. **Terminal states** (`banned`, `expired`, `credits_exhausted`) are NOT cooldowns — they persist until creds change or an operator resets. Lazy recovery on past `rateLimitedUntil`; a successful use clears all error fields. `§Connection Cooldown (L53)`.

### 3. Model lockout — scope: provider + connection + model
Quarantines one model (per-model 429 quota, local 404, mode/permission failures) without disabling the whole connection. **Off by default** (`enabled:false`). Defaults: `errorCodes [403,404,429,502,503,504]`, `baseCooldownMs 120_000`, `maxCooldownMs 1_800_000`, `maxBackoffSteps 10`, `useExponentialBackoff true`. **Success-decay recovery**: a healthy response **halves** the model's `failureCount` (at 0 the lockout is deleted) — recovery can beat timer expiry. State is **in-memory** (lost on restart); settings persist. List: `GET /api/resilience/model-cooldowns`; re-enable: `DELETE /api/resilience/model-cooldowns` body `{provider,connection,model}` (management auth), or Settings → Model Cooldowns → Re-enable. `§Model Lockout (L94)`.

### Quota-share concurrency control (v3.8.36)
Subscription accounts accept only ~1–3 concurrent requests; acute under `qtSd/…` quota-share combos. Three layers:
- **Per-connection cap** `max_concurrent` (`provider_connections.max_concurrent`) — set to the account's real concurrency (GLM ~1, MiniMax ~2); empty = unlimited.
- **Request serialization** — a positive cap routes concurrent requests through a per-connection semaphore (`qsconn:<connectionId>`); excess **waits** instead of flooding. **Fail-open** (never rejects a dispatchable request). Toggle: Settings → Resilience → Quota-share per-connection concurrency (default on).
- **Combo cooldown-aware retry** — for quota-share combos, a request that would crystallize a SHORT transient 429 **waits it out and re-dispatches**. Bounded by `comboCooldownWait` (`maxWaitMs 5s`, `maxAttempts 2`, `budgetMs 8s`). Never waits on `quota_exhausted` (locked till midnight) or auth/not-found. `§Quota-Share Concurrency Control (L162)`, `§Combo cooldown-aware retry (L192)`.

### Exponential backoff tuning & anti-thundering-herd
Provider profiles: **base delay** 1s, **max delay** 30s, **multiplier** 2×. Anti-thundering-herd: concurrent requests to a rate-limited provider are serialized via mutex + auto rate-limiting (automatic for API-key providers); the cooldown guard prevents double-incrementing `backoffLevel` or over-extending cooldown. `TROUBLESHOOTING.md §Resilience Settings (L329)`. Tune via **config-and-env.md**.

---

## Monitoring: is the provider actually healthy?

> Only `GET /api/monitoring/health` is a REST endpoint. All other monitoring data (provider health, autopilot issues, quota monitors, token health, latency) comes from the **dashboard** or the MCP tool `observability_snapshot`. `docs/ops/MONITORING_GUIDE.md §Health Check API (L102)`.

| Where | What it shows |
|---|---|
| `/dashboard/health` | Server status, DB integrity/WAL, provider summary (active/healthy/breaker-open), quota monitors, last 10 errors w/ stacks, heap pressure. |
| `/dashboard/providers` | Per-provider: health (G/Y/R), circuit state, connections, per-model health, today's cost, 24h errors. Click → recent requests + latency, per-connection scores, lockouts, autopilot recs. |
| `GET /api/monitoring/health` | JSON: `status`, `version`, `uptime`, checks (database, writeable, integrity, foreign_keys, heap_pressure), `active_sessions`, providers `{total,healthy,degraded,down}`. |
| MCP `observability_snapshot` | `circuitBreakers[]`, `sessions[]`, `quotaMonitors`, uptime/version — agents read this to route around OPEN breakers. |

`§/dashboard/health (L49)`, `§/dashboard/providers (L62)`, `§Observability Snapshot (L248)`.

### Provider Health Autopilot
Self-healing module that detects issues, generates recommended actions, and (manual mode by default) lets you apply them from the dashboard. **Issue types**: `provider_circuit_open` (critical), `provider_circuit_half_open` (warn), `connection_cooldown` (warn), `stale_connection_error` (warn, 30+ min), `terminal_connection_error` (critical), `inactive_connection` (info), `model_lockout` (warn), `quota_monitor_warning` (≥80%). **Actions**: `clear_provider_breaker` (med), `clear_connection_cooldown`/`clear_stale_connection_error`/`clear_model_lockout` (low), `reactivate_connection` (med), `deactivate_connection` (high). Configured per-connection via `autopilotMode` (DB), **not** env. `§Provider Health Autopilot (L146)`.

### Combo Health Autopilot
Combo-specific equivalent: detects unhealthy combos, recommends **target reordering** (e.g. move a healthy target above one in lockout), suggests disabling broken targets, auto-removes dead targets after N failures. `§Combo Health Autopilot (L188)`. See **routing-and-combos.md**.

### Token health check
Background scheduler (`tokenHealthCheck.ts`) for OAuth providers: **sweep every 60s** (`TICK_MS`), per-connection check default **60 min** (`DEFAULT_HEALTH_CHECK_INTERVAL_MIN`), pre-emptive refresh on 401. Status: `valid` | `expiring_soon` | `expired` | `refresh_failed`. No REST endpoint — read via dashboard / `observability_snapshot`. Alerts: `token_refresh_failed` (3+ consecutive), `token_expired` (past expiry). `§Token Health Check (L283)`.

> Enabling logs & reading request/call logs, quota enforcement, and per-key budgets are all in **logs-costs-usage.md** (`APP_LOG_TO_FILE`, `omniroute logs`, `/dashboard/costs`, runtime storage).
