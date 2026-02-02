# TODO

- Add plan review + approval after the brainstorming step
    - Spawn 2-3 subagents to review (GPT-5.2 High and Gemini/Kimi).  Have the main agent summarize their feedback and decide whether to approve or request changes.
    - Use the existing `plan_reviewer.md` agent (might have to move it to a SKILL)

Example prompt for the plan review subagents:
```
Read @ai-provider-usage-monitor/docs/plans/2026-01-31-server-foundation-poc-design.md .  Do you have any thoughts, feedback, or criticism?
```

Example prompt for the main agent to summarize feedback and decide:
```
Read the plan @docs/plans/2026-01-31-server-foundation-poc-design.md. What do you think of the feedback below from a plan review?  What points do you agree with and which do you not? Why or why not? Which might not be a concern for the first PoC, but should be addressed later?
```


- Brainstorm and implement an implement + review + fix looping process
- Add best practices and rules for querying tables in the Snowflake Skill

In `bootstrap/install.py`:
- Install the specified provider's CLI tool (e.g. `npm install -g @github/copilot`)
- Install/configure MCPs for the selected provider by using `mcp_setup.md`

- Update GOALS