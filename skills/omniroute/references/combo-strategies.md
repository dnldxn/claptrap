# OmniRoute Combo Strategies

> Every routing strategy OmniRoute can run on a combo — including Fusion, the one that fans a prompt out to MULTIPLE models and synthesizes one answer.

**When you need this file:** choosing or explaining a routing strategy, understanding Fusion multi-model fan-out, the auto router sub-strategies, or picking the right strategy/combo for a goal (coding, cheap-bulk, reliability, latency, quality). For the 11-factor scorer and auto-routing internals, see routing-and-combos.md.

## All 17 routing strategies

Declared in `routingStrategies.ts` (`ROUTING_STRATEGY_VALUES`); set per combo as `strategy`. `docs/routing/AUTO-COMBO.md §All Routing Strategies (L148)`.

| Strategy | One-liner | Use when |
| --- | --- | --- |
| `priority` | First-target ordered list by explicit priority | Fixed preference order / forced tier ordering |
| `weighted` | Weighted random by per-target weight | Split traffic by a ratio (e.g. 70/30) |
| `round-robin` | Cycle targets in order | Even, predictable rotation |
| `context-relay` | Hand off context across targets | Long conversations spanning models |
| `fill-first` | Exhaust one target's quota before next | Drain a cheap/free quota fully first |
| `p2c` | Power-of-2-choices random load balancing | Low-overhead balancing at scale |
| `random` | Uniform random selection | Simple spread, no state |
| `least-used` | Pick lowest current load | Balance concurrent load |
| `cost-optimized` | Minimize $/request from catalog pricing | Pure cost minimization |
| `reset-aware` ⭐ | Rank by quota reset time (short windows higher) | Juggling quotas with different reset windows |
| `reset-window` | Prefer soonest-resetting quota window | Maximize throughput across resets |
| `headroom` | Pick most remaining quota headroom | Avoid rate limits under load |
| `strict-random` | Random without dedup of repeats | Stress / test randomization |
| `auto` | 11-factor adaptive scoring (**recommended**) | Default smart routing |
| `lkgp` | Last-Known-Good Path (sticky to last success) | Session stickiness / caching continuity |
| `context-optimized` | Best fit for current context size | Mixed short / long context requests |
| `fusion` 🧬 | Fan out to a panel, judge synthesizes one answer | Highest quality on hard/ambiguous prompts |

⭐ new in v3.8.0 · 🧬 new in v3.8.36. Create with `POST /api/combos` (see auth-and-api.md, cli-commands.md).

## Fusion strategy (multi-model fan-out) — in depth

`fusion` is the **only** strategy that does NOT pick a single target. It is **why a request fans out to multiple models at once**. `docs/routing/AUTO-COMBO.md §Fusion Strategy (L174)`, `§Configuration (L196)` (impl `open-sse/services/fusion.ts`, ported from `decolua/9router`'s OpenRouter Fusion design).

Pipeline:
1. **Fan-out** — the prompt is sent to **every panel model in parallel**, forced non-streaming with tools stripped (the judge needs complete prose to synthesize).
2. **Quorum-grace collection** — once `minPanel` answers arrive, a short grace timer waits for stragglers, then fusion proceeds with whatever was collected; a hard timeout caps the slowest model's impact on wall time.
3. **Judge synthesis** — panel answers are **anonymized** (`Source 1`, `Source 2`, … so the judge weighs substance, not model brand) and handed to the `judgeModel`, which analyzes consensus / contradictions / partial coverage / unique insights / blind spots, then writes **one** authoritative answer. The judge call keeps the client's original `stream` flag + tools, so streaming and downstream tool use still work.
4. **Graceful degradation** — 0 panel answers → `503`; exactly 1 survivor → that answer is returned directly (nothing to fuse).

Config (on the combo's `config` blob; reuses the existing `combos` table, no migration):

| Field | Default | Purpose |
| --- | --- | --- |
| `config.judgeModel` | first panel model | Model that synthesizes the final answer |
| `config.fusionTuning.minPanel` | `2` | Answers required before the grace timer (clamped `[2, panelSize]`) |
| `config.fusionTuning.stragglerGraceMs` | `8000` | How long to wait for laggards after quorum |
| `config.fusionTuning.panelHardTimeoutMs` | `90000` | Absolute cap so a hung model can't stall the request |

```bash
curl -X POST http://localhost:20128/api/combos -H "Content-Type: application/json" -d '{
  "name":"fusion-panel","strategy":"fusion",
  "targets":[{"model":"cc/claude-opus-4-7"},{"model":"cx/gpt-5.5"},{"model":"glm/glm-5.1"}],
  "config":{"judgeModel":"cc/claude-opus-4-7",
    "fusionTuning":{"minPanel":2,"stragglerGraceMs":8000,"panelHardTimeoutMs":90000}}}'
```

Then call it like any combo: `{"model":"fusion-panel","messages":[...]}`. **Trade-off:** fusion multiplies token cost + latency (N panel calls + 1 judge) for a quality/reliability gain — reserve it for hard, high-stakes prompts.

## Auto router sub-strategies (`config.routerStrategy`)

A persisted `strategy:"auto"` combo can swap the internal **RouterStrategy** via `config.routerStrategy` (or legacy `config.auto.routerStrategy`). 5 pluggable implementations, each picks one provider from the candidate pool given a `RoutingContext`. `docs/routing/AUTO-COMBO.md §Auto router strategies (L281)`, `§Router strategies in detail (L293)`.

| routerStrategy | Aliases | Behavior |
| --- | --- | --- |
| `rules` | — | Default 6-factor weighted scoring (quota, health, cost, latency, taskFit, stability); filters OPEN candidates |
| `cost` | `eco` | Cheapest healthy provider (sort by `costPer1MTokens` asc) |
| `latency` | `fast` | Lowest `p95LatencyMs + errorRate*1000` (reliability penalty) |
| `sla-aware` | `sla` | Best satisfies latency / error / cost SLOs |
| `lkgp` | — | Last-known-good provider first, else falls back to `rules` |

**SLA-aware** composite scoring: latency 35% · error 35% · health 15% · cost 10% · stability 5%. With `slaHardConstraints:true`, candidates sort by SLO-violation score first, then composite. Fields:

```json
{"strategy":"auto","config":{"routerStrategy":"sla-aware",
  "slaTargetP95Ms":1500,"slaMaxErrorRate":0.05,"slaMaxCostPer1MTokens":5,"slaHardConstraints":true}}
```

Custom strategies: implement `RouterStrategy`, call `registerStrategy("my-custom", impl)`, then set `config.routerStrategy:"my-custom"`. `docs/routing/AUTO-COMBO.md §Custom router strategies (L464)`.

## Router strategy selection guide

`docs/routing/AUTO-COMBO.md §Router strategy selection guide (L504)`.

| Use case | routerStrategy | Reason |
| --- | --- | --- |
| Balanced workload | `rules` | Considers all factors (default) |
| Minimize cost | `cost` / `eco` | Always picks cheapest |
| Minimize latency | `latency` / `fast` | Fastest reliable provider |
| Strict SLOs | `sla-aware` | Filters by p95 / error / cost thresholds |
| Multi-turn chat | `lkgp` | Session stickiness |

## Recommendations by goal

| Goal | Pick | Why |
| --- | --- | --- |
| **Coding** | `auto/coding` (quality-first) or `auto/coding:fast` | taskFit-heavy weights route to coding-specialist models |
| **Cheap bulk** | `auto/cheap`, combo `strategy:"cost-optimized"`, or router `cost`/`eco` | costInv 0.37 / always-cheapest; pair with `fill-first` to drain free quota |
| **Max reliability** | combo `strategy:"fusion"`, or `auto` + router `sla-aware` (hard constraints) | Fusion survives single-model failure; SLA enforces error/latency budget |
| **Lowest latency** | `auto/fast` or router `latency`/`fast` | latencyInv 0.32 / p95 sort with reliability penalty |
| **Highest quality** | `strategy:"fusion"` (panel of top models) or `auto/smart` | Judge synthesis across models; smart adds 10% exploration |

More tips: for **forced tier/provider order** use `priority`; for **quota juggling** across reset windows use `reset-aware` / `headroom`; for **even rotation** use `round-robin`. See config-and-env.md for weight tuning and providers.md for model IDs.

## Task Fitness

`taskFit` (8% of the default scorer) ranks models per task type. 30+ models scored across 6 task types: `coding`, `review`, `planning`, `analysis`, `debugging`, `documentation`. Wildcard patterns supported (e.g. `*-coder` → high coding score). `quality-first` / `auto/coding` raise this weight to 0.37, making task fitness dominate selection. `docs/routing/AUTO-COMBO.md §Task Fitness (L529)`.

## Auto variants

See **routing-and-combos.md** for the `auto`, `auto/coding`, `auto/fast`, `auto/cheap`, `auto/offline`, `auto/smart`, `auto/lkgp`, and `auto/<category>:<tier>` variant map.
