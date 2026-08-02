import { expect, test } from "bun:test"
import {
  buildStatusReport,
  classifyManagedSkillEdit,
  classifyToolCall,
  isGardenerDue,
  isLockStale,
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
