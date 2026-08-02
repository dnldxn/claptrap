export const WEEK_MS = 7 * 24 * 60 * 60 * 1000
export const STALE_LOCK_MS = 12 * 60 * 60 * 1000
export const MEMORY_TOOL_PREFIXES = ["mnemosyne_", "mcp__mnemosyne__"]
const DAY_MS = 24 * 60 * 60 * 1000

export type EventRecord = {
  event: string
  ts: string | number
  [key: string]: unknown
}

export type ToolInput = { tool: string; args?: Record<string, unknown>; sessionID?: string }
export type TrackedEvent = {
  event: "skill_loaded" | "memory_recalled" | "memory_stored" | "memory_other" | "managed_skill_changed"
  name?: string
  tool?: string
  session_id?: string
}

function eventTime(event: EventRecord) {
  const value = typeof event.ts === "number" ? event.ts : Date.parse(String(event.ts))
  return Number.isFinite(value) ? value : 0
}

export function classifyToolCall(input: ToolInput): TrackedEvent | undefined {
  if (input.tool === "skill") {
    const name = input.args?.name ?? input.args?.skill
    return { event: "skill_loaded", ...(typeof name === "string" ? { name } : {}) }
  }

  const lower = input.tool.toLowerCase()
  if (!MEMORY_TOOL_PREFIXES.some((prefix) => lower.startsWith(prefix))) return undefined
  if (/recall|search|retrieve|query|context/.test(lower)) {
    return { event: "memory_recalled", tool: input.tool }
  }
  if (/remember|store|record|add|write/.test(lower)) {
    return { event: "memory_stored", tool: input.tool }
  }
  return { event: "memory_other", tool: input.tool }
}

export function classifyManagedSkillEdit(filePath: string):
  | { event: "managed_skill_changed"; name: string }
  | undefined {
  const path = filePath.replaceAll("\\", "/")
  const match = path.match(/(?:^|\/)skills(?:-archive)?\/claptrap\/(ct-[^/]+)\/SKILL\.md$/)
  return match ? { event: "managed_skill_changed", name: match[1] } : undefined
}

export function isGardenerDue(events: EventRecord[], now = Date.now()) {
  return !events.some((event) => {
    if (event.event !== "gardener_completed") return false
    const age = now - eventTime(event)
    return age >= 0 && age <= WEEK_MS
  })
}

export function isLockStale(lockMtimeMs: number, now = Date.now()) {
  return now - lockMtimeMs > STALE_LOCK_MS
}

function formatTime(value: number | undefined) {
  return value === undefined ? "never" : new Date(value).toISOString().replace("T", " ").replace(".000Z", " UTC")
}

function newest(events: EventRecord[], names: string[]) {
  return events
    .filter((event) => names.includes(event.event))
    .sort((a, b) => eventTime(b) - eventTime(a))[0]
}

function eventsSince(events: EventRecord[], now: number, age: number) {
  return events.filter((event) => {
    const eventAge = now - eventTime(event)
    return eventAge >= 0 && eventAge <= age
  })
}

export function buildStatusReport(
  events: EventRecord[],
  summaryText: string,
  lockPresent: boolean,
  skillCounts: { active: number; archived: number },
  now = Date.now(),
) {
  const lastSuccess = newest(events, ["gardener_completed"])
  const lastResult = newest(events, ["gardener_completed", "gardener_failed"])
  const last30 = eventsSince(events, now, 30 * DAY_MS)
  const last7 = eventsSince(events, now, WEEK_MS)
  const loads = last30.filter((event) => event.event === "skill_loaded")
  const loadCounts = new Map<string, number>()
  for (const event of loads) {
    if (typeof event.name === "string") loadCounts.set(event.name, (loadCounts.get(event.name) ?? 0) + 1)
  }
  const mostLoaded = [...loadCounts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 3)
  const recent = events
    .filter((event) => !["project_seen", "gardener_result_notified"].includes(event.event))
    .sort((a, b) => eventTime(b) - eventTime(a))
    .slice(0, 10)
  const recentText = recent.length
    ? recent.map((event) => `- ${event.event.replaceAll("_", " ")}${typeof event.name === "string" ? ` ${event.name}` : ""}`).join("\n")
    : "- none"
  const mostLoadedText = mostLoaded.length
    ? mostLoaded.map(([name, count], index) => `${index + 1}. ${name} — ${count} loads`).join("\n")
    : "- none"
  const resultText = summaryText.trim() || "not available"

  return `# Claptrap status

Gardener
- Last successful run: ${formatTime(lastSuccess ? eventTime(lastSuccess) : undefined)}
- Next due: ${formatTime(lastSuccess ? eventTime(lastSuccess) + WEEK_MS : now)}
- Running: ${lockPresent ? "yes" : "no"}
- Last result: ${lastResult?.event === "gardener_failed" ? "failed; check gardener.log" : resultText}

Managed Skills
- Active: ${skillCounts.active}
- Archived: ${skillCounts.archived}

Last 7 days
- Skill loads: ${last7.filter((event) => event.event === "skill_loaded").length}
- Mnemosyne recalls: ${last7.filter((event) => event.event === "memory_recalled").length}
- Mnemosyne stores: ${last7.filter((event) => event.event === "memory_stored").length}
- Managed-Skill changes: ${last7.filter((event) => event.event === "managed_skill_changed").length}

Last 30 days
- Skill loads: ${loads.length}
- Mnemosyne recalls: ${last30.filter((event) => event.event === "memory_recalled").length}
- Mnemosyne stores: ${last30.filter((event) => event.event === "memory_stored").length}
- Managed-Skill changes: ${last30.filter((event) => event.event === "managed_skill_changed").length}

Most-loaded Skills
${mostLoadedText}

Recent activity
${recentText}
`
}
