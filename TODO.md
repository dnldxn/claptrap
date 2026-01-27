# TODO

- Rework `/brainstorm`
    - Utilize the installed third-party "brainstor" Skill
    - Init an OpenSpec change using their tools
    - Create OpenSpec formatted `proposal.md` in the `openspec/changes/<change-name>/` directory
- Move commands to skills (use installed "skill-creator" Skill)
- Add best practices and rules for querying tables in the Snowflake Skill

In `bootstrap/install.py`:
- Copy Agents, Skills, and Commands to the provider's global directory
- Install the specified provider's CLI tool (e.g. `npm install -g @github/copilot`)
- Don't reinstall OpenSpec if the current version is the latest
- Install/configure MCPs for the selected provider by using `mcp_setup.md`
- Simplify main by extracting functions to helper functions
