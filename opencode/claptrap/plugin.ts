import { type Plugin, type PluginInput, tool } from "@opencode-ai/plugin"
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync } from "node:fs"
import { spawn } from "node:child_process"
import { homedir } from "node:os"
import { join } from "node:path"
import {
  buildStatusReport,
  classifyManagedSkillEdit,
  classifyToolCall,
  isGardenerDue,
  isGardenerLive,
  needsFailureBackfill,
  type TrackedEvent,
  type EventRecord,
} from "./logic"

const STATE_DIR = join(homedir(), ".local/state/claptrap")
const GARDENER_AGENT = "ct-gardener"
const CHILD_ENV = "CLAPTRAP_GARDENER_CHILD"

const EVENTS_FILE = join(STATE_DIR, "events.jsonl")
const GARDENER_LOG = join(STATE_DIR, "gardener.log")
const GARDENER_LOCK = join(STATE_DIR, "gardener.lock")
const GARDENER_PID_FILE = join(GARDENER_LOCK, "pid")
const SUMMARY_FILE = join(STATE_DIR, "last-gardener-summary.md")
type PluginContext = PluginInput

function timestamp() {
  return new Date().toISOString()
}

function ensureStateDirectory() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function appendEvent(event: Omit<EventRecord, "ts">) {
  ensureStateDirectory()
  appendFileSync(EVENTS_FILE, `${JSON.stringify({ ts: timestamp(), ...event })}\n`)
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

function gardenerToast(ctx: PluginContext, event: "gardener_started" | "gardener_completed" | "gardener_failed") {
  const message = event === "gardener_started"
    ? "CT: weekly gardener started in background"
    : event === "gardener_completed"
      ? "CT: weekly gardener completed; run /ct-status"
      : "CT: weekly gardener failed; check gardener.log"
  void ctx.client.app.log({ body: { service: "claptrap", level: "info", message, extra: { event } } })
  void ctx.client.tui.showToast({ body: { message, variant: "info", duration: 3000 } }).catch(() => {
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

function readLockState() {
  if (!existsSync(GARDENER_LOCK)) return { present: false }
  let mtimeMs: number | undefined
  try {
    mtimeMs = statSync(GARDENER_LOCK).mtimeMs
  } catch {
    mtimeMs = undefined
  }
  try {
    const pid = Number.parseInt(readFileSync(GARDENER_PID_FILE, "utf8").trim(), 10)
    if (Number.isFinite(pid) && pid > 0) return { present: true, mtimeMs, pidAlive: processAlive(pid) }
  } catch {
    // No pid recorded (pre-pid run, or the wrapper died before writing it).
  }
  return { present: true, mtimeMs }
}

function clearLock() {
  rmSync(GARDENER_LOCK, { recursive: true, force: true })
}

/** A killed gardener never runs its cleanup, so a stale lock and a missing
 *  terminal event survive it. Reconcile both instead of waiting out
 *  STALE_LOCK_MS, which would otherwise report "Running: yes" for 12h. */
function reconcileGardenerState(ctx: PluginContext) {
  const lock = readLockState()
  if (isGardenerLive(lock)) return
  if (!needsFailureBackfill(readEvents(), false)) {
    if (lock.present) clearLock()
    return
  }
  if (lock.present) clearLock()
  appendEvent({ event: "gardener_failed", reason: "process died without recording a result" })
  gardenerToast(ctx, "gardener_failed")
}

function hasSystemdRun() {
  if (process.platform !== "linux" || !process.env.XDG_RUNTIME_DIR) return false
  return ["/usr/bin/systemd-run", "/bin/systemd-run"].some((path) => existsSync(path))
}

function spawnCommand(wrapper: string) {
  if (!hasSystemdRun()) return ["/bin/sh", "-c", wrapper]
  return [
    "systemd-run",
    "--user",
    "--scope",
    "--quiet",
    "--collect",
    `--unit=ct-gardener-${Date.now()}`,
    "/bin/sh",
    "-c",
    wrapper,
  ]
}

function appendResultFromShell(event: "gardener_completed" | "gardener_failed") {
  return `printf '{"ts":"%s","event":"${event}"}\\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> ${shellQuote(EVENTS_FILE)}`
}

function startGardener(ctx: PluginContext, reason: "weekly" | "manual") {
  ensureStateDirectory()
  const lock = readLockState()
  if (lock.present) {
    if (isGardenerLive(lock)) return "already running"
    clearLock()
  }

  try {
    mkdirSync(GARDENER_LOCK)
  } catch {
    return "already running"
  }

  appendEvent({ event: "gardener_started", reason })
  gardenerToast(ctx, "gardener_started")
  const wrapper = `#!/bin/sh
set +e
echo $$ > ${shellQuote(GARDENER_PID_FILE)}
CLAPTRAP_GARDENER_CHILD=1 opencode run \\
  --agent ${GARDENER_AGENT} --auto \\
  --dir "$HOME/.config/opencode" \\
  --title "[ct-gardener] weekly review" \\
  "Run the complete weekly Claptrap Skill garden now." >> ${shellQuote(GARDENER_LOG)} 2>&1
status=$?
if [ "$status" -eq 0 ]; then
  ${appendResultFromShell("gardener_completed")}
else
  ${appendResultFromShell("gardener_failed")}
fi
rm -rf ${shellQuote(GARDENER_LOCK)}
exit "$status"
`

  // A review outlives the session that triggers it. `detached` only breaks the
  // process group, NOT cgroup membership — the child stays in the caller's
  // systemd scope and is SIGKILLed when that scope goes away, mid-run, before
  // it can record a result. A transient --user scope reparents it to the user
  // manager so it survives. Fall back to a bare spawn where systemd-run is
  // absent (non-systemd hosts); there the old race remains, but the pid file
  // still lets us detect the death.
  const command = spawnCommand(wrapper)
  try {
    const child = spawn(command[0]!, command.slice(1), {
      cwd: join(homedir(), ".config/opencode"),
      detached: true,
      stdio: "ignore",
      env: { ...process.env, [CHILD_ENV]: "1" },
    })
    child.unref()
  } catch (error) {
    clearLock()
    appendEvent({ event: "gardener_failed", reason: String(error) })
    gardenerToast(ctx, "gardener_failed")
    return `failed to start gardener: ${error instanceof Error ? error.message : String(error)}`
  }
  return "started"
}

function notifyGardenerResultIfNeeded(ctx: PluginContext) {
  const events = readEvents()
  const result = newest(events, ["gardener_completed", "gardener_failed"])
  const notified = newest(events, ["gardener_result_notified"])
  if (!result || (notified && eventTime(notified) >= eventTime(result))) return
  const failed = result.event === "gardener_failed"
  const message = failed ? "CT: weekly gardener failed; check gardener.log" : "CT: weekly gardener completed; run /ct-status"
  appendEvent({ event: "gardener_result_notified" })
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

  if (process.env[CHILD_ENV] !== "1") {
    reconcileGardenerState(ctx)
    notifyGardenerResultIfNeeded(ctx)
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
          const summary = existsSync(SUMMARY_FILE) ? readFileSync(SUMMARY_FILE, "utf8") : ""
          return buildStatusReport(events, summary, isGardenerLive(readLockState()), skillCounts(ctx, events))
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
      void output
    },
    event: async ({ event }) => {
      if (event.type === "file.edited") {
        const file = (event.properties as { file?: string } | undefined)?.file
        const tracked = file ? classifyManagedSkillEdit(file) : undefined
        if (tracked) await recordAndNotify(ctx, tracked)
      }
      if (event.type === "session.idle" && process.env[CHILD_ENV] !== "1") {
        reconcileGardenerState(ctx)
        notifyGardenerResultIfNeeded(ctx)
        if (isGardenerDue(readEvents())) startGardener(ctx, "weekly")
      }
      if (event.type === "session.error") {
        appendEvent({ event: "session_error", project: projectFor(ctx) })
      }
    },
  }
}

export default ClaptrapPlugin
