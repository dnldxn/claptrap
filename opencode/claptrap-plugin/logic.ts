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

export const HARVESTER_THRESHOLD = 5
export const MUTATING_TOOLS = ["edit", "write", "patch", "bash"]
export const RECALL_REMINDER = "<system-reminder>No mnemosyne_recall yet this session — recall relevant memories before continuing, or state why this task needs no prior context.</system-reminder>"
export function isMutatingTool(tool: string) {
  return MUTATING_TOOLS.includes(tool.toLowerCase())
}

export type GateState = {
  recalled: boolean
  mutated: boolean
  warnedRecall: boolean
  storedMemory: boolean
  warnedStore: boolean
  counter: number
  watermark: number
}

export function newGateState(): GateState {
  return {
    recalled: false,
    mutated: false,
    warnedRecall: false,
    storedMemory: false,
    warnedStore: false,
    counter: 0,
    watermark: 0,
  }
}

export function applyToolToGate(
  state: GateState,
  tool: string,
): { state: GateState; warnRecall: boolean } {
  const tracked = classifyToolCall({ tool })
  const mutating = isMutatingTool(tool)
  const warnRecall = mutating && !state.recalled && !state.warnedRecall

  return {
    warnRecall,
    state: {
      ...state,
      recalled: state.recalled || tracked?.event === "memory_recalled",
      storedMemory: state.storedMemory || tracked?.event === "memory_stored",
      mutated: state.mutated || mutating,
      warnedRecall: state.warnedRecall || warnRecall,
      counter: state.counter + (mutating || tracked ? 1 : 0),
    },
  }
}

export function shouldWarnStore(state: GateState) {
  return state.mutated && !state.storedMemory && !state.warnedStore
}

export function shouldRunHarvester(counter: number, watermark: number, live: boolean) {
  return !live && counter - watermark >= HARVESTER_THRESHOLD
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

/** Lock-dir facts. `pidAlive` is undefined when the run recorded no pid (older
 *  runs, or the lock dir was created but the wrapper never started). */
export type LockState = {
  present: boolean
  mtimeMs?: number
  pidAlive?: boolean
}

/** A gardener is running only if its process is. The lock file alone is not
 *  proof: a SIGKILLed run never reaches its cleanup, so the lock outlives it.
 *  Falls back to lock age only when no pid was recorded. */
export function isGardenerLive(lock: LockState, now = Date.now()) {
  if (!lock.present) return false
  if (lock.pidAlive !== undefined) return lock.pidAlive
  return !isLockStale(lock.mtimeMs ?? 0, now)
}

/** True when a start has no matching terminal event and its process is gone —
 *  i.e. the run was killed before its shell could record the outcome. */
export function needsFailureBackfill(events: EventRecord[], live: boolean, prefix = "gardener") {
  if (live) return false
  const start = newest(events, [`${prefix}_started`])
  if (!start) return false
  const result = newest(events, [`${prefix}_completed`, `${prefix}_failed`])
  return !result || eventTime(result) < eventTime(start)
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

export type StatusInput = {
  events: EventRecord[]
  summaryText: string
  harvesterSummaryText: string
  running: boolean
  harvesterRunning: boolean
  skillCounts: { active: number; archived: number }
  now?: number
}

export function buildStatusReport(input: StatusInput) {
  const {
    events,
    summaryText,
    harvesterSummaryText,
    running,
    harvesterRunning,
    skillCounts,
    now = Date.now(),
  } = input
  const lastSuccess = newest(events, ["gardener_completed"])
  const lastResult = newest(events, ["gardener_completed", "gardener_failed"])
  const harvesterResult = newest(events, ["harvester_completed", "harvester_failed"])
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
    .filter((event) => !["project_seen", "gardener_result_notified", "harvester_result_notified"].includes(event.event))
    .sort((a, b) => eventTime(b) - eventTime(a))
    .slice(0, 10)
  const recentText = recent.length
    ? recent.map((event) => `- ${event.event.replaceAll("_", " ")}${typeof event.name === "string" ? ` ${event.name}` : ""}`).join("\n")
    : "- none"
  const mostLoadedText = mostLoaded.length
    ? mostLoaded.map(([name, count], index) => `${index + 1}. ${name} — ${count} loads`).join("\n")
    : "- none"
  const resultText = summaryText.trim() || "not available"
  const harvesterResultText = harvesterResult?.event === "harvester_failed"
    ? "failed; check harvester.log"
    : harvesterSummaryText.trim() || "not available"
  // Child runs stamp their agent name on every event, so the harvester's own
  // skill writes are separable from the main agent's.
  const harvesterSkills7 = last7.filter(
    (event) => event.event === "managed_skill_changed" && event.agent === "ct-skill-harvester",
  ).length
  const gateCounts = (window: EventRecord[], name: string) => window.filter((event) => event.event === name).length

  return `# Claptrap status

Gardener
- Last successful run: ${formatTime(lastSuccess ? eventTime(lastSuccess) : undefined)}
- Next due: ${formatTime(lastSuccess ? eventTime(lastSuccess) + WEEK_MS : now)}
- Running: ${running ? "yes" : "no"}
- Last result: ${lastResult?.event === "gardener_failed" ? "failed; check gardener.log" : resultText}

Skill-harvester
- Last run: ${formatTime(harvesterResult ? eventTime(harvesterResult) : undefined)}
- Running: ${harvesterRunning ? "yes" : "no"}
- Runs (7d): ${last7.filter((event) => event.event === "harvester_started").length}
- Skills created/updated (7d): ${harvesterSkills7}
- Last result: ${harvesterResultText}

Managed Skills
- Active: ${skillCounts.active}
- Archived: ${skillCounts.archived}

Last 7 days
- Skill loads: ${last7.filter((event) => event.event === "skill_loaded").length}
- Mnemosyne recalls: ${last7.filter((event) => event.event === "memory_recalled").length}
- Mnemosyne stores: ${last7.filter((event) => event.event === "memory_stored").length}
- Managed-Skill changes: ${last7.filter((event) => event.event === "managed_skill_changed").length}
- Recall-gate warnings: ${gateCounts(last7, "gate_recall_warned")}
- Store-gate warnings: ${gateCounts(last7, "gate_store_warned")}

Last 30 days
- Skill loads: ${loads.length}
- Mnemosyne recalls: ${last30.filter((event) => event.event === "memory_recalled").length}
- Mnemosyne stores: ${last30.filter((event) => event.event === "memory_stored").length}
- Managed-Skill changes: ${last30.filter((event) => event.event === "managed_skill_changed").length}
- Recall-gate warnings: ${gateCounts(last30, "gate_recall_warned")}
- Store-gate warnings: ${gateCounts(last30, "gate_store_warned")}

Most-loaded Skills
${mostLoadedText}

Recent activity
${recentText}
`
}
