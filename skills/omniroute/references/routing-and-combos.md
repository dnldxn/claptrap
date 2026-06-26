# OmniRoute Routing & Combos

> The "routing brain": how `auto/` zero-config routing, the 11-factor scorer, and persisted vs virtual combos decide which of ~240 providers serves each request.

**When you need this file:** understanding or explaining auto-routing, the scoring factors, mode packs, multi-account behavior, self-healing, or answering "why did my request go to model X?". For the full strategy catalog and Fusion multi-model fan-out, see combo-strategies.md.

## The `auto/` prefix (zero-config auto-routing)

Set `model: "auto"` (or a variant) in any OpenAI-compatible client — no combo creation, no toggle, no config. OmniRoute builds a **virtual combo** in memory per request from your live connected providers and scores them.

| Model ID | Mode pack / behavior |
| --- | --- |
| `auto` | Balanced default, LKGP strategy, 5% exploration |
| `auto/coding` | Quality-first (taskFit-heavy) |
| `auto/fast` | Low-latency weighted (ship-fast) |
| `auto/cheap` | Cost-optimized (cheapest first) |
| `auto/offline` | Highest quota headroom (offline-friendly) |
| `auto/smart` | Quality-first + 10% exploration |
| `auto/lkgp` | Explicit Last-Known-Good Path (= bare `auto`) |

7 invokable IDs total (6 `AutoVariant` values + bare `auto`). Usage:

```
Base URL: http://localhost:20128/v1
model: "auto/coding"
```

**Request flow** (`docs/routing/AUTO-COMBO.md §Zero-Config Auto-Routing (L13)`):
1. `src/sse/handlers/chat.ts` detects the `auto/` prefix.
2. Queries all **active** provider connections from the DB.
3. Filters to those with valid credentials (API key or non-expired OAuth).
4. Picks the model per connection (`connection.defaultModel` or provider's first).
5. Builds a virtual combo in-memory (no DB write).
6. Routes via the variant's weight profile + LKGP strategy.

Key properties: always-on, dynamic (new providers auto-expand the pool), session-sticky (LKGP), multi-account aware, zero persistence. Live fitness can use **Arena ELO** + **models.dev** tier data when `ARENA_ELO_SYNC_ENABLED` is on (else a static fitness map).

## Category × Tier composition (`auto/<category>:<tier>`)

OpenRouter-style suffixes separate **what kind of route** (category = candidate-pool filter) from **how to optimize it** (tier = scoring weights / pool filter). Compose freely. `docs/routing/AUTO-COMBO.md §Category × Tier Composition (L29)`.

- **Categories** (filter pool by capability): `coding` · `reasoning` · `vision` · `chat` · `multimodal`. `vision`/`multimodal` keep vision-capable models; `reasoning` keeps reasoning/thinking models.
- **Tiers** (pick weights / filter): `fast` (ship-fast) · `cheap` (alias `floor`, cost-saver) · `reliable` (circuit-breaker health + latency stability) · `free` / `pro` (model-tier filter via `classifyTier`).

| Example | Resolves to |
| --- | --- |
| `auto/coding:fast` | coding pool, low-latency weights |
| `auto/coding:cheap` | coding pool, cost-optimized (`= auto/coding:floor`) |
| `auto/reasoning:pro` | reasoning/thinking models, premium tier |
| `auto/vision` | vision-capable models, balanced weights |
| `auto/multimodal:free` | multimodal models, free tier only |

Filtering is **fail-open**: if a constraint matches no connected models, the full pool is used so routing never breaks. Any valid `auto/<category>[:<tier>]` resolves on demand; a curated subset is advertised in `/v1/models` and the dashboard.

## Combo vs auto-combo (persisted vs virtual)

| | Persisted combo | Virtual auto-combo |
| --- | --- | --- |
| Created by | `POST /api/combos` | `auto/` prefix at request time |
| Storage | `combos` table, reusable by ID | In-memory, per-request, no DB write |
| Strategy | any of 17 (incl. `strategy:"auto"`) | always the 11-factor auto scorer |
| Pool | explicit `targets` / `candidatePool` | live active connections, rebuilt each request |

There is **no** `POST /api/combos/auto` endpoint. Two ways to consume auto: (1) zero-config `model:"auto/<variant>"`; (2) a persisted combo with `strategy:"auto"` + `config.auto.weights` / `candidatePool`. `GET /api/combos/auto` lists variants with their resolved pool + MAX `context_length` / `max_output_tokens`. The **virtual factory** (`virtualFactory.ts`) rebuilds the pool per request, so adding a provider expands candidates immediately — no manual editing. `docs/routing/AUTO-COMBO.md §Virtual Auto-Combo Factory (L233)`, `§API (L258)`. See auth-and-api.md for combo CRUD, cli-commands.md for combo commands.

## The 11-factor scoring system

Every auto request scores each candidate `(provider, model, connection)` with `DEFAULT_WEIGHTS` (sum = 1.0) in `scoring.ts`. Highest weighted sum wins. `docs/routing/AUTO-COMBO.md §How It Works (L103)`.

| Factor | Weight | Meaning |
| --- | --- | --- |
| `health` | 0.20 | Circuit breaker: CLOSED=1.0, HALF_OPEN=0.5, OPEN=0.0 |
| `quota` | 0.15 | Remaining quota / rate-limit headroom [0..1] |
| `costInv` | 0.15 | Inverse blended cost (60% input + 40% output price); cheaper = higher |
| `latencyInv` | 0.12 | Inverse p95 latency normalized to pool; faster = higher |
| `taskFit` | 0.08 | Task-type fitness (coding/review/planning/analysis/debugging/docs) |
| `stability` | 0.05 | Variance-based (low latency stdDev / error rate) |
| `tierPriority` | 0.05 | Account tier: Ultra=1.0, Pro=0.67, Standard=0.33, Free=0.0 |
| `tierAffinity` | 0.05 | Candidate tier vs manifest-recommended tier |
| `specificityMatch` | 0.05 | Request specificity (manifest hint) vs model tier |
| `contextAffinity` | 0.05 | Candidate context window fit for the request |
| `connectionDensity` | 0.05 | Preference for providers/accounts with stronger connection coverage |

`resetWindowAffinity` exists in source but has default weight `0`, so it is not counted among the 11 active default factors. Tier alone does **not** force Tier-1 first — bad latency or cost can let a lower tier win. To force ordering use `strategy:"priority"` or raise `tierPriority`. See config-and-env.md for weight overrides; the plain-English guide in `docs/getting-started/AUTO-COMBO-GUIDE.md` may lag the source scorer.

## Mode Packs

Five named weight profiles (`modePacks.ts`) the `auto/*` variants map to; each row sums to 1.0. `docs/routing/AUTO-COMBO.md §Mode Packs (L125)`.

| Factor | ship-fast | cost-saver | quality-first | offline-friendly | reliability-first |
| --- | --- | --- | --- | --- | --- |
| quota | 0.14 | 0.14 | 0.10 | **0.37** | 0.14 |
| health | 0.28 | 0.19 | 0.18 | 0.28 | **0.37** |
| costInv | 0.05 | **0.37** | 0.05 | 0.10 | 0.04 |
| latencyInv | **0.32** | 0.05 | 0.05 | 0.05 | 0.05 |
| taskFit | 0.10 | 0.10 | **0.37** | 0.00 | 0.10 |
| stability | 0.00 | 0.05 | 0.15 | 0.10 | **0.20** |
| tierPriority | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |
| tierAffinity | 0 | 0 | 0 | 0 | 0 |
| specificityMatch | 0 | 0 | 0 | 0 | 0 |
| contextAffinity | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 |
| resetWindowAffinity | 0 | 0 | 0 | 0 | 0 |
| connectionDensity | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |

Emphasis: ship-fast → latency + health · cost-saver → cost · quality-first → taskFit + stability · offline-friendly → quota + health · reliability-first → health + stability.

## Multi-account support

Multiple accounts/keys for the same provider each become a **separate candidate**, scored independently on their own health, quota, and latency. `docs/getting-started/AUTO-COMBO-GUIDE.md §Multi-Account Support`.

- Account A has quota → used; Account B rate-limited → skipped; Account C cheaper → preferred.
- Quota fairness across keys sharing a connection is handled by the Quota Sharing Engine (`docs/routing/QUOTA_SHARE.md`): a soft penalty (`QUOTA_SOFT_DEPRIORITIZE_FACTOR`, default 0.7) deprioritizes saturated keys; hard policy returns 429. See logs-costs-usage.md.

## Self-healing, emergency fallback & bandit exploration

`docs/routing/AUTO-COMBO.md §Self-Healing (L247)`, `§Bandit Exploration (L254)`.

- **Temporary exclusion:** score < 0.2 → excluded 5 min (progressive backoff, max 30 min).
- **Circuit breaker:** OPEN → auto-excluded; HALF_OPEN → probe requests only.
- **Incident mode:** >50% of providers OPEN → exploration disabled, stability maximized.
- **Cooldown recovery:** first request after exclusion is a "probe" with reduced timeout.
- **Auto-fallback:** if the top pick fails, the next-best candidate is tried automatically.
- **Emergency fallback:** if *all* providers fail, route to stable free providers (e.g. Kiro, Qoder) as a last resort.
- **Bandit exploration:** 5% of requests (10% for `auto/smart`) go to a random provider to discover better options; disabled in incident mode.

## Seeing which provider was used

Check the **response headers** — OmniRoute reports the actual provider + model used on every response. For deeper traces (decision reason, candidates considered, scores) see debugging.md and logs-costs-usage.md.

## "Why was my request routed to model X?" — decision path

Walk it in order:

1. **Prefix parse** — `auto/<category>:<tier>` → category filter + tier/mode-pack weights (`parseAutoPrefix`). Bare `auto` = balanced + LKGP.
2. **Pool build** — virtual factory pulls active connections with valid creds, cross-refs the registry for model + pricing. Category filter applied (fail-open).
3. **Exclusions** — OPEN circuit breakers and recently-failed (score < 0.2) candidates removed; quota-saturated keys soft-penalized ×0.7.
4. **LKGP stickiness** — for multi-turn, the last-known-good provider is tried first if still healthy.
5. **11-factor scoring** — remaining candidates scored with the variant's weights; the highest weighted sum wins (X).
6. **Bandit** — ~5% chance the pick is overridden by a random explore candidate (not in incident mode).
7. **Execute + fallback** — on failure, self-healing excludes X and the next-best is used; emergency fallback if all fail.

So X won because, given your variant's weights, it had the best blend of health / quota / cost / latency / taskFit among eligible candidates — *or* it was the sticky LKGP target, *or* a bandit explore. Confirm via response headers.

