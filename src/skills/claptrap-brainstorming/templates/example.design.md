<!-- Source: /claptrap-brainstorm -->
<!-- Naming: .claptrap/designs/quota-monitor-plugin/design.md -->

# Design: Quota Monitor Plugin

Date: 2025-01-15

## Intent

A modular plugin for CodeNomad that allows users to see, visualize, and monitor their AI provider subscription usage across multiple providers (OpenAI, Anthropic/Claude, Google Gemini, Cursor, GitHub Copilot). Users need at-a-glance visibility into their quota consumption to avoid unexpected service interruptions.

## Scope

### In Scope
- At-a-glance quota visibility in the existing Status Panel
- Detailed modal dashboard with provider cards and model breakdowns
- Direct API integration for providers with usage APIs (OpenAI, Anthropic, Google)
- CLIProxyAPI integration for providers without APIs (Cursor, Copilot)
- Modular package that can be included/excluded from builds
- On-demand refresh (manual trigger)

### Out of Scope
- Load balancing (CLIProxyAPI feature, not needed)
- Automatic background polling (architecture supports it, not in MVP)
- Usage alerts/notifications
- Historical charts/trends
- Export/reporting
- Multi-account per provider

## Acceptance Criteria

- [ ] User can view quota usage for OpenAI, Anthropic, and Google in Status Panel
- [ ] User can open modal to see detailed per-model breakdown
- [ ] Progress indicators show warning (70-90%) and critical (>90%) states
- [ ] User can configure provider credentials via settings panel
- [ ] Quota data refreshes on-demand via "Refresh" button
- [ ] Plugin can be excluded from build without breaking CodeNomad

## Architecture Overview

### Components
- **QuotaProvider**: Abstract interface for fetching quota from any provider
- **StatusPanelWidget**: Compact quota display for Status Panel
- **QuotaMonitorModal**: Full dashboard with provider cards
- **ProviderCard**: Individual provider display with progress ring
- **QuotaStore**: SolidJS store for quota state management

### Package Structure
```
packages/quota-monitor/
├── src/
│   ├── index.ts                 # Public exports
│   ├── types/                   # Provider, quota, config types
│   ├── providers/               # Provider adapters (openai, anthropic, etc.)
│   ├── auth/                    # OAuth and credential management
│   ├── store/                   # SolidJS store and caching
│   ├── components/              # UI components
│   └── hooks/                   # useQuotaData, useProviderAuth
├── package.json
└── tsconfig.json
```

### Core Types
```typescript
interface QuotaInfo {
  providerId: string
  providerName: string
  quotaLimit: number | null
  quotaUsed: number
  quotaUnit: 'tokens' | 'requests' | 'dollars' | 'credits'
  resetDate: Date | null
  models?: ModelUsage[]
  status: 'ok' | 'warning' | 'critical' | 'error' | 'unknown'
  lastUpdated: Date
}

interface QuotaProvider {
  id: string
  name: string
  isAuthenticated(): Promise<boolean>
  authenticate(): Promise<void>
  fetchQuota(): Promise<QuotaInfo>
}
```

### Data Flow
1. User opens Status Panel or Modal → triggers `useQuotaData` hook
2. Hook checks cache freshness → calls `provider.fetchQuota()` if stale
3. Provider adapter calls external API → transforms to `QuotaInfo`
4. Store updates → UI re-renders with new data

## Key Decisions

| Decision | Options Considered | Choice | Rationale |
|----------|-------------------|--------|-----------|
| Platform target | Electron only, Tauri only, Both | Both | Shared UI in `packages/ui/` makes this feasible |
| Data source | Direct API only, Proxy only, Hybrid | Hybrid | Direct API where available, CLIProxyAPI for Cursor/Copilot |
| UI integration | New tab, Modal overlay, Status Panel only | Status Panel + Modal | Minimal footprint with detail on-demand |
| Authentication | OAuth only, API keys only, Tiered | Tiered | OAuth → Existing config → Manual entry for flexibility |
| Refresh strategy | Auto-polling, On-demand, Hybrid | On-demand (MVP) | Simpler MVP, architecture supports polling later |

## Constraints / Concerns

- Provider APIs may have rate limits that affect refresh frequency
- OAuth flows require platform-specific handling (Electron vs Tauri)
- Cursor and Copilot lack official usage APIs - depends on CLIProxyAPI accuracy
- New code must match existing CodeNomad patterns exactly

## Open Questions

- [ ] What is CLIProxyAPI's exact endpoint format for usage data?
- [ ] Does Google Gemini API support per-model usage breakdown?
- [ ] How should we handle providers with no hard quota limit (pay-as-you-go)?

## OpenSpec Proposals

<!-- Auto-populated by /claptrap-propose -->
- (none yet)
