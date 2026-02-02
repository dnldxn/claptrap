// .opencode/plugins/slack-alerts.ts
export const SlackAlerts = async ({ directory, worktree, project }) => {
  const webhook = process.env.SLACK_WEBHOOK_URL;
  if (!webhook) {
    console.warn(
      "[SlackAlerts] SLACK_WEBHOOK_URL is not set; plugin will do nothing."
    );
    return {};
  }

  // Very small dedupe so we don't spam if multiple identical events fire.
  let lastSent = "";

  // Track if a question was recently asked to distinguish "idle after question"
  // from "idle after completion/summary"
  let recentQuestionAsked = false;

  // Tool names that indicate the agent is asking a question
  const questionToolNames = new Set([
    "AskUserQuestion",
    "AskUserTool",
    "question",
    "ask",
  ]);

  async function postToSlack(text: string) {
    const key = text.slice(0, 500);
    if (key === lastSent) return;
    lastSent = key;

    const res = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    // Slack returns useful non-200 errors for bad payloads / invalid webhook, etc.
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      console.warn(`[SlackAlerts] Slack webhook failed: ${res.status} ${body}`);
    }
  }

  function summarizeContext() {
    const proj = project?.name ? `project: ${project.name}\n` : "";
    const dir = directory ? `dir: ${directory}\n` : "";
    const wt = worktree ? `worktree: ${worktree}\n` : "";
    return `${proj}${dir}${wt}`.trim();
  }

  // Log at plugin init to confirm loading
  console.log("[SlackAlerts] Plugin initialized, webhook configured");

  return {
    // Detect when agent/subagent asks a question via tool invocation
    // Signature per docs: (input, output) where input.tool is tool name, output.args is arguments
    "tool.execute.after": async (
      input: { tool: string },
      output: { args: Record<string, unknown> }
    ) => {
      console.log("[SlackAlerts] tool.execute.after fired:", input?.tool);

      const toolName = input?.tool ?? "";
      if (!questionToolNames.has(toolName)) return;

      recentQuestionAsked = true;

      // Extract question text from output.args
      const args = output?.args ?? {};
      const questionText =
        (args?.question as string) ??
        (args?.prompt as string) ??
        (args?.message as string) ??
        "(question details not available)";

      const text = `❓ OpenCode is asking a question\n\n${summarizeContext()}\n\ntool: ${toolName}\nquestion: ${questionText}`;
      await postToSlack(text);
    },

    // Generic event hook - receives { event } with event.type
    event: async ({ event }: { event: { type?: string } }) => {
      console.log("[SlackAlerts] event hook fired:", event?.type);

      const type = event?.type ?? "unknown";

      // Handle session.idle specially - distinguish question vs completion
      if (type === "session.idle") {
        if (recentQuestionAsked) {
          // Already sent alert via tool.execute.after, reset flag
          recentQuestionAsked = false;
          return;
        }
        // No recent question = agent completed/provided summary
        const text = `✅ OpenCode completed (summary ready)\n\n${summarizeContext()}\n\nevent: ${type}`;
        await postToSlack(text);
        return;
      }

      // Other attention-needing events
      if (type === "session.error") {
        const text = `🛑 OpenCode session error\n\n${summarizeContext()}\n\nevent: ${type}`;
        await postToSlack(text);
        return;
      }

      if (type === "permission.asked") {
        const text = `✋ OpenCode needs approval\n\n${summarizeContext()}\n\nevent: ${type}`;
        await postToSlack(text);
        return;
      }
    },
  };
};
