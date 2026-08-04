import { type Plugin, type PluginInput, tool } from "@opencode-ai/plugin"
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs"
import { spawn } from "node:child_process"
import { homedir } from "node:os"
import { join } from "node:path"
import {
  applyToolToGate,
  buildStatusReport,
  classifyManagedSkillBashCommand,
  classifyManagedSkillEdit,
  classifyToolCall,
  eventTime,
  isGardenerDue,
  isGardenerLive,
  newest,
  newGateState,
  needsFailureBackfill,
  pruneEvents,
  RECALL_REMINDER,
  recordSkillAnnouncement,
  shouldAnnounceSkillChange,
  shouldRunHarvester,
  shouldWarnStore,
  transcriptBanner,
  transcriptNotice,
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
  /** Transcript wording. Shorter than the toast: the "CT: " prefix is added by
   *  transcriptNotice, and this text is permanent context. */
  transcript: { completed: string; failed: string }
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
    transcript: {
      completed: `${label} completed — run /ct-status`,
      failed: `${label} failed — check ${prefix}.log`,
    },
  }
}

const GARDENER = agentRun("ct-gardener", "gardener", "weekly gardener")
const HARVESTER = agentRun("ct-skill-harvester", "harvester", "skill-harvester")

function timestamp() {
  return new Date().toISOString()
}

function ensureStateDirectory() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function appendEvent(event: Omit<EventRecord, "ts">): EventRecord {
  ensureStateDirectory()
  const agent = process.env[CHILD_ENV]
  const record = { ts: timestamp(), ...(agent ? { agent } : {}), ...event } as EventRecord
  appendFileSync(EVENTS_FILE, `${JSON.stringify(record)}\n`)
  return record
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

/** Rewrite events.jsonl without old history. Read-then-write can drop an event
 *  appended concurrently by another OpenCode instance; acceptable for
 *  metadata-only telemetry, and only main sessions prune, once at startup. */
function pruneEventsFile() {
  const events = readEvents()
  const pruned = pruneEvents(events)
  if (pruned.length === events.length) return
  writeFileSync(EVENTS_FILE, pruned.map((event) => JSON.stringify(event)).join("\n") + (pruned.length ? "\n" : ""))
}

function projectFor(ctx: PluginInput) {
  return ctx.worktree || ctx.directory
}

/** Only for toasted events; `memory_*` is recorded silently, see recordAndNotify. */
function toastMessage(tracked: TrackedEvent) {
  if (tracked.event === "skill_loaded") return `CT: loaded Skill ${tracked.name ?? "(unnamed)"}`
  return `CT: changed managed Skill ${tracked.name ?? "(unknown)"}`
}

type ToastVariant = "info" | "warning" | "success"
const TOAST_MS = 5000

function notify(ctx: PluginInput, message: string, event: string, variant: ToastVariant = "info") {
  void ctx.client.app.log({ body: { service: "claptrap", level: "info", message, extra: { event } } })
  void ctx.client.tui.showToast({ body: { message, variant, duration: TOAST_MS } }).catch(() => {
    // Detached `opencode run` processes do not always have a TUI.
  })
}

/** Write one line into the session transcript, where it survives the 5s toast.
 *  `noReply` stops it starting a model turn. The text must NOT be marked
 *  `synthetic`: verified against a live server on 1.18.11 — synthetic parts are
 *  stored and fed to the model but filtered out of every TUI render path, so a
 *  synthetic notice would be invisible, which is the opposite of the point.
 *  This costs context on every subsequent turn; callers must rate-limit. */
function postTranscript(ctx: PluginInput, sessionID: string, message: string) {
  void ctx.client.session
    .promptAsync({
      path: { id: sessionID },
      body: { noReply: true, parts: [{ type: "text", text: transcriptNotice(message) }] },
    })
    .catch(() => {
      // Best-effort: a missing session or a headless run must not break the hook.
    })
}

function recordAndNotify(ctx: PluginInput, tracked: TrackedEvent) {
  appendEvent({
    event: tracked.event,
    project: projectFor(ctx),
    ...(tracked.name ? { name: tracked.name } : {}),
    ...(tracked.tool ? { tool: tracked.tool } : {}),
    ...(tracked.session_id ? { session_id: tracked.session_id } : {}),
  })
  // Routine Mnemosyne traffic is recorded but not announced — it fires on every
  // recall/store and drowns out the rest. The recall/store gates still toast.
  if (tracked.event.startsWith("memory_")) return
  notify(ctx, toastMessage(tracked), tracked.event)
}

function agentToast(ctx: PluginInput, run: AgentRun, kind: "started" | "completed" | "failed") {
  notify(ctx, run.toasts[kind], `${run.prefix}_${kind}`, kind === "failed" ? "warning" : "info")
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
 *  STALE_LOCK_MS, which would otherwise report "Running: yes" for 12h.
 *  Returns the backfilled event, if any, so callers can extend their event
 *  snapshot without re-reading the file. */
function reconcileAgentState(ctx: PluginInput, run: AgentRun, events: EventRecord[]): EventRecord | undefined {
  const lock = readLockState(run)
  if (isGardenerLive(lock)) return undefined
  if (!needsFailureBackfill(events, false, run.prefix)) {
    if (lock.present) clearLock(run)
    return undefined
  }
  if (lock.present) clearLock(run)
  agentToast(ctx, run, "failed")
  return appendEvent({ event: `${run.prefix}_failed`, reason: "process died without recording a result" })
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
  // %3N is GNU date only. On BSD/macOS this writes a malformed ts that parses
  // to 0, making every result look older than its start and triggering a
  // spurious failure backfill. Fine on this Linux host; port before reuse.
  return `printf '{"ts":"%s","event":"${event}"}\\n' "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)" >> ${shellQuote(EVENTS_FILE)}`
}

function runBackgroundAgent(
  ctx: PluginInput,
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
  ${shellQuote(options.prompt)} > ${shellQuote(run.logFile)} 2>&1
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

function startGardener(ctx: PluginInput, reason: "weekly" | "manual") {
  return runBackgroundAgent(ctx, GARDENER, {
    dir: join(homedir(), ".config/opencode"),
    title: "[ct-gardener] weekly review",
    prompt: "Run the complete weekly Claptrap Skill garden now.",
    reason,
  })
}

function startHarvester(ctx: PluginInput, sessionID: string) {
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

function notifyResultIfNeeded(
  ctx: PluginInput,
  run: AgentRun,
  events: EventRecord[],
  sessionID?: string,
): EventRecord | undefined {
  const result = newest(events, [`${run.prefix}_completed`, `${run.prefix}_failed`])
  const notified = newest(events, [`${run.prefix}_result_notified`])
  if (!result || (notified && eventTime(notified) >= eventTime(result))) return undefined
  const failed = result.event === `${run.prefix}_failed`
  notify(ctx, failed ? run.toasts.failed : run.toasts.completed, String(result.event), failed ? "warning" : "success")
  // A background run finishes long after the toast that announced its start,
  // so this is the notice most likely to be missed. The _result_notified
  // event is the rate limit: one transcript line per run, never per idle.
  if (sessionID) postTranscript(ctx, sessionID, failed ? run.transcript.failed : run.transcript.completed)
  return appendEvent({ event: `${run.prefix}_result_notified` })
}

/** Startup and idle share this: reconcile dead runs, surface unseen results,
 *  and kick the weekly gardener — with one events read for everything.
 *  `sessionID` is present only on the idle path, where a transcript line has
 *  somewhere to land; at startup the toast is all we can offer. */
function reconcileAndSchedule(ctx: PluginInput, sessionID?: string) {
  const events = readEvents()
  for (const run of [GARDENER, HARVESTER]) {
    const backfilled = reconcileAgentState(ctx, run, events)
    if (backfilled) events.push(backfilled)
    const notified = notifyResultIfNeeded(ctx, run, events, sessionID)
    if (notified) events.push(notified)
  }
  if (isGardenerDue(events)) startGardener(ctx, "weekly")
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

function skillCounts(ctx: PluginInput, events: EventRecord[]) {
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

  // Managed-Skill names seen via file.edited, waiting for the next tool result
  // to carry them into the transcript. Bounded by the drain in the tool hook;
  // if no tool call follows (session ends mid-edit) the note is simply dropped.
  const pendingSkillNotes: string[] = []

  if (!process.env[CHILD_ENV]) {
    pruneEventsFile()
    reconcileAndSchedule(ctx)
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
      if (tracked) recordAndNotify(ctx, { ...tracked, ...(input.sessionID ? { session_id: input.sessionID } : {}) })
      const skillChange = input.tool === "bash" && typeof input.args?.command === "string"
        ? classifyManagedSkillBashCommand(input.args.command)
        : undefined
      if (skillChange) recordAndNotify(ctx, skillChange)
      // Child agents (gardener/harvester) have their own instructions; the
      // recall/store gates and harvester counters are for main sessions only.
      if (process.env[CHILD_ENV]) return
      const sessionID = input.sessionID
      if (!sessionID) return
      const { state, warnRecall } = applyToolToGate(gates.get(sessionID) ?? newGateState(), input.tool)
      gates.set(sessionID, state)

      // A managed-Skill write outlives the session, so it earns a permanent
      // line rather than a 5s toast — but only the first time this session
      // touches that skill. `edit`/`write` arrive via the file.edited event
      // instead, which drains through pendingSkillNotes.
      const announce = [...(skillChange ? [skillChange.name] : []), ...pendingSkillNotes.splice(0)]
      for (const name of announce) {
        const current = gates.get(sessionID)!
        if (!shouldAnnounceSkillChange(current, name)) continue
        gates.set(sessionID, recordSkillAnnouncement(current, name))
        output.output = `${output.output}${transcriptBanner(`updated managed Skill ${name}`)}`
      }

      if (!warnRecall) return
      // Verified to reach the model: mutating output.output propagates.
      output.output = `${output.output}\n\n${RECALL_REMINDER}`
      appendEvent({ event: "gate_recall_warned", project: projectFor(ctx), session_id: sessionID })
      notify(ctx, "CT: mutating files without a Mnemosyne recall this session", "gate", "warning")
    },
    event: async ({ event }) => {
      if (event.type === "file.edited") {
        const file = (event.properties as { file?: string } | undefined)?.file
        const tracked = file ? classifyManagedSkillEdit(file) : undefined
        if (tracked) {
          recordAndNotify(ctx, tracked)
          // file.edited carries no sessionID, so it cannot post on its own.
          // Park the name for the next tool result to carry. If that is the
          // edit's own result the line lands immediately; if the ordering puts
          // it later, it lands on the following tool call — still in the
          // transcript, still deduped. Skipped for child agents, whose writes
          // are the harvester doing its job, not news for this session.
          if (!process.env[CHILD_ENV] && !pendingSkillNotes.includes(tracked.name)) {
            pendingSkillNotes.push(tracked.name)
          }
        }
      }
      if (event.type === "session.idle" && !process.env[CHILD_ENV]) {
        const sessionID = (event.properties as { sessionID?: string } | undefined)?.sessionID
        reconcileAndSchedule(ctx, sessionID)

        const state = sessionID ? gates.get(sessionID) : undefined
        if (!sessionID || !state) return

        if (shouldWarnStore(state)) {
          gates.set(sessionID, { ...state, warnedStore: true })
          appendEvent({ event: "gate_store_warned", project: projectFor(ctx), session_id: sessionID })
          notify(ctx, "CT: session mutated files without storing a Mnemosyne memory", "gate", "warning")
          // The recall gate already lands in the transcript via tool output;
          // this one fires at idle with nothing to ride. warnedStore caps it
          // at one line per session.
          postTranscript(ctx, sessionID, "files changed with no Mnemosyne memory stored")
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
