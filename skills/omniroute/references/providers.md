# OmniRoute Providers & Auth-Type Taxonomy

> OmniRoute aggregates **231 providers** (50+ with free tiers) across nine auth categories. The single most important distinction is the **credential type**: OAuth vs API Key vs Web Cookie vs Local — the *same* underlying model (e.g. Claude) is reachable through different provider IDs that draw on *different quota pools*.

**When you need this file:** picking/adding a provider, understanding why `claude` ≠ `claude-web` ≠ `anthropic`, decoding a provider-id suffix (`-web`, `-cli`, `-cn`), answering "how many providers / how many free", citing the ~1.6B free-token budget, or checking ToS caution before relying on a free tier.

---

## The headline: auth-type taxonomy

A provider's **category determines what credential you supply and which quota pool you spend.** Totals from `docs/reference/PROVIDER_REFERENCE.md §Categories (L15)`.

| Category | Count | Credential you supply | Cost model | Key tradeoffs |
|---|---|---|---|---|
| **OAuth** | 19 | Sign-in flow handled by OmniRoute (login popup / imported token). **No API key.** | A subscription you already pay (Claude/Copilot/Cursor plans) | Reuses existing sub quota; tokens **expire & must refresh**; several ToS prohibit third-party/proxy use |
| **Web Cookie** | 22 | Session cookie(s) copied from the provider's web app via browser DevTools | **$0 marginal** — rides your web account (free or Plus/Pro) | Most **fragile**: cookies expire, anti-bot (Cloudflare Turnstile) challenges, TLS-fingerprint spoofing; **highest ToS risk**; manual re-paste |
| **API Key** | 157 | An API key/token pasted into the dashboard | Pay-per-token (many ship **free credits / free tiers**) | Most **stable & official**; predictable; you spend real money or burn free credits |
| **Local** | 11 | None, or optional key + a local base URL | **$0** — your own hardware | Private/offline/unlimited; you must run Ollama, LM Studio, vLLM, llama.cpp, etc.; quality bound by your GPU |
| **Search** | 11 | API key (web-search APIs) | Free tier / paid | Web search, **not** chat — Brave, Exa, Tavily, Serper, You.com… |
| **Audio-only** | 7 | API key | Pay-per-use | TTS/STT only — ElevenLabs, Deepgram, AssemblyAI, Cartesia… |
| **Upstream Proxy** | 2 | Upstream config | Varies | Proxy to *other* provider stacks (`9router`, `cliproxyapi`) |
| **Cloud Agent** | 3 | API key | Pay-per-task | Long-running coding agents — Codex Cloud, Devin, Jules |
| **System** | 1 | None | — | OmniRoute-internal `auto` zero-config router |

> Counts sum to 233, but the **total is 231** — `huggingchat` and `phind` are listed in *two* categories each (a web-cookie flavor and an API-key flavor). That overlap is the taxonomy itself in miniature: one brand, multiple auth flavors. See `docs/reference/PROVIDER_REFERENCE.md` (full per-ID tables at L34/L58/L85/L247…).

Enable, configure, and test every provider from the dashboard at **`/dashboard/providers`**.

---

## Same model, different provider: OAuth vs API Key vs Cookie

The canonical example is **Claude**, reachable three ways — each a *separate provider ID drawing on a separate quota bucket*:

| Provider ID | Alias | Category | Draws on… | Cost | ToS risk | Setup friction |
|---|---|---|---|---|---|---|
| `claude` | `cc` | **OAuth** ("Claude Code") | Your Claude **subscription** (Pro/Max) via OAuth login | Flat monthly sub, $0/token | Medium — Claude Code ToS frowns on third-party harness/proxy use | Low — one OAuth login (token auto-refreshes) |
| `claude-web` | `cw` | **Web Cookie** ("Claude Web") | Your **claude.ai web session** (free or Plus/Pro web quota) | $0 marginal | **High** — automated access to the consumer web app | **High** — copy cookies from DevTools, re-paste on expiry |
| `anthropic` | — | **API Key** | Prepaid **API credits** at platform.claude.com | Pay-per-token | **Low** — the officially supported path | Low — paste one key |

**Why choose one over the other:**

- **Pick `claude` (OAuth)** if you already pay for a Claude subscription and want $0-marginal usage with minimal setup — you're spending sub quota, not API dollars. Watch for subscription rate caps and occasional token-refresh prompts.
- **Pick `claude-web` (Cookie)** only to tap a web account's quota with no API spend — but accept fragility and ToS exposure. Cookies break often; it exists for squeezing the consumer web tier.
- **Pick `anthropic` (API Key)** for production stability, predictable billing, and the lowest ToS risk. You pay per token but nothing breaks on a cookie refresh.

**The quota-pool insight:** these three buckets are *independent*. Configuring all three multiplies your effective Claude access (subscription + web session + API credits) and lets auto-routing fail over between them — see **routing-and-combos.md**.

### claude-web cookie mechanics

From `docs/PROVIDERS.md §How It Works (L7) / §Required Cookies (L14)`. You paste your full `claude.ai` cookie header; `ClaudeWebExecutor` rewrites OpenAI-format requests into Claude's web API and ships them via **`tls-client-node` spoofing a Chrome 124 TLS fingerprint** to clear Cloudflare Turnstile, then streams SSE back.

| Cookie | Purpose | Source |
|---|---|---|
| `sessionKey` | Main authentication | claude.ai browser session |
| `routingHint` | Anthropic routing | claude.ai browser session |
| `cf_clearance` | Cloudflare Turnstile clearance | auto-set after challenge — **bound to the TLS fingerprint** that solved it |
| `__cf_bm` | Cloudflare bot management | auto-set by Cloudflare |
| `_cfuvid` | Cloudflare visitor ID | auto-set by Cloudflare |

Endpoint: `POST /api/organizations/{orgId}/chat_conversations/{convId}/completion` with headers `anthropic-client-platform: web_claude_ai` + a generated `anthropic-device-id`. Because `cf_clearance` is fingerprint-bound, the server must replay the same Chrome-124 handshake — that's the whole reason cookie providers are brittle.

### Generalize: the provider-id suffix signals credential + quota pool

Many brands ship in multiple flavors; **the ID/suffix tells you which credential and which bucket:**

- **`-web`** → Web Cookie, rides the consumer web app: `gemini-web`, `qwen-web`, `deepseek-web`, `chatgpt-web`, `grok-web`, `perplexity-web`, `poe-web`, `kimi-web`, `doubao-web`.
- **`-cli` / bare OAuth IDs** → OAuth, rides a subscription/CLI login: `gemini-cli`, `claude`(`cc`), `codex`, `github`, `cursor`, `cline`.
- **bare brand name** → usually API Key: `gemini`, `anthropic`, `openai`, `xai`, `deepseek`, `kimi`, `glm`.
- **`-cn`** → China-region endpoint of the same API: `alibaba-cn`, `minimax-cn`, `glm-cn`.
- **`-coding` / `-coding-plan`** → a coding-subscription pool: `kimi-coding`, `bailian-coding-plan`.

Worked examples of one brand × three credentials:

- **Claude** — `claude` (OAuth) · `claude-web` (cookie) · `anthropic` (API key)
- **Gemini** — `gemini-cli` (OAuth) · `gemini-web` / `gemini-business` (cookie, free/enterprise) · `gemini` (API key)
- **OpenAI/ChatGPT** — `codex` (OAuth) · `chatgpt-web` (cookie) · `openai` (API key)
- **Qwen** — `qwen` (OAuth, ⚠️ deprecated) · `qwen-web` (cookie) · `alibaba` / `bailian-coding-plan` (API key)
- **Grok** — `grok-web` (cookie) · `xai` (API key)

---

## How many providers? How many free?

- **231 total** providers (`docs/reference/PROVIDER_REFERENCE.md` header). The bundled getting-started guide still says "226" — treat the reference as canonical.
- **50+ have free tiers**; `docs/reference/FREE_TIERS.md` counts **40+ documented free-tier pools** plus a long tail of keyless/uncapped ones.

**"Free forever" (no-credit-card, recurring) standouts** — best starting set (from `PROVIDERS-GUIDE.md` + FREE_TIERS):

- **Kiro** (50 credits/mo, Claude models, ⚠️ ToS), **Pollinations** (keyless GPT-5/Claude/Gemini), **Cloudflare AI** (~10K Neurons/day, 50+ models), **LongCat** (~5M tokens/day), **Cerebras** (1M tokens/day), **Groq** (30 RPM), **NVIDIA NIM** (~40 RPM, 70+ models), **Gemini** (Flash family, free key).
- **Permanently free but uncapped** (real recurring access, rate-limited, *no token cap to count*): `siliconflow`, `glm-cn` (GLM-4-Flash), `tencent`, `baidu`, `kilo-gateway`, `opencode-zen` — see `docs/reference/FREE_TIERS.md §Methodology (L49)`.

### Where the ~1.6B free-tokens/month number comes from

`docs/reference/FREE_TIERS.md §TL;DR (L14)` and §Methodology (L49): the budget is the sum of each provider's **documented recurring monthly token cap**, with each shared pool counted **once** (pool-deduped) and **one-time signup credits excluded** (they count as 0 because they don't recur). Daily caps are ×30; RPD-only tiers use `RPD × ~800 tokens × 30`; rate-limit-only providers with no published cap are deliberately **not summed** (multiplying RPM×24/7 is the inflation OmniRoute rejects). That yields **~1.54B documented recurring tokens/mo (headline ~1.6B)**, rising to **~2.15B in your first month** once signup credits (Together $25, Z.AI 20M, DeepSeek 5M…) are added. Biggest documented contributors: `mistral` 1.00B, `llm7` 150M, `longcat` 150M, `groq` 117M, `gemini` 60M, `cerebras`/`cloudflare-ai`/`sambanova` ~30M each. The live source is the per-model catalog behind `/api/free-tier/summary`; figures are **upper-bound estimates** that change constantly.

### ToS cautions (summary — do not rely blindly)

`docs/reference/FREE_TIERS.md §Caution personal-use/proxy clauses (L64)` flags **19 providers** whose terms warrant a glance before you route a self-hosted proxy through them. The pattern:

- **Consumer OAuth/cookie tiers** often explicitly ban third-party/proxy/harness access: `agy` (Antigravity), `gemini-cli`, `kiro`, `qwen-web`, `t3-web`, `muse-spark-web`, `amazon-q`.
- **API-key providers** often forbid reselling/sublicensing/standalone proxying: `fireworks`, `friendliai`, `modal`, `nlpcloud`, `blackbox`, `coze`, `featherless-ai`, `ai21`, `iflytek`, `opencode`.

Access is real and OmniRoute *can* route to them — these are personal-use/proxy clauses worth knowing, **not legal advice**. The OAuth/keyless ones aren't token-quantifiable, so they're excluded from the headline budget. Most providers (Scaleway, SearXNG, ComfyUI, SD WebUI, DeepSeek, Hyperbolic, Morph…) are rated `ok` or `ambiguous`.

---

## Adding / configuring a provider

1. **Dashboard** (easiest): `/dashboard/providers` → **Add Provider** → pick it → supply the credential for its category:
   - *Free*: just **Connect** (no creds).
   - *API key*: paste the key.
   - *OAuth*: **Connect with OAuth** → log in (token auto-managed).
   - *Web cookie*: paste the cookie header from DevTools.
   - *Local*: set the base URL (e.g. `http://localhost:11434/v1`).
   Then **Test Connection**.
2. **CLI**: provider enable/list/test commands — see **cli-commands.md**.
3. **Env / credentials**: OAuth client IDs/secrets and provider keys via environment — see **config-and-env.md** (OAuth credential env vars, §11/§14) for `GITLAB_DUO_OAUTH_CLIENT_ID`, `WINDSURF_API_KEY`, and the standard `*_API_KEY` pattern.

Once 2+ providers are live, use `model: "auto"` and OmniRoute fails over / cost-optimizes across them.

---

## See also

- **routing-and-combos.md** — how auto-routing picks among providers / quota pools and fails over.
- **config-and-env.md** — OAuth credential env vars and provider key configuration (§11/§14).
- **cli-commands.md** — provider management commands.
- **debugging.md** — "OAuth token expired", cookie breakage, provider health checks.
- **auth-and-api.md** — OmniRoute's own API auth (distinct from upstream provider auth).
- Upstream: `docs/reference/PROVIDER_REFERENCE.md` (full per-ID tables), `docs/PROVIDERS.md` (claude-web deep-dive), `docs/reference/FREE_TIERS.md` (per-provider free tiers + ToS table).
