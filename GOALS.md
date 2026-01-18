# Goals

To create an AI-powered development workflow that is:
- Provider/model agnostic
- IDE/CLI/Environment agnostic
  - Should consume usage from provider subscriptions, such as Cursor, Github Copilot, Claude, Codex, etc.  Not per-request API usage.
- Easy to install and use
- Easy to extend and customize
- Easy to maintain and update
- Based on popular higher-level AI-based development tools/platforms (e.g. OpenSpec, claude-flow, etc.) that have frequent updates and are actively developed.  Allows customizing the workflow with new Agents, Skills, Commands, and instructions.  The platform or tool should:
    - Not be overly complex
    - Opinionated
    - Free and open source
- Utilizes specialed sub-agents to handle specific tasks, such as research, code exploration, code review, etc.  Sub-agents should be initialized with a fresh context window with instructions and relevant details from the parent agent.
- Automatically maintains a memory of project details so that it gets smarter over time, including:
  - Project structure and organization
  - Goals
  - What works and what doesn't work.  Lessons learned.
  - Previously completed changes/tasks and their results.
