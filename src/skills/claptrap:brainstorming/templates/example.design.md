# Quota Monitor Plugin Design

## Overview

A modular plugin for CodeNomad that allows users to see, visualize, and monitor their AI provider subscription usage across multiple providers (OpenAI, Anthropic/Claude, Google Gemini, Cursor, GitHub Copilot).

## Goals

- Provide at-a-glance quota visibility in the existing Status Panel
- Offer a detailed modal dashboard with provider cards and model breakdowns
- Support direct API integration for providers with usage APIs (OpenAI, Anthropic, Google)
- Support CLIProxyAPI integration for providers without APIs (Cursor, Copilot)
- Maintain modularity as a separate package that can be included/excluded from builds
- **Match existing codebase patterns** - New code should be indistinguishable from original

## Non-Goals

- Load balancing (CLIProxyAPI feature, not needed)
- Automatic background polling (designed for, not implemented in MVP)
- Usage alerts/notifications
- Historical charts/trends
- Export/reporting
- Multi-account per provider

## Key Decisions

### Platform Target
- Both Electron and Tauri via shared UI in `packages/ui/`

### Data Source Strategy
- Hybrid approach: Direct API polling where available, CLIProxyAPI integration for Cursor/Copilot

### Provider Priority
- MVP: OpenAI, Anthropic, Google Gemini (direct APIs)
- Post-MVP: Cursor, GitHub Copilot (via CLIProxyAPI)

### UI Integration
- Status Panel: Minimal single-row-per-provider with progress bar
- Full View: Modal overlay (not a tab)

### Authentication
- Tiered: OAuth → Existing configs → External config file

### Data Refresh
- On-demand only for MVP, architecture supports future polling

### Modularity
- Separate package: `packages/quota-monitor/`

### Visualization
- Dashboard cards with progress rings, model breakdown expandable

### Proxy Integration
- Integrate with CLIProxyAPI (don't build own proxy)

---

## Development Practices

### Test-Driven Development (TDD)

**All implementation proposals follow TDD principles:**

1. **Tests First** - Unit tests MUST be written BEFORE implementation code
2. **Coverage Focus** - Tests cover main functionality, not exhaustive edge cases
3. **Tests as Specification** - Tests represent the expected final behavior
4. **Code Must Pass** - Implementation is not complete until all tests pass
5. **Minimal Test Modification** - Tests should rarely change unless:
   - A bug is discovered during implementation
   - A feature requirement changes, making the test outdated
6. **Tests Define Success** - The test suite is the source of truth for "done"

Each implementation proposal includes a `## 0. Tests` section at the top of `tasks.md` that must be completed before the implementation tasks.

### Codebase Style Matching

**New plugin code must be indistinguishable from existing CodeNomad code:**

The `research-codenomad-codebase` proposal produces a comprehensive style guide documenting:
- Architecture patterns (layer organization, module boundaries)
- Naming conventions (files, functions, components, types)
- Code style guidelines (imports, exports, formatting, TypeScript patterns)
- Documentation style (JSDoc, comments, tone)

All subsequent implementation must follow this style guide. The goal is that a reader cannot tell which code was original vs. added by this plugin.

---

## Architecture

### Package Structure

```
packages/quota-monitor/
├── src/
│   ├── index.ts                 # Public exports
│   ├── types/
│   │   ├── provider.ts          # Provider interface & types
│   │   ├── quota.ts             # QuotaInfo, UsageStats types
│   │   └── config.ts            # Configuration types
│   ├── providers/
│   │   ├── base.ts              # Abstract base provider
│   │   ├── openai.ts            # OpenAI adapter
│   │   ├── anthropic.ts         # Claude/Anthropic adapter
│   │   ├── google.ts            # Gemini adapter
│   │   └── cli-proxy/           # CLIProxyAPI integration
│   │       ├── client.ts        # API client for CLIProxyAPI
│   │       ├── cursor.ts        # Cursor via proxy
│   │       └── copilot.ts       # Copilot via proxy
│   ├── auth/
│   │   ├── oauth.ts             # OAuth flow handling
│   │   ├── credentials.ts       # Credential storage/retrieval
│   │   └── config-file.ts       # External config file reader
│   ├── store/
│   │   ├── quota-store.ts       # SolidJS store for quota data
│   │   └── cache.ts             # Caching layer
│   ├── components/
│   │   ├── StatusPanelWidget.tsx    # Minimal row for Status Panel
│   │   ├── QuotaMonitorModal.tsx    # Full modal view
│   │   ├── ProviderCard.tsx         # Individual provider card
│   │   ├── ProgressRing.tsx         # Circular progress indicator
│   │   └── SettingsPanel.tsx        # Provider configuration
│   └── hooks/
│       ├── useQuotaData.ts      # Hook for accessing quota data
│       └── useProviderAuth.ts   # Hook for auth state
├── package.json
└── tsconfig.json
```

### Integration with Main UI

The package imports from `packages/ui/` for consistency:
- Design tokens (colors, spacing, typography)
- Utility classes (Tailwind)
- Base components (buttons, modals, accordions)
- Typography component
- Icons and layout primitives

### Core Types

```typescript
interface QuotaInfo {
  providerId: string
  providerName: string
  providerIcon: string
  
  // Quota limits
  quotaLimit: number | null
  quotaUsed: number
  quotaRemaining: number | null
  quotaUnit: 'tokens' | 'requests' | 'dollars' | 'credits'
  
  // Reset timing
  resetDate: Date | null
  resetIntervalDays: number | null
  
  // Token breakdown
  tokens?: {
    input: number
    output: number
    total: number
  }
  
  // Cost
  cost?: {
    current: number
    limit: number | null
    currency: string
  }
  
  // Model breakdown
  models?: ModelUsage[]
  
  // Status
  status: 'ok' | 'warning' | 'critical' | 'error' | 'unknown'
  statusMessage?: string
  lastUpdated: Date
}

interface ModelUsage {
  modelId: string
  modelName: string
  tokens: { input: number; output: number; total: number }
  cost?: number
  requestCount?: number
  percentOfTotal: number
}

interface QuotaProvider {
  id: string
  name: string
  icon: string
  
  isAuthenticated(): Promise<boolean>
  authenticate(): Promise<void>
  fetchQuota(): Promise<QuotaInfo>
  
  capabilities: {
    hasTokenBreakdown: boolean
    hasCostTracking: boolean
    hasResetSchedule: boolean
    supportsOAuth: boolean
  }
}
```

### Status Thresholds
- `ok` - Under 70% usage
- `warning` - 70-90% usage
- `critical` - Over 90% usage
- `error` - Failed to fetch / auth issue
- `unknown` - Never fetched

## UI Design

### Status Panel Widget

Minimal accordion section in existing Status Panel:
- One line per configured provider
- Compact progress bar with percentage
- Status icon (✓ ok, ⚠️ warning, 🔴 critical)
- "View Details" link opens modal

### Quota Monitor Modal

Full dashboard with:
- Card per provider with progress ring
- Primary stat (tokens or cost) prominently displayed
- Reset countdown
- Expandable model breakdown (sorted by usage)
- Settings gear for provider config
- Unconfigured providers show setup prompt
- "Refresh All" button
- "Last refreshed" timestamp

### Provider Card with Model Expansion

Each card shows:
- Provider name and logo
- Progress ring with percentage
- Primary metric (quota used / limit)
- Reset countdown
- Expandable "Models" section with per-model breakdown

## Authentication

### Tier 1: OAuth
- Google Gemini via Google OAuth
- GitHub Copilot via GitHub OAuth (future)

### Tier 2: Existing Config Detection
- OpenCode's provider config
- Environment variables

### Tier 3: Manual / Config File
- API key entry
- Save to `~/.config/codenomad/quota-monitor.json`
- Platform keychain for secure storage

## CLIProxyAPI Integration

For Cursor and GitHub Copilot (Phase 3):

### Integration Points
- Discovery: Detect if CLIProxyAPI is running
- Data retrieval: Fetch usage stats from proxy API
- Format: TBD during CLIProxyAPI research

### Cursor Specifics
- User configures plan limits (fast requests per month)
- Proxy tracks actual usage
- Calculate percentage against user-configured limits
- Track both fast and slow requests

## State Management

SolidJS store pattern:
- `providers[]` - Configured providers
- `data{}` - Quota data keyed by provider ID
- `fetching{}` - Loading state per provider
- `errors{}` - Error state per provider
- `lastFetched{}` - Cache timestamps

Actions:
- `refreshProvider(id)` - Fetch single provider
- `refreshAll()` - Fetch all providers
- `configureProvider(config)` - Add/update provider config

---

## OpenSpec Proposals

Ordered by recommended execution sequence, grouped by phase.

### Phase 1: Research

| # | Proposal | Description |
|---|----------|-------------|
| 1 | `research-codenomad-codebase` | Analyze CodeNomad for integration points AND coding patterns/style guide |
| 2 | `research-cliproxyapi` | Document CLIProxyAPI features and integration approach |
| 3 | `research-quotio-features` | Map Quotio features to replicate/skip/improve |

**Outputs:**
- `.workflow/research/codenomad-analysis.md` - Integration guidance
- `.workflow/research/codenomad-style-guide.md` - Patterns and style guide
- `.workflow/research/cliproxyapi-analysis.md` - CLIProxyAPI integration guide
- `.workflow/research/quotio-feature-mapping.md` - Feature comparison

### Phase 2: Foundation

| # | Proposal | Description |
|---|----------|-------------|
| 4 | `scaffold-quota-monitor-package` | Create package structure and build config |
| 5 | `add-provider-abstraction-layer` | Design provider interface and base adapter |
| 6 | `add-authentication-system` | OAuth flows and credential management |
| 7 | `add-data-layer-infrastructure` | Caching, storage, refresh infrastructure |

### Phase 3: MVP Implementation

| # | Proposal | Description |
|---|----------|-------------|
| 8 | `add-direct-api-providers` | OpenAI, Anthropic, Google adapters |
| 9 | `add-status-panel-widget` | Minimal quota indicators in Status Panel |
| 10 | `add-quota-monitor-modal` | Full dashboard UI with cards |
| 11 | `add-settings-configuration-ui` | Provider setup and auth management |

### Phase 4: Post-MVP (CLIProxyAPI)

| # | Proposal | Description |
|---|----------|-------------|
| 12 | `add-cliproxyapi-integration` | Read usage from CLIProxyAPI |
| 13 | `add-cursor-copilot-providers` | Provider adapters via proxy |

---

## Research Outputs

Research proposals produce documentation that guides implementation:

| Document | Purpose |
|----------|---------|
| `codenomad-analysis.md` | How to integrate with CodeNomad (packages, Status Panel, modals) |
| `codenomad-style-guide.md` | Coding patterns to match (naming, style, architecture, documentation) |
| `cliproxyapi-analysis.md` | How to connect to and read from CLIProxyAPI |
| `quotio-feature-mapping.md` | What features to build, skip, or improve |
