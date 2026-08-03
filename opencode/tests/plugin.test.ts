import { expect, test } from "bun:test"
import {
  buildStatusReport,
  classifyManagedSkillEdit,
  classifyToolCall,
  isGardenerDue,
  isGardenerLive,
  isLockStale,
  needsFailureBackfill,
} from "../claptrap/logic.ts"

const day = 24 * 60 * 60 * 1000

function event(event: string, ts: number, extra: Record<string, unknown> = {}) {
  return { event, ts: new Date(ts).toISOString(), ...extra }
}

test("classifies both Mnemosyne tool-id prefixes and skill args", () => {
  const cases = [
    ["mcp__mnemosyne__mnemosyne_recall", "memory_recalled"],
    ["mcp__mnemosyne__mnemosyne_remember", "memory_stored"],
    ["mcp__mnemosyne__mnemosyne_stats", "memory_other"],
    ["mnemosyne_recall", "memory_recalled"],
  ] as const

  for (const [tool, expected] of cases) {
    expect(classifyToolCall({ tool, args: {} })).toMatchObject({ event: expected })
  }
  expect(classifyToolCall({ tool: "skill", args: { name: "ct-example" } })).toEqual({
    event: "skill_loaded",
    name: "ct-example",
  })
  expect(classifyToolCall({ tool: "bash", args: {} })).toBeUndefined()
})

test("detects only managed-skill path shapes", () => {
  expect(classifyManagedSkillEdit("/x/skills/claptrap/ct-foo/SKILL.md")).toEqual({
    event: "managed_skill_changed",
    name: "ct-foo",
  })
  expect(classifyManagedSkillEdit("/x/skills-archive/claptrap/ct-foo/SKILL.md")).toEqual({
    event: "managed_skill_changed",
    name: "ct-foo",
  })
  expect(classifyManagedSkillEdit("/x/ct-foo/SKILL.md")).toBeUndefined()
  expect(classifyManagedSkillEdit("/x/skills/claptrap/not-ct-foo/SKILL.md")).toBeUndefined()
  expect(classifyManagedSkillEdit("/x/skills/claptrap/ct-foo/README.md")).toBeUndefined()
})

test("applies the seven-day gardener due rule", () => {
  const now = Date.parse("2026-08-02T00:00:00.000Z")
  expect(isGardenerDue([], now)).toBe(true)
  expect(isGardenerDue([event("gardener_completed", now - day)], now)).toBe(false)
  expect(isGardenerDue([event("gardener_completed", now - 8 * day)], now)).toBe(true)
})

test("marks locks stale only after twelve hours", () => {
  const now = Date.parse("2026-08-02T00:00:00.000Z")
  expect(isLockStale(now - 11 * 60 * 60 * 1000, now)).toBe(false)
  expect(isLockStale(now - 13 * 60 * 60 * 1000, now)).toBe(true)
})

test("treats a lock as running only while its process lives", () => {
  const now = Date.parse("2026-08-02T00:00:00.000Z")
  const fresh = now - 60 * 1000

  expect(isGardenerLive({ present: false }, now)).toBe(false)
  // The bug: a killed run leaves a fresh lock behind. pid wins over lock age.
  expect(isGardenerLive({ present: true, mtimeMs: fresh, pidAlive: false }, now)).toBe(false)
  expect(isGardenerLive({ present: true, mtimeMs: fresh, pidAlive: true }, now)).toBe(true)
  // No pid recorded (pre-pid run) falls back to the 12h staleness window.
  expect(isGardenerLive({ present: true, mtimeMs: fresh }, now)).toBe(true)
  expect(isGardenerLive({ present: true, mtimeMs: now - 13 * 60 * 60 * 1000 }, now)).toBe(false)
})

test("backfills a failure only for a dead start with no recorded result", () => {
  const now = Date.parse("2026-08-02T00:00:00.000Z")
  const started = [event("gardener_started", now - 2 * day)]

  expect(needsFailureBackfill(started, false)).toBe(true)
  // Still running: leave it alone.
  expect(needsFailureBackfill(started, true)).toBe(false)
  // Already recorded its own outcome.
  expect(
    needsFailureBackfill([...started, event("gardener_completed", now - day)], false),
  ).toBe(false)
  expect(needsFailureBackfill([...started, event("gardener_failed", now - day)], false)).toBe(false)
  // A result older than the newest start means that start went unrecorded.
  expect(
    needsFailureBackfill(
      [event("gardener_completed", now - 3 * day), event("gardener_started", now - day)],
      false,
    ),
  ).toBe(true)
  expect(needsFailureBackfill([], false)).toBe(false)
})

test("builds a status report from event and skill fixtures", () => {
  const now = Date.parse("2026-08-02T00:00:00.000Z")
  const report = buildStatusReport(
    [
      event("gardener_completed", now - day),
      event("skill_loaded", now - 2 * day, { name: "ct-one", project: "/repo" }),
      event("skill_loaded", now - 3 * day, { name: "ct-one", project: "/repo" }),
      event("memory_recalled", now - 2 * day),
      event("memory_stored", now - 3 * day),
      event("managed_skill_changed", now - 4 * day, { name: "ct-one" }),
    ],
    "- 1 updated, 0 archived, 0 created",
    false,
    { active: 1, archived: 0 },
    now,
  )

  expect(report).toContain("# Claptrap status")
  expect(report).toContain("Running: no")
  expect(report).toContain("Active: 1")
  expect(report).toContain("Archived: 0")
  expect(report).toContain("Skill loads: 2")
  expect(report).toContain("Mnemosyne recalls: 1")
  expect(report).toContain("ct-one — 2 loads")
  expect(report).toContain("1 updated, 0 archived, 0 created")
})
