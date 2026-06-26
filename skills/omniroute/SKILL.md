---
name: omniroute
description: "Use when managing, monitoring, debugging, or configuring an OmniRoute AI gateway — authenticating and querying its API, understanding auto-routing and combos (why a request went to a given model or fanned out to several), provider auth types (OAuth vs API Key vs Cookie, e.g. claude vs claude-web), checking logs/costs/usage, tuning config, or running CLI commands. Index skill: load only the reference file your task needs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [omniroute, ai-gateway, llm-router, combos, providers, monitoring, api]
    related_skills: [hermes-providers, native-mcp]
---

# OmniRoute — Management & Monitoring

## Overview

**OmniRoute** (repo: [`diegosouzapw/OmniRoute`](https://github.com/diegosouzapw/OmniRoute),
site: [omniroute.online](https://omniroute.online)) is a self-hosted **AI gateway**: one
OpenAI-compatible endpoint that fans out across **231 providers (50+ with free
tiers)**. It auto-falls-back when a provider is rate-limited, picks the cheapest
model that works via **auto-routing / combos** (17 routing strategies), and applies
**RTK + Caveman prompt compression** (15–95% token savings). It ships a web **dashboard**,
a large management **REST API**, an internal **CLI** (`omniroute`), an **MCP server**, and
desktop/Docker/Termux builds.

This is an **index skill**. The body below holds only the facts needed on *almost every*
OmniRoute task. Everything else lives in focused `references/*.md` files — **load only the
one your task needs** rather than reading all of them. Each reference cites the upstream
doc (`docs/...md §Section (Lxx)`) so you can jump to full detail.

## When to Use

- Authenticating to or querying the OmniRoute API (chat, embeddings, images, models…).
- Explaining **why a request routed to a given model/provider**, or why it hit **multiple**
  models (fusion), or why a model request **failed** (circuit breaker, quota, OAuth expiry).
- Recommending **combos / strategies / tiers** or server **config** settings.
- Understanding **provider auth types** — OAuth vs API Key vs Cookie — even for the same
  underlying model (`claude` OAuth vs `claude-web` cookie).
- Checking **logs, costs, usage, quotas**, or provider/combo **health**.
- Making **configuration changes** (env vars, feature flags) or running **CLI** commands.

**Don't use for:** writing OmniRoute application code / plugins (read the repo's
`docs/architecture/` + `docs/dev/` directly), or unrelated LLM-routing products.

## Core Facts (true for most tasks)

| Fact | Value |
|------|-------|
| Default API/dashboard port | **20128** (`http://localhost:20128`) |
| OpenAI-compatible base | `http://localhost:20128/v1` |
| Auth header | `Authorization: Bearer <OMNIROUTE_API_KEY>` |
| Dashboard | `http://localhost:20128/dashboard` (provider health, combos, usage, settings) |
| Zero-config routing | use model id `auto`, `auto/smart`, or `auto/<category>:<tier>` (e.g. `auto/coding:fast`, `auto/reasoning:pro`) |
| Compression header | `x-omniroute-compression: engine:rtk` (or `engine:caveman`, `off`) |
| Internal CLI | `omniroute <subcommand>` (setup, doctor, providers, cost, usage, logs…) |
| Config | env vars + DB feature-flag overrides (NOT a single yaml); secrets in `.env` |
| Logs | enable file logs via env; `omniroute logs`; dashboard Request Logs |

> Verify the port/host if the user runs a non-default deploy (Docker, remote, tunnel).
> `OMNIROUTE_PORT` and reverse-proxy/tunnel setups can change it — see `config-and-env.md`.

## Reference Index — load what your task needs

| File | Load it when you need to… |
|------|---------------------------|
| [`references/auth-and-api.md`](references/auth-and-api.md) | Authenticate; make chat/embedding/image/model-list/TTS/rerank/transcription calls; custom headers; WebSocket/Responses-API streaming; Ollama & headerless aliases; the **dashboard/management REST API** endpoint groups; report quotas/issues. |
| [`references/routing-and-combos.md`](references/routing-and-combos.md) | Understand `auto/` routing, persisted vs virtual combos, the **9-factor scoring system**, mode packs, multi-account, self-healing, emergency fallback, bandit exploration — and **"why was my request routed to model X?"** |
| [`references/combo-strategies.md`](references/combo-strategies.md) | Pick or explain a **routing strategy** (all 17: failover, round-robin, **fusion**, race…); understand **why a request fans out to multiple models**; strategy-selection decision table; recommendations for coding / cheap-bulk / reliability / latency / quality; task fitness & auto variants. |
| [`references/providers.md`](references/providers.md) | Understand the **provider auth-type taxonomy** — **OAuth vs API Key vs Cookie vs Local** — and **why `claude` differs from `claude-web`**; provider counts, free-forever providers, the ~1.6B free-tokens/mo methodology, ToS cautions; how to add/configure a provider. |
| [`references/cli-commands.md`](references/cli-commands.md) | Run the internal `omniroute` CLI (setup, doctor/diagnostics, provider mgmt, recovery/reset, cost/usage); configure external coding-CLI tools (Claude Code, Codex, Cline…) to use OmniRoute. |
| [`references/config-and-env.md`](references/config-and-env.md) | Change **server config**: env vars (secrets, ports, security, timeouts, circuit-breaker thresholds, OAuth creds, proxy, logging, memory), **feature flags** and their resolution order, deployment scenarios. |
| [`references/debugging.md`](references/debugging.md) | Diagnose a failure: rate limits/429s, **circuit breaker OPEN**, OAuth token expired, "fetch failed", cloud/Docker issues, translator errors, resilience tuning; provider/combo **health autopilot** and monitoring. |
| [`references/logs-costs-usage.md`](references/logs-costs-usage.md) | Read **logs**, **cost/spend** tracking (pricing source + formula), **usage/quota** records and enforcement, retention, cost-optimization, the analytics/usage REST + MCP surfaces. |

## Task → File quick map

- *"Why did my request go to model X / why so expensive / why multiple models?"* →
  `routing-and-combos.md` + `combo-strategies.md` (fusion).
- *"A model request failed — why?"* → `debugging.md` (then `routing-and-combos.md` for
  fallback behavior).
- *"OAuth vs API Key vs Cookie? claude vs claude-web?"* → `providers.md`.
- *"How do I call the API / which endpoint?"* → `auth-and-api.md`.
- *"Recommend a combo / strategy / tier."* → `combo-strategies.md` (+ `providers.md` for
  what's free).
- *"Change a setting / flag / timeout / threshold."* → `config-and-env.md`.
- *"What's it costing / how much quota left?"* → `logs-costs-usage.md`.
- *"Run a CLI command / wire up Claude Code."* → `cli-commands.md`.

## Common Pitfalls

1. **Assuming the port.** Default is 20128 but Docker/remote/tunnel deploys remap it.
   Confirm before constructing URLs (`config-and-env.md`).
2. **Confusing provider auth types.** `claude` (OAuth, your Claude subscription) and
   `claude-web` (cookie, claude.ai session) are *different providers with different quota
   pools and ToS risk* — see `providers.md` before advising on either.
3. **Reading a request as "broken" when it's fallback/fusion.** Multiple model calls for
   one request are usually intentional (fusion strategy or self-healing retry), not a bug —
   confirm the combo/strategy in `routing-and-combos.md` before debugging.
4. **Looking for one config file.** OmniRoute config is env vars + DB feature-flag
   overrides with a resolution order, not a single yaml. `.env` is secrets only.
5. **Loading every reference.** This skill is an index; pulling all 8 references defeats the
   point. Match the task to one file via the map above.

## Verification Checklist

- [ ] Confirmed the actual host/port (not blindly 20128) for the user's deploy.
- [ ] Loaded only the reference file(s) the task needs.
- [ ] For routing/cost questions, distinguished **intended** routing (combo/fusion/fallback)
      from an actual **error** before calling something broken.
- [ ] Cross-checked auth-type when a provider has OAuth/API-key/cookie variants.
- [ ] Cited the upstream doc section when the user needs full payloads/spec beyond the
      reference file.
