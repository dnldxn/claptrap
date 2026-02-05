// Claptrap Enforcement Plugin for OpenCode
// Runs enforcement checks at session idle and after tool execution.
// Installed to: ~/.config/opencode/plugins/ (global) or .opencode/plugins/ (project)

import type { Plugin } from "@opencode-ai/plugin";

const ENFORCEMENT_SCRIPT = ".claptrap/enforcement.py";

// Tool names that involve file writes/edits
const WRITE_TOOLS = new Set([
  "write",
  "Write",
  "edit",
  "Edit",
  "EditFile",
  "WriteFile",
  "create_file",
  "replace_in_file",
]);

export const ClaptrapEnforcement: Plugin = async ({ directory, $ }) => {
  const scriptPath = `${directory}/${ENFORCEMENT_SCRIPT}`;

  // Check if enforcement script exists in this project
  const exists = await Bun.file(scriptPath).exists();
  if (!exists) {
    // Not a claptrap-enabled project, skip silently
    return {};
  }

  console.log("[ClaptrapEnforcement] Plugin initialized for", directory);

  return {
    "session.idle": async () => {
      try {
        await $`python3 ${scriptPath} --event session-end`.quiet();
      } catch {
        // Enforcement script may exit non-zero to signal action needed
      }
    },

    "tool.execute.after": async (
      input: { tool: string },
      _output: { args: Record<string, unknown> }
    ) => {
      const toolName = input?.tool ?? "";
      if (!WRITE_TOOLS.has(toolName)) return;

      try {
        await $`python3 ${scriptPath} --event post-tool`.quiet();
      } catch {
        // Enforcement script may exit non-zero to signal action needed
      }
    },
  };
};
