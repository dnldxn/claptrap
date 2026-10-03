import { expect, test } from "bun:test"
import { mergeModels, parseModelList, toModelConfig } from "../logic.ts"

const combo = {
  id: "skill-gardener",
  owned_by: "combo",
  capabilities: { vision: true, pdf: true, tools: true, reasoning: true, contextWindow: 400000, maxOutput: 128000 },
}

test("parses an OpenAI-style model list and skips malformed rows", () => {
  expect(parseModelList({ data: [{ id: "a" }, { id: "" }, {}, null] }).map((m) => m.id)).toEqual(["a"])
  expect(() => parseModelList({ error: "nope" })).toThrow()
})

test("maps 9router capabilities onto OpenCode model fields", () => {
  expect(toModelConfig(combo)).toEqual({
    name: "skill-gardener (9router combo)",
    modalities: { input: ["text", "image", "pdf"], output: ["text"] },
    attachment: true,
    tool_call: true,
    reasoning: true,
    limit: { context: 400000, output: 128000 },
  })
  expect(toModelConfig({ id: "nw/glm-5.3" })).toEqual({ name: "nw/glm-5.3" })
})

test("router list decides membership while configured fields win", () => {
  const merged = mergeModels([combo, { id: "new/model" }], {
    "skill-gardener": { name: "Skill Gardener", options: { x: 1 } },
    "gone/model": { name: "Retired" },
  })
  expect(Object.keys(merged)).toEqual(["skill-gardener", "new/model"])
  expect(merged["skill-gardener"].name).toBe("Skill Gardener")
  expect(merged["skill-gardener"].options).toEqual({ x: 1 })
  expect(merged["skill-gardener"].tool_call).toBe(true)
})
