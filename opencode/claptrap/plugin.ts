import { type Plugin, type PluginInput, tool } from "@opencode-ai/plugin"
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync } from "node:fs"
import { spawn } from "node:child_process"
import { homedir } from "node:os"
import { join } from "node:path"
import {
  applyToolToGate,
  buildStatusReport,
  classifyManagedSkillEdit,
  classifyToolCall,
  isGardenerDue,
  isGardenerLive,
  newGateState,
  needsFailureBackfill,
  RECALL_REMINDER,
  shouldRunHarvester,
  shouldWarnStore,
  type GateState,
  type TrackedEvent,
  type EventRecord,
} from "./logic"

const STATE_DIR = join(homedir(), ".local/state/claptrap")
const CHILD_ENV = "CLAPTRAP_AGENT_CHILD"

const EVENTS_FILE = join(STATE_DIR, "events.jsonl")
type AgentRun = {
  agent: string
  prefix: "gardener" | "harvester"
  lockDir: string
  pidFile: string
  logFile: string
  summaryFile: string
  toasts: { started: string; completed: string; failed: string }
}

function agentRun(agent: string, prefix: AgentRun["prefix"], label: string): AgentRun {
  const lockDir = join(STATE_DIR, `${prefix}.lock`)
  return {
    agent,
    prefix,
    lockDir,
    pidFile: join(lockDir, "pid"),
    logFile: join(STATE_DIR, `${prefix}.log`),
    summaryFile: join(STATE_DIR, `last-${prefix}-summary.md`),
    toasts: {
      started: `CT: ${label} started in background`,
      completed: `CT: ${label} completed; run /ct-status`,
      failed: `CT: ${label} failed; check ${prefix}.log`,
    },
  }
}

const GARDENER = agentRun("ct-gardener", "gardener", "weekly gardener")
const HARVESTER = agentRun("ct-skill-harvester", "harvester", "skill-harvester")
type PluginContext = PluginInput

function timestamp() {
  return new Date().toISOString()
}

function ensureStateDirectory() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function appendEvent(event: Omit<EventRecord, "ts">) {
  ensureStateDirectory()
  const agent = process.env[CHILD_ENV]
  appendFileSync(EVENTS_FILE, `${JSON.stringify({ ts: timestamp(), ...(agent ? { agent } : {}), ...event })}\n`)
}

function readEvents(): EventRecord[] {
  if (!existsSync(EVENTS_FILE)) return []
  return readFileSync(EVENTS_FILE, "utf8")
    .split("\n")
    .filter(Boolean)
    .flatMap((line) => {
      try {
        const value = JSON.parse(line)
        return value && typeof value === "object" ? [value as EventRecord] : []
      } catch {
        return []
      }
    })
}

function eventTime(event: EventRecord) {
  const value = typeof event.ts === "number" ? event.ts : Date.parse(String(event.ts))
  return Number.isFinite(value) ? value : 0
}

function newest(events: EventRecord[], names: string[]) {
  return events
    .filter((event) => names.includes(event.event))
    .sort((a, b) => eventTime(b) - eventTime(a))[0]
}

function projectFor(ctx: PluginContext) {
  return ctx.worktree || ctx.directory
}

function toastMessage(tracked: TrackedEvent) {
  if (tracked.event === "skill_loaded") return `CT: loaded Skill ${tracked.name ?? "(unnamed)"}`
  if (tracked.event === "memory_recalled") return "CT: recalled Mnemosyne memory"
  if (tracked.event === "memory_stored") return "CT: stored Mnemosyne memory"
  if (tracked.event === "memory_other") return `CT: used Mnemosyne tool ${tracked.tool ?? "(unknown)"}`
  return `CT: changed managed Skill ${tracked.name ?? "(unknown)"}`
}

async function recordAndNotify(ctx: PluginContext, tracked: TrackedEvent) {
  const event: Record<string, unknown> = {
    event: tracked.event,
    project: projectFor(ctx),
    ...(tracked.name ? { name: tracked.name } : {}),
    ...(tracked.tool ? { tool: tracked.tool } : {}),
    ...(tracked.session_id ? { session_id: tracked.session_id } : {}),
  }
  appendEvent(event as Omit<EventRecord, "ts">)
  await ctx.client.app.log({
    body: { service: "claptrap", level: "info", message: toastMessage(tracked), extra: { event: tracked.event } },
  })
  try {
    await ctx.client.tui.showToast({ body: { message: toastMessage(tracked), variant: "info", duration: 3000 } })
  } catch {
    // Detached `opencode run` processes do not always have a TUI.
  }
}

function agentToast(ctx: PluginContext, run: AgentRun, kind: "started" | "completed" | "failed") {
  const event = `${run.prefix}_${kind}`
  const message = run.toasts[kind]
  void ctx.client.app.log({ body: { service: "claptrap", level: "info", message, extra: { event } } })
  void ctx.client.tui.showToast({ body: { message, variant: "info", duration: 3000 } }).catch(() => {
    // A detached run may not have a TUI.
  })
}

function gateToast(ctx: PluginContext, message: string) {
  void ctx.client.app.log({ body: { service: "claptrap", level: "info", message, extra: { event: "gate" } } })
  void ctx.client.tui.showToast({ body: { message, variant: "warning", duration: 3000 } }).catch(() => {
    // A detached run may not have a TUI.
  })
}

function shellQuote(value: string) {
  return `'${value.replaceAll("'", "'\\''")}'`
}

function processAlive(pid: number) {
  try {
    // Signal 0 checks for existence without delivering anything.
    process.kill(pid, 0)
    return true
  } catch (error) {
    // EPERM means the process exists but is owned by someone else.
    return (error as NodeJS.ErrnoException)?.code === "EPERM"
  }
}

function readLockState(run: AgentRun) {
  if (!existsSync(run.lockDir)) return { present: false }
  let mtimeMs: number | undefined
  try {
    mtimeMs = statSync(run.lockDir).mtimeMs
  } catch {
    mtimeMs = undefined
  }
  try {
    const pid = Number.parseInt(readFileSync(run.pidFile, "utf8").trim(), 10)
    if (Number.isFinite(pid) && pid > 0) return { present: true, mtimeMs, pidAlive: processAlive(pid) }
  } catch {
    // No pid recorded (pre-pid run, or the wrapper died before writing it).
  }
  return { present: true, mtimeMs }
}

function clearLock(run: AgentRun) {
  rmSync(run.lockDir, { recursive: true, force: true })
}

/** A killed background agent never runs its cleanup, so a stale lock and a missing
 *  terminal event survive it. Reconcile both instead of waiting out
 *  STALE_LOCK_MS, which would otherwise report "Running: yes" for 12h. */
function reconcileAgentState(ctx: PluginContext, run: AgentRun) {
  const lock = readLockState(run)
  if (isGardenerLive(lock)) return
  if (!needsFailureBackfill(readEvents(), false, run.prefix)) {
    if (lock.present) clearLock(run)
    return
  }
  if (lock.present) clearLock(run)
  appendEvent({ event: `${run.prefix}_failed`, reason: "process died without recording a result" })
  agentToast(ctx, run, "failed")
}

function hasSystemdRun() {
  if (process.platform !== "linux" || !process.env.XDG_RUNTIME_DIR) return false
  return ["/usr/bin/systemd-run", "/bin/systemd-run"].some((path) => existsSync(path))
}

function spawnCommand(run: AgentRun, wrapper: string) {
  if (!hasSystemdRun()) return ["/bin/sh", "-c", wrapper]
  return [
    "systemd-run",
    "--user",
    "--scope",
    "--quiet",
    "--collect",
    `--unit=${run.agent}-${Date.now()}`,
    "/bin/sh",
    "-c",
    wrapper,
  ]
}

function appendResultFromShell(event: string) {
  return `printf '{"ts":"%s","event":"${event}"}\\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> ${shellQuote(EVENTS_FILE)}`
}

function runBackgroundAgent(
  ctx: PluginContext,
  run: AgentRun,
  options: { dir: string; title: string; prompt: string; reason: string },
) {
  ensureStateDirectory()
  const lock = readLockState(run)
  if (lock.present) {
    if (isGardenerLive(lock)) return "already running"
    clearLock(run)
  }

  try {
    mkdirSync(run.lockDir)
  } catch {
    return "already running"
  }

  appendEvent({ event: `${run.prefix}_started`, reason: options.reason })
  agentToast(ctx, run, "started")
  const wrapper = `#!/bin/sh
set +e
echo $$ > ${shellQuote(run.pidFile)}
${CHILD_ENV}=${run.agent} opencode run \\
  --agent ${run.agent} --auto \\
  --dir ${shellQuote(options.dir)} \\
  --title ${shellQuote(options.title)} \\
  ${shellQuote(options.prompt)} >> ${shellQuote(run.logFile)} 2>&1
status=$?
if [ "$status" -eq 0 ]; then
  ${appendResultFromShell(`${run.prefix}_completed`)}
else
  ${appendResultFromShell(`${run.prefix}_failed`)}
fi
rm -rf ${shellQuote(run.lockDir)}
exit "$status"
`

  // A review outlives the session that triggers it. `detached` only breaks the
  // process group, NOT cgroup membership — the child stays in the caller's
  // systemd scope and is SIGKILLed when that scope goes away, mid-run, before
  // it can record a result. A transient --user scope reparents it to the user
  // manager so it survives. Fall back to a bare spawn where systemd-run is
  // absent (non-systemd hosts); there the old race remains, but the pid file
  // still lets us detect the death.
  const command = spawnCommand(run, wrapper)
  try {
    const child = spawn(command[0]!, command.slice(1), {
      cwd: options.dir,
      detached: true,
      stdio: "ignore",
      env: { ...process.env, [CHILD_ENV]: run.agent },
    })
    child.unref()
  } catch (error) {
    clearLock(run)
    appendEvent({ event: `${run.prefix}_failed`, reason: String(error) })
    agentToast(ctx, run, "failed")
    return `failed to start ${run.agent}: ${error instanceof Error ? error.message : String(error)}`
  }
  return "started"
}

function startGardener(ctx: PluginContext, reason: "weekly" | "manual") {
  return runBackgroundAgent(ctx, GARDENER, {
    dir: join(homedir(), ".config/opencode"),
    title: "[ct-gardener] weekly review",
    prompt: "Run the complete weekly Claptrap Skill garden now.",
    reason,
  })
}

function startHarvester(ctx: PluginContext, sessionID: string) {
  const project = projectFor(ctx)
  return runBackgroundAgent(ctx, HARVESTER, {
    // Unlike the gardener: session storage, project-scoped skills, and the
    // repo-vs-global placement decision all need the session's project root.
    dir: project,
    title: `[ct-skill-harvester] session ${sessionID}`,
    reason: "idle",
    prompt: [
      `Review OpenCode session ${sessionID} and decide whether it contains a verified, non-obvious, likely-to-recur procedure worth capturing as a managed ct-* Skill.`,
      `Project root: ${project}.`,
      `Read the transcript with: opencode export ${sessionID}`,
      `Session storage is a SQLite database (~/.local/share/opencode/opencode.db) — do not read it directly; if the export fails, exit with a "no changes — transcript unavailable" summary.`,
      `Default outcome is no change. Create at most one Skill.`,
    ].join(" "),
  })
}

function notifyResultIfNeeded(ctx: PluginContext, run: AgentRun) {
  const events = readEvents()
  const result = newest(events, [`${run.prefix}_completed`, `${run.prefix}_failed`])
  const notified = newest(events, [`${run.prefix}_result_notified`])
  if (!result || (notified && eventTime(notified) >= eventTime(result))) return
  const failed = result.event === `${run.prefix}_failed`
  const message = failed ? run.toasts.failed : run.toasts.completed
  appendEvent({ event: `${run.prefix}_result_notified` })
  void ctx.client.app.log({ body: { service: "claptrap", level: "info", message, extra: { event: result.event } } })
  void ctx.client.tui.showToast({ body: { message, variant: failed ? "warning" : "success", duration: 3000 } }).catch(() => {
    // Startup in a detached run may not have a TUI.
  })
}

function skillFileIsManaged(path: string) {
  try {
    return readFileSync(path, "utf8").includes("managed-by: ct-gardener")
  } catch {
    return false
  }
}

function scanSkillRoot(root: string) {
  if (!existsSync(root)) return 0
  let count = 0
  try {
    for (const entry of readdirSync(root, { withFileTypes: true })) {
      if (entry.isDirectory() && entry.name.startsWith("ct-") && skillFileIsManaged(join(root, entry.name, "SKILL.md"))) count++
    }
  } catch {
    return count
  }
  return count
}

function skillCounts(ctx: PluginContext, events: EventRecord[]) {
  const projects = new Set<string>([ctx.worktree, ctx.directory])
  for (const event of events) if (event.event === "project_seen" && typeof event.project === "string") projects.add(event.project)
  let active = scanSkillRoot(join(homedir(), ".agents/skills/claptrap"))
  let archived = scanSkillRoot(join(homedir(), ".agents/skills-archive/claptrap"))
  for (const project of projects) {
    if (!project) continue
    active += scanSkillRoot(join(project, ".agents/skills/claptrap"))
    archived += scanSkillRoot(join(project, ".agents/skills-archive/claptrap"))
  }
  return { active, archived }
}

const ClaptrapPlugin: Plugin = async (ctx) => {
  ensureStateDirectory()
  appendEvent({ event: "project_seen", project: projectFor(ctx) })

  // Per-session gate + activity state. In-memory and best-effort by design:
  // lost on plugin restart, which at worst re-fires a gate or re-reviews a
  // transcript the harvester is already conservative about.
  const gates = new Map<string, GateState>()

  if (!process.env[CHILD_ENV]) {
    for (const run of [GARDENER, HARVESTER]) {
      reconcileAgentState(ctx, run)
      notifyResultIfNeeded(ctx, run)
    }
    if (isGardenerDue(readEvents())) startGardener(ctx, "weekly")
  }

  return {
    tool: {
      ct_run_gardener: tool({
        description: "Start the complete weekly Claptrap Skill gardener immediately in the background.",
        args: {},
        async execute() {
          return startGardener(ctx, "manual")
        },
      }),
      ct_status: tool({
        description: "Show Claptrap Skill, Mnemosyne, and gardener activity.",
        args: {},
        async execute() {
          const events = readEvents()
          const summary = (run: AgentRun) =>
            existsSync(run.summaryFile) ? readFileSync(run.summaryFile, "utf8") : ""
          return buildStatusReport({
            events,
            summaryText: summary(GARDENER),
            harvesterSummaryText: summary(HARVESTER),
            running: isGardenerLive(readLockState(GARDENER)),
            harvesterRunning: isGardenerLive(readLockState(HARVESTER)),
            skillCounts: skillCounts(ctx, events),
          })
        },
      }),
    },
    "tool.execute.after": async (input, output) => {
      const tracked = classifyToolCall(input)
      if (tracked) await recordAndNotify(ctx, { ...tracked, ...(input.sessionID ? { session_id: input.sessionID } : {}) })
      if (input.tool === "bash" && typeof input.args?.command === "string") {
        const command = input.args.command
        const match = command.match(/(?:^|[\s/'"])(?:[^\s/'"]+\/)?skills(?:-archive)?\/claptrap\/(ct-[^/\s/'"]+)/)
        if (match) await recordAndNotify(ctx, { event: "managed_skill_changed", name: match[1] })
      }
      const sessionID = input.sessionID
      if (!sessionID) return
      const { state, warnRecall } = applyToolToGate(gates.get(sessionID) ?? newGateState(), input.tool)
      gates.set(sessionID, state)
      if (!warnRecall) return
      // Verified to reach the model: mutating output.output propagates.
      output.output = `${output.output}\n\n${RECALL_REMINDER}`
      appendEvent({ event: "gate_recall_warned", project: projectFor(ctx), session_id: sessionID })
      gateToast(ctx, "CT: mutating files without a Mnemosyne recall this session")
    },
    event: async ({ event }) => {
      if (event.type === "file.edited") {
        const file = (event.properties as { file?: string } | undefined)?.file
        const tracked = file ? classifyManagedSkillEdit(file) : undefined
        if (tracked) await recordAndNotify(ctx, tracked)
      }
      if (event.type === "session.idle" && !process.env[CHILD_ENV]) {
        for (const run of [GARDENER, HARVESTER]) {
          reconcileAgentState(ctx, run)
          notifyResultIfNeeded(ctx, run)
        }
        if (isGardenerDue(readEvents())) startGardener(ctx, "weekly")

        const sessionID = (event.properties as { sessionID?: string } | undefined)?.sessionID
        const state = sessionID ? gates.get(sessionID) : undefined
        if (!sessionID || !state) return

        if (shouldWarnStore(state)) {
          gates.set(sessionID, { ...state, warnedStore: true })
          appendEvent({ event: "gate_store_warned", project: projectFor(ctx), session_id: sessionID })
          gateToast(ctx, "CT: session mutated files without storing a Mnemosyne memory")
        }

        // idle fires after every completed turn; the watermark is the only
        // debounce. A live harvester blocks other sessions — they retry at
        // their next idle, and the weekly gardener is the backstop.
        const current = gates.get(sessionID)!
        if (shouldRunHarvester(current.counter, current.watermark, isGardenerLive(readLockState(HARVESTER)))) {
          gates.set(sessionID, { ...current, watermark: current.counter })
          startHarvester(ctx, sessionID)
        }
      }
      if (event.type === "session.error") {
        appendEvent({ event: "session_error", project: projectFor(ctx) })
      }
    },
  }
}

export default ClaptrapPlugin
