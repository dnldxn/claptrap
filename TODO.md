# TODO

- Move commands to skills (use installed "skill-creator" Skill)
- Add best practices and rules for querying tables in the Snowflake Skill

In `bootstrap/install.py`:
- Copy Agents, Skills, and Commands to the provider's global directory
- Install the specified provider's CLI tool (e.g. `npm install -g @github/copilot`)
- Don't reinstall OpenSpec if the current version is the latest
- Install/configure MCPs for the selected provider by using `mcp_setup.md`
- Simplify main by extracting functions to helper functions
