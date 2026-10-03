import type { Plugin } from "@opencode-ai/plugin"
import { mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"
import { mergeModels, parseModelList, type RemoteModel } from "./logic"

// Providers whose model list is replaced by their live /models endpoint at startup.
const PROVIDERS = ["9router"]
const TIMEOUT_MS = 4000
const CACHE_DIR = join(homedir(), ".cache/opencode/claptrap-model-sync")

type ProviderConfig = {
  options?: { baseURL?: string; apiKey?: string }
  models?: Record<string, Record<string, unknown>>
}

async function fetchModels(provider: ProviderConfig): Promise<RemoteModel[]> {
  const baseURL = provider.options?.baseURL?.replace(/\/+$/, "")
  if (!baseURL) throw new Error("provider has no options.baseURL")
  const headers: Record<string, string> = {}
  if (provider.options?.apiKey) headers.Authorization = `Bearer ${provider.options.apiKey}`
  const response = await fetch(`${baseURL}/models`, { headers, signal: AbortSignal.timeout(TIMEOUT_MS) })
  if (!response.ok) throw new Error(`GET /models returned HTTP ${response.status}`)
  return parseModelList(await response.json())
}

function readCache(id: string): RemoteModel[] | undefined {
  try {
    return parseModelList(JSON.parse(readFileSync(join(CACHE_DIR, `${id}.json`), "utf8")))
  } catch {
    return undefined
  }
}

function writeCache(id: string, models: RemoteModel[]): void {
  try {
    mkdirSync(CACHE_DIR, { recursive: true })
    writeFileSync(join(CACHE_DIR, `${id}.json`), JSON.stringify({ data: models }))
  } catch {
    // A cache miss only costs the offline fallback.
  }
}

export const ModelSyncPlugin: Plugin = async ({ client }) => {
  const log = (level: "info" | "warn", message: string) =>
    client.app.log({ body: { service: "claptrap-model-sync", level, message } }).catch(() => {})

  return {
    // Runs once while OpenCode loads config, before providers are built, so
    // mutating provider.models here is what the model picker sees.
    config: async (config) => {
      const providers = (config.provider ?? {}) as Record<string, ProviderConfig>
      await Promise.all(
        PROVIDERS.filter((id) => providers[id]).map(async (id) => {
          const provider = providers[id]
          let remote: RemoteModel[] | undefined
          try {
            remote = await fetchModels(provider)
            writeCache(id, remote)
          } catch (error) {
            remote = readCache(id)
            log("warn", `${id}: live model fetch failed (${error}); ${remote ? "using cached list" : "keeping configured list"}`)
          }
          if (!remote?.length) return
          provider.models = mergeModels(remote, provider.models)
          log("info", `${id}: loaded ${remote.length} models`)
        }),
      )
    },
  }
}
