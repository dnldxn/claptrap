// Pure helpers for model-sync; plugin.ts owns I/O.

export type RemoteModel = {
  id: string
  owned_by?: string
  capabilities?: {
    vision?: boolean
    pdf?: boolean
    audioInput?: boolean
    videoInput?: boolean
    tools?: boolean
    reasoning?: boolean
    contextWindow?: number | null
    maxOutput?: number | null
  }
}

export type ModelConfig = Record<string, unknown>
type Modality = "text" | "audio" | "image" | "video" | "pdf"

export function parseModelList(body: unknown): RemoteModel[] {
  const data = (body as { data?: unknown })?.data
  if (!Array.isArray(data)) throw new Error("response has no data array")
  return data.filter((m): m is RemoteModel => typeof m?.id === "string" && m.id.length > 0)
}

export function toModelConfig(model: RemoteModel): ModelConfig {
  const caps = model.capabilities
  const config: ModelConfig = {
    name: model.owned_by === "combo" ? `${model.id} (9router combo)` : model.id,
  }
  if (!caps) return config

  const input: Modality[] = ["text"]
  if (caps.vision) input.push("image")
  if (caps.pdf) input.push("pdf")
  if (caps.audioInput) input.push("audio")
  if (caps.videoInput) input.push("video")
  config.modalities = { input, output: ["text"] }
  config.attachment = input.length > 1
  if (typeof caps.tools === "boolean") config.tool_call = caps.tools
  if (typeof caps.reasoning === "boolean") config.reasoning = caps.reasoning
  if (caps.contextWindow && caps.maxOutput) {
    config.limit = { context: caps.contextWindow, output: caps.maxOutput }
  }
  return config
}

/**
 * The router's list decides which models exist. Hand-written config entries
 * for a listed id win field-by-field, so custom names and options survive.
 * Configured ids the router no longer serves are dropped.
 */
export function mergeModels(
  remote: RemoteModel[],
  configured: Record<string, ModelConfig> = {},
): Record<string, ModelConfig> {
  const merged: Record<string, ModelConfig> = {}
  for (const model of remote) {
    merged[model.id] = { ...toModelConfig(model), ...(configured[model.id] ?? {}) }
  }
  return merged
}
