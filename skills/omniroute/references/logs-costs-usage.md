# OmniRoute Logs, Costs, Usage & Quota

> Enable + read logs, understand how costs are estimated (savings tracker, not a bill), find the Costs dashboard + REST/CLI/MCP surfaces, and configure quota enforcement, retention & alerting.

**When you need this file:** turning on log files, reading `omniroute logs` / Request Logs, explaining a cost figure or pricing source, finding `/dashboard/costs`, calling `/api/usage/*` or `/api/pricing/*`, setting per-key budgets/quotas, planning retention/storage, or wiring Prometheus/Slack/PagerDuty alerts. For *why a request failed* + resilience/health see **debugging.md**. For env vars (logging, pricing-sync) see **config-and-env.md**; for usage/analytics auth see **auth-and-api.md**; CLI overview in **cli-commands.md**.

Default port **20128**; dashboard at **/dashboard**.

---

## Where do I look?

| Need | Dashboard | REST | CLI |
|---|---|---|---|
| **Application logs** | — (files under `logs/`) | — | `omniroute logs` |
| **Request / call logs** | `/dashboard/costs` Request Logs; **Clean history** action | `GET /api/usage/call-logs` | `omniroute usage logs [--follow] [--search]` |
| **Proxy logs** | Request Logs | `GET /api/usage/proxy-logs` | `omniroute usage proxy-logs` |
| **Cost analytics** | `/dashboard/costs` (Cost Overview) | `GET /api/usage/analytics` | `omniroute cost`, `omniroute usage analytics` |
| **Pricing (view/override/sync)** | `/dashboard/costs/pricing` | `GET/PATCH/DELETE /api/pricing`, `POST /api/pricing/sync` | `omniroute pricing list/get/sync/diff/defaults` |
| **Budgets (per API key)** | `/dashboard/costs/budget` | `GET/POST /api/usage/budget`, `/bulk` | `omniroute usage budget list/get/set/reset` |
| **Quota status / utilization** | `/dashboard/quota` | `GET /api/usage/quota`, `/api/usage/utilization` | `omniroute usage quota [--check]`, `usage utilization` |
| **Quota-share pools** | `/dashboard/costs/quota-share` | `GET /api/quota/pools/[id]/usage` | — |
| **Free-tier remaining** | Costs page | `GET /api/free-tier/summary` | — |
| **Raw usage history** | — | `GET /api/usage/history` | `omniroute usage history` |
| **For agents (MCP)** | — | — | `omniroute_cost_report`, `omniroute_check_quota` |

> Most `/api/usage/*` + `/api/pricing/*` endpoints require **management auth** (loopback/JWT, `requireManagementAuth`). See **auth-and-api.md**.

---

## Logs

### Enable log files
Set `APP_LOG_TO_FILE=true` in `.env`. Application logs are written under `<repo>/logs/`. Request artifacts go to `${DATA_DIR}/call_logs/YYYY-MM-DD/…` **when the call-log pipeline is enabled in settings**. Tuning:
- `CALL_LOG_PIPELINE_CAPTURE_STREAM_CHUNKS=false` — omit stream-chunk payloads.
- `CALL_LOG_PIPELINE_MAX_SIZE_KB` — change the per-artifact cap (KB).

If no logs appear: confirm `APP_LOG_TO_FILE=true` **and** that call-log capture is enabled. `docs/getting-started/TROUBLESHOOTING.md §Enable Log Files (L237)`, `§Quick Fixes (L37)`. Logging env vars: **config-and-env.md**.

### Read logs
- **CLI**: `omniroute logs`; or `omniroute usage logs [--limit 100] [--follow] [--api-key <k>] [--search <q>]` for per-request call logs.
- **Dashboard**: Request Logs (under the Costs area) shows per-request model, tokens, cost, latency, status.
- **REST**: `GET /api/usage/call-logs` (per-request), `GET /api/usage/proxy-logs` (proxy).

### Runtime storage
- Main state: `${DATA_DIR}/storage.sqlite` (providers, combos, aliases, keys, settings). `DATA_DIR` defaults to `~/.omniroute`; override with `DATA_DIR=/writable/dir` (fixes `EACCES`).
- Usage: SQLite tables in `storage.sqlite` — `usage_history`, `call_logs`, `proxy_logs` — plus optional `${DATA_DIR}/call_logs/` artifacts.
- App logs: `<repo>/logs/…` (when `APP_LOG_TO_FILE=true`).
- **Clean history** (Request Logs page) clears `call_logs`, legacy `request_detail_logs`, and the `${DATA_DIR}/call_logs/` artifact dir.
`§Runtime Storage (L255)`.

---

## Costs — how they're estimated

> **The dashboard "cost" is a savings tracker, not a bill.** OmniRoute never charges you — it routes to providers you already connected. "$290 total cost" on free models ≈ **$290 you did not pay**. It estimates what the same traffic would cost at list prices. `docs/guides/COST_TRACKING.md §What it is (L16)`.

A model with **no pricing entry contributes $0** (shows as "Legacy / Free"). Free-tier/subscription traffic still accrues an *estimated* cost = your savings.

### Pricing source (precedence)
Resolved in `pricingSync.ts` in this order: **1. User overrides** (dashboard / `PATCH /api/pricing`) → **2. Synced external pricing** (LiteLLM `model_prices_and_context_window.json`, stored in a separate `pricing_synced` namespace so it never clobbers overrides) → **3. Hardcoded defaults**. External sync is **opt-in, off by default**:

| Env var | Default | Purpose |
|---|---|---|
| `PRICING_SYNC_ENABLED` | `false` | Enable background LiteLLM sync at startup |
| `PRICING_SYNC_INTERVAL` | `86400` | Sync interval (**seconds**, daily) |
| `PRICING_SYNC_SOURCES` | `litellm` | Comma-separated sources (only `litellm` today) |

`§The pricing source (L43)`. Also in **config-and-env.md**.

### Cost formula
Per-request, rates are **USD per 1,000,000 tokens** (`costCalculator.ts`):
- (input − cache-read − cache-creation tokens) × `input` rate
- cache-read tokens × `cached` rate (→ falls back to input)
- cache-creation tokens × `cache_creation` rate (→ input)
- output tokens × `output` rate
- reasoning tokens × `reasoning` rate (→ output)

Simplified: `cost = (prompt − cached) × input + cached × cached + completion × output`. **Subtract cached from prompt** so the cached portion isn't double-counted (Anthropic caching ≈ 10% of normal). Codex `fast`/`priority`/`flex` tiers apply a multiplier (`getCodexFastCostMultiplier`); flex ≈ 50% discount, shown as **flex savings**. Model names are normalized (strip `openai/`, `accounts/fireworks/models/`…) so old rows still match. `§The cost formula (L63)`, `USAGE_QUOTA_GUIDE.md §Cost Calculation (L90)`.

### How spend is recorded
Cost is computed **after** the response, **fire-and-forget** (no client latency). Shared-quota consumption is scheduled next event-loop tick (`spendRecorder.ts`). API-key spend is **buffered + batch-flushed** (`SpendBatchWriter`):

| Env var | Default | Purpose |
|---|---|---|
| `OMNIROUTE_SPEND_FLUSH_INTERVAL_MS` | `60000` | Flush interval (ms) |
| `OMNIROUTE_SPEND_MAX_BUFFER_SIZE` | `1000` | Max buffered entries before flush |

Dashboard cost is **recomputed on the fly** from token counts + current pricing each analytics read — so fixing a wrong price (and re-syncing) updates historical estimates **retroactively**. `§How spend is recorded (L82)`.

### Cached tokens
Tracked separately from `prompt_tokens` because cached reads are priced differently (Anthropic ~10%; `cache_read_input_tokens`). Enables a **cache-hit rate** = `cached_tokens / prompt_tokens`. `USAGE_QUOTA_GUIDE.md §Cached Tokens (L80)`.

---

## Costs dashboard

**Costs page** = `/dashboard/costs` → main **Cost Overview** tab (loads `GET /api/usage/analytics`). Shows: spend tiles (Today/7d/30d/window; range `7d`/`30d`/`90d`/`all`), headline metrics (requests, active providers/models, avg cost/request), **Cost Explorer** (group by provider/model/API key/account/service tier; cost, requests, tokens, avg, share %), token usage + in:out ratio, routing efficiency (fallback count/rate, requested-model coverage), monthly forecast, period comparison, charts (daily trend, provider share, top models, cost by key/account, heatmap), and **CSV/JSON export** (appears once cost data is non-zero). `§Costs page (L103)`.

**Sub-pages** (all under `/dashboard/costs/`): **Pricing** (`/pricing` — view/override per-model prices), **Budget** (`/budget` — per-scope spend limits), **Quota Share** (`/quota-share` — shared-quota pools + burn rate). `§Related sub-pages (L132)`.

---

## Cost & usage REST endpoints

**Usage & cost analytics** (`COST_TRACKING.md §API endpoints (L145)`):
- `GET /api/usage/analytics` — full analytics: summary, daily trend, by provider/model/API key/account/tier. Query: `range`, `startDate`, `endDate`, `apiKeyIds`, `presets`, `groupBy`.
- `GET /api/usage/utilization` — per-provider quota utilization over time (`range`=`1h`/`24h`/`7d`/`30d`, `provider`).
- `GET /api/usage/history` — raw usage rows. `GET /api/usage/call-logs` — per-request logs. `GET /api/usage/quota` — provider quota status. `GET /api/usage/proxy-logs` — proxy logs.
- `GET /api/usage?range=7d&apiKeyId=…&provider=…` — list usage records (paginated, `nextCursor`).

**Budgets** (scoped per **API key**): `GET /api/usage/budget?apiKeyId=…` (returns `dailyLimitUsd`, `weeklyLimitUsd`, `monthlyLimitUsd`, `warningThreshold`, `totalCostToday`, `totalCostMonth`…), `POST /api/usage/budget` (set limits + warning threshold), `GET /api/usage/budget/bulk`. `§Budgets (L161)`.

**Pricing**: `GET /api/pricing` (merged; `?includeSources=1`), `PATCH /api/pricing` (override `{provider:{model:{input,output,cached,…}}}`), `DELETE /api/pricing` (reset, `?provider=&model=`), `GET /api/pricing/defaults`, `GET /api/pricing/models`, `POST /api/pricing/sync` (manual LiteLLM sync), `GET /api/pricing/sync` (status), `DELETE /api/pricing/sync` (clear synced). `§Pricing (L173)`.

**Other**: `GET /api/free-tier/summary` (free-token totals + remaining), `GET /api/quota/pools/[id]/usage`.

### MCP tools
`omniroute_cost_report` (per-key cost report for a period — `{"period":"week"}`), `omniroute_check_quota` (current quota status for an API key). `USAGE_QUOTA_GUIDE.md §MCP Tools (L295)`.

---

## CLI

```bash
# -- Cost report (from /api/usage/analytics) --
omniroute cost                          # last 30d, by provider
omniroute cost --period 7d
omniroute cost --group-by model         # provider | model | combo | api-key | day
omniroute cost --since 2026-06-01 --until 2026-06-13
omniroute cost --api-key <key> --limit 50      # grand-total line; --quiet/--output json to suppress

# -- Usage --
omniroute usage analytics --period 30d [--provider <id>]
omniroute usage logs [--limit 100] [--follow] [--api-key <k>] [--search <q>]
omniroute usage quota [--provider <id>] [--check]
omniroute usage utilization [--api-key <k>]
omniroute usage history [--limit 100]
omniroute usage proxy-logs [--limit 100]
omniroute usage budget list | get [scope] | set <amount> [--scope global] [--period monthly] | reset [scope]

# -- Pricing --
omniroute pricing list [--provider <p>] [--model <m>] [--limit 200]
omniroute pricing get <model>
omniroute pricing sync [--provider <p>] [--force]      # POST /api/pricing/sync
omniroute pricing diff [--model <m>]
omniroute pricing defaults show | set [--input <p>] [--output <p>] [--cache-read <p>] [--cache-write <p>]
```
`omniroute cost` columns: group, requests, tokens in/out, cost USD, % of total. `COST_TRACKING.md §CLI (L195)`. Full CLI: **cli-commands.md**.

---

## Quota enforcement

Per-API-key quota enforced in two places: **soft** (`quotaWarnAt` → dashboard warning) and **hard** (`quotaLimit` → request rejected `429 Too Many Requests` + `Retry-After`). Config:
```ts
updateApiKey(keyId, { quotaWarnAt: 5_00, quotaLimit: 10_00, quotaWindow: "month" }); // cents; "day"|"week"|"month"|"all"
```
**Enforcement flow**: `quotaCheck()` → within limit → allow; over limit → 429 + `Retry-After`. **Snapshots** (`quotaSnapshots` table: `apiKeyId`, `window`, `used`, `limit`, `resetAt`, `createdAt`) are taken on **every request with > 0 cost** and drive the progress bar, 30-day trend, and approach-limit alerts. `USAGE_QUOTA_GUIDE.md §Quota Enforcement (L173)`.

"Quota not enforcing"? Check the key's `quotaLimit`, confirm `quotaWindow`, and verify `quotaSnapshots` rows exist. Note `/dashboard/quota` data can be **stale** — the provider's upstream truth wins, so 429s can appear while local quota looks healthy (`MONITORING_GUIDE.md §Troubleshooting (L422)`).

---

## Retention, cleanup & storage

Usage data grows ~1–10 KB/request. Retention default **90 days**, set via Database Settings UI or `/api/settings/database`. Cleanup (`src/lib/db/cleanup.ts`) runs on the background cron, deleting `usage_history` rows older than the `usageHistory` retention. Storage: ~3 MB / 9 MB (30d/90d) at 100 req/day → ~3 GB / 9 GB at 100k req/day. High traffic: shorten retention or use `aggregated_metrics` instead of raw rows. `USAGE_QUOTA_GUIDE.md §Retention and Cleanup (L315)`.

---

## Cost optimization

| Tactic | How |
|---|---|
| **Right model** | `model:"auto/fast"` for quick answers, `auto/smart` for quality. |
| **Caching** | Reuse the same large system prompt — Anthropic prompt caching saves ~90% on repeated context (automatic). |
| **Compression** | RTK + Caveman saves 15–95% on tool-heavy sessions (`compression:{engine:"rtk",intensity:"aggressive"}`). |
| **Per-key quotas** | Always set `quotaLimit` to cap runaway spend. |
| **Audit top consumers** | `GET /api/usage/analytics?groupBy=apiKey` (or `groupBy=model`) sorted by cost; Dashboard → Usage. |

"Costs higher than expected" → group by model, then by apiKey, then re-sync pricing (`POST /api/pricing/sync`). All costs `$0`/"Legacy/Free" → models lack pricing; set `PRICING_SYNC_ENABLED=true` + `omniroute pricing sync`, or `PATCH /api/pricing`. Spend lagging → lower `OMNIROUTE_SPEND_FLUSH_INTERVAL_MS`. `USAGE_QUOTA_GUIDE.md §Cost Optimization Tips (L347)`, `COST_TRACKING.md §Troubleshooting (L248)`.

---

## Observability, performance metrics & alerting

**Observability snapshot** (MCP `observability_snapshot`): circuit breakers, sessions, quota monitors, uptime/version — agents use it to route around OPEN breakers. `MONITORING_GUIDE.md §Observability Snapshot (L248)`. See **debugging.md** for health-check details.

**Performance metrics** (`services/usage.ts` etc.): `request_count`, `request_latency_ms` (histogram), `tokens_consumed`, `cost_usd`, `provider_errors`, `circuit_state_changes`, `cache_hits`, `compression_savings`, `quota_used`, `memory_used_mb`. **Latency p50/p95/p99**: dashboard `/dashboard/health` only (no REST). **Prometheus/OpenTelemetry/Datadog export**: planned for v3.9 — for now scrape `GET /api/monitoring/health` with an HTTP-based monitor (Prometheus blackbox, Datadog HTTP check). `§Performance Metrics (L347)`, `§Prometheus/OpenTelemetry Export (L368)`.

**Alerting channels** (3): Dashboard banner (always on), **Webhook** (Slack / Discord / PagerDuty / any JSON POST endpoint — configured in **Settings UI**, no webhook env vars), and Log (for external aggregation). Alert types: `quota_warning` (80%+), `quota_exhausted` (100%), `token_refresh_failed`, `token_expired`, `provider_circuit_open`, `combo_target_unhealthy`, `db_integrity_warning`, `heap_pressure`. `§Alerting (L315)`, `§Alerting Recipes (L376)`.
