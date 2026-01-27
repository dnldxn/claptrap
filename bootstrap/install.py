#!/usr/bin/env python3
"""
Claptrap Installer - Sets up AI agent workflows for your project.

Usage:
    cd /path/to/your/project
    python ~/projects/claptrap/bootstrap/install.py
"""

import re
import shutil
import subprocess
from pathlib import Path

# ============================================================================
# Pretty Output
# ============================================================================

class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def success(msg: str) -> None:
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def warning(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def info(msg: str) -> None:
    print(f"{Colors.CYAN}→{Colors.RESET} {msg}")

def header(msg: str) -> None:
    print(f"\n{Colors.BOLD}📦 {msg}{Colors.RESET}")

def step(num: int, msg: str) -> None:
    print(f"\n{Colors.BOLD}[{num}]{Colors.RESET} {msg}")

# ============================================================================
# Installation Configuration
# ============================================================================

GLOBAL_SKILLS = [
    {
        "repo": "https://github.com/anthropics/skills",
        "skill": "skill-creator",
    },
    {
        "repo": "https://github.com/anthropics/skills",
        "skill": "frontend-design",
    },
    # {
    #     "repo": "https://github.com/obra/superpowers",
    #     "skill": "writing-plans",
    # },
    # {
    #     "repo": "https://github.com/softaworks/agent-toolkit",
    #     "skill": "codex",
    # },
    # {
    #     "repo": "https://github.com/obra/superpowers",
    #     "skill": "brainstorming",
    # },
    # {
    #     "repo": "https://github.com/obra/superpowers",
    #     "skill": "subagent-driven-development",
    # },
]

MCP_SERVERS = ['serena', 'context7', 'snowflake']

# ============================================================================
# Provider Configuration (Data-Driven)
# ============================================================================

DEFAULT_PROVIDER = {
    "agents_dir": "agents",
    "commands_dir": "commands",
    "skills_dir": "skills",
    "agent_suffix": ".md",
    "command_suffix": ".md",
}

PROVIDERS = {
    "cursor": {
        "name": "Cursor",
        "dir": ".cursor",
        "mcp_cmd": ["agent", "mcp", "list"],
    },
    "github-copilot": {
        "name": "GitHub Copilot",
        "dir": ".github",
        "commands_dir": "prompts",
        "agent_suffix": ".agent.md",
        "command_suffix": ".prompt.md",
    },
    "opencode": {
        "name": "OpenCode",
        "dir": ".opencode",
        "mcp_cmd": ["opencode", "mcp", "list"],
    },
    "claude": {
        "name": "Claude",
        "dir": ".claude",
        "mcp_cmd": ["claude", "mcp", "list"],
    },
    "codex": {
        "name": "Codex",
        "dir": ".codex",
        "mcp_cmd": ["codex", "mcp", "list"],
    },
    "gemini": {
        "name": "Gemini",
        "dir": ".gemini",
        "mcp_cmd": ["gemini", "mcp", "list"],
    },
}

# Provider key order for menu display
PROVIDER_ORDER = ["opencode", "cursor", "github-copilot", "claude", "codex", "gemini"]

def get_provider(key: str) -> dict:
    """Get provider config merged with defaults."""
    return {**DEFAULT_PROVIDER, **PROVIDERS[key]}

# ============================================================================
# Helper Functions
# ============================================================================

def run_cmd(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run a command, optionally capturing output."""
    return subprocess.run(cmd, capture_output=capture, text=True, check=False)

def get_openspec_version() -> str | None:
    """Get installed openspec version, or None if not installed."""
    result = run_cmd(["npm", "list", "-g", "@fission-ai/openspec", "--depth=0"])
    if result.returncode == 0:
        match = re.search(r"@fission-ai/openspec@([\d.]+)", result.stdout)
        if match:
            return match.group(1)
    return None

def get_latest_openspec_version() -> str | None:
    """Get latest openspec version from npm."""
    result = run_cmd(["npm", "view", "@fission-ai/openspec", "version"])
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def select_provider() -> str:
    """Interactive provider selection menu."""
    print("\n🎯 Select your AI provider:\n")
    for i, key in enumerate(PROVIDER_ORDER, 1):
        cfg = get_provider(key)
        print(f"  {Colors.BOLD}{i}{Colors.RESET}) {cfg['name']} ({cfg['dir']})")
    
    print()
    while True:
        try:
            choice = input(f"Enter 1-{len(PROVIDER_ORDER)} [1]: ").strip() or "1"
            idx = int(choice) - 1
            if 0 <= idx < len(PROVIDER_ORDER):
                return PROVIDER_ORDER[idx]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nAborted.")
            raise SystemExit(1)
        print(f"Please enter a number between 1 and {len(PROVIDER_ORDER)}.")

def transform_frontmatter(content: str, provider_key: str) -> str:
    """Transform model: in frontmatter based on provider, remove models: block."""
    # Match YAML frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return content
    
    frontmatter = fm_match.group(1)
    rest = content[fm_match.end():]
    
    # Extract + remove models: block (line-based to handle varying indentation and missing trailing newline)
    models = {}
    frontmatter_lines = frontmatter.splitlines()
    kept_lines = []
    found_models_block = False

    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if re.match(r"^models:\s*$", line):
            found_models_block = True
            i += 1
            while i < len(frontmatter_lines) and re.match(r"^[ \t]+", frontmatter_lines[i]):
                model_line = frontmatter_lines[i]
                m = re.match(r"^[ \t]+(\S+):\s*(.+?)\s*$", model_line)
                if m:
                    models[m.group(1)] = m.group(2)
                i += 1
            continue

        kept_lines.append(line)
        i += 1

    if not found_models_block:
        return content

    # Get provider-specific model or keep default
    if provider_key in models:
        new_model = models[provider_key]
        # Replace model: line
        frontmatter = "\n".join(kept_lines)
        if re.search(r"^model:\s*.*$", frontmatter, flags=re.MULTILINE):
            frontmatter = re.sub(r"^model:\s*.*$", f"model: {new_model}", frontmatter, count=1, flags=re.MULTILINE)
        else:
            frontmatter = (frontmatter + "\n" if frontmatter else "") + f"model: {new_model}"
    else:
        frontmatter = "\n".join(kept_lines)
    
    return f"---\n{frontmatter.strip()}\n---{rest}"

def copy_and_transform(src_dir: Path, dest_dir: Path, provider_key: str, new_suffix: str) -> int:
    """Copy markdown files, transform frontmatter, apply suffix. Returns count."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    
    for src_file in src_dir.rglob("*.md"):
        # Skip AGENTS.md and README.md
        if src_file.name in ("AGENTS.md", "README.md"):
            continue
        
        # Compute relative path and new filename
        rel_path = src_file.relative_to(src_dir)
        
        # For files in subdirectories, preserve structure
        if len(rel_path.parts) > 1:
            new_name = rel_path.parts[-1]
            if new_suffix != ".md":
                new_name = new_name.replace(".md", new_suffix)
            dest_file = dest_dir / rel_path.parent / new_name
        else:
            new_name = src_file.stem + new_suffix
            dest_file = dest_dir / new_name
        
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Read, transform, write
        content = src_file.read_text()
        content = transform_frontmatter(content, provider_key)
        dest_file.write_text(content)
        count += 1
    
    return count

def copy_skills(src_dir: Path, dest_dir: Path) -> int:
    """Copy skills directory structure (no transformation needed). Returns count."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    
    for src_file in src_dir.rglob("*"):
        if src_file.is_file():
            # Skip AGENTS.md and README.md
            if src_file.name in ("AGENTS.md", "README.md"):
                continue
            
            rel_path = src_file.relative_to(src_dir)
            dest_file = dest_dir / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dest_file)
            count += 1
    
    return count

def cleanup_provider_dir(provider_dir: Path) -> None:
    """Remove AGENTS.md and README.md from provider directories (they confuse AI harnesses)."""
    for pattern in ("AGENTS.md", "README.md"):
        for f in provider_dir.rglob(pattern):
            f.unlink()
            info(f"Removed {f.relative_to(provider_dir.parent)}")

def update_gitignore(target_dir: Path) -> None:
    """Add provider directories to .gitignore if not present."""
    gitignore = target_dir / ".gitignore"
    
    entries = [
        ".claude/",
        ".codex/",
        ".cursor/",
        ".gemini/",
        ".github/",
        ".opencode/",
        ".claptrap/",
        ".serena/",
    ]
    
    existing = set()
    if gitignore.exists():
        existing = set(gitignore.read_text().splitlines())
    
    added = []
    with open(gitignore, "a") as f:
        for entry in entries:
            if entry not in existing:
                f.write(f"{entry}\n")
                added.append(entry)
    
    if added:
        success(f"Added to .gitignore: {', '.join(added)}")
    else:
        info(".gitignore already configured")

def update_agents_md(target_dir: Path, claptrap_path: Path) -> None:
    """Update AGENTS.md with claptrap content."""
    agents_md = target_dir / "AGENTS.md"
    template = claptrap_path / "bootstrap" / "templates" / "agents_md.txt"
    claptrap_content = template.read_text()
    
    if agents_md.exists():
        content = agents_md.read_text()
        # Check for existing claptrap block
        if "<!-- CLAPTRAP:START -->" in content:
            # Replace existing block
            content = re.sub(
                r"<!-- CLAPTRAP:START -->.*?<!-- CLAPTRAP:END -->",
                claptrap_content.strip(),
                content,
                flags=re.DOTALL
            )
            success("Updated existing CLAPTRAP section in AGENTS.md")
        else:
            # Append after OPENSPEC:END if it exists, otherwise at end
            if "<!-- OPENSPEC:END -->" in content:
                content = content.replace(
                    "<!-- OPENSPEC:END -->",
                    f"<!-- OPENSPEC:END -->\n\n{claptrap_content}"
                )
            else:
                content = content + "\n\n" + claptrap_content
            success("Added CLAPTRAP section to AGENTS.md")
        agents_md.write_text(content)
    else:
        agents_md.write_text(claptrap_content)
        success("Created AGENTS.md with CLAPTRAP section")

def check_ripgrep() -> bool:
    """Check if ripgrep is installed."""
    return shutil.which("rg") is not None

def check_mcp_server(provider_key: str, server_name: str) -> bool | None:
    """Check if an MCP server is configured. Returns None if can't check."""
    cfg = get_provider(provider_key)
    mcp_cmd = cfg.get("mcp_cmd")
    
    if not mcp_cmd: return None
    
    try:
        result = run_cmd(mcp_cmd)
        if result.returncode == 0:
            return server_name.lower() in result.stdout.lower()
    except FileNotFoundError: pass  # CLI not installed
    return None

def check_serena_mcp(provider_key: str) -> bool | None:
    """Check if Serena MCP is configured. Returns None if can't check."""
    return check_mcp_server(provider_key, "serena")

def install_global_skills() -> tuple[int, int]:
    """Install global skills from configured list. Returns (success_count, total_count)."""
    success_count = 0
    
    for skill in GLOBAL_SKILLS:
        info(f"Installing {skill['skill']} from {skill['repo']}...")
        result = run_cmd(["npx", "-y", "skills", "add", "--yes", "--global", skill["repo"], "--skill", skill["skill"]])
        if result.returncode == 0: success_count += 1
        else: warning(f"Failed to install {skill['skill']}")
    
    return success_count, len(GLOBAL_SKILLS)

# ============================================================================
# Main Installation
# ============================================================================

header("Claptrap Installer")

claptrap_path = Path(__file__).resolve().parent.parent
target_dir = Path.cwd()

info(f"Claptrap path: {claptrap_path}")
info(f"Target project: {target_dir}")

# Step 1: Select provider
step(1, "Provider Selection")
provider_key = select_provider()
cfg = get_provider(provider_key)
success(f"Selected: {cfg['name']} ({cfg['dir']})")

# Step 2: OpenSpec
step(2, "OpenSpec Installation")
current_version = get_openspec_version()
latest_version = get_latest_openspec_version()

if current_version:
    if latest_version and current_version == latest_version:
        success(f"OpenSpec v{current_version} is up to date")
    else:
        version_msg = f"v{current_version} → v{latest_version}" if latest_version else f"v{current_version} → latest"
        info(f"Upgrading OpenSpec: {version_msg}")
        result = run_cmd(["npm", "install", "-g", "@fission-ai/openspec@latest"])
        if result.returncode == 0:
            success(f"Upgraded to {f'v{latest_version}' if latest_version else 'latest'}")
        else:
            warning("Upgrade failed, continuing with current version")
else:
    version_msg = f"v{latest_version}" if latest_version else "latest"
    info(f"Installing OpenSpec ({version_msg})")
    result = run_cmd(["npm", "install", "-g", "@fission-ai/openspec@latest"])
    if result.returncode == 0:
        success(f"Installed OpenSpec ({version_msg})")
    else:
        warning("Installation failed - install manually: npm install -g @fission-ai/openspec@latest")

# Initialize or update openspec
openspec_dir = target_dir / "openspec"
if openspec_dir.exists():
    cmd = ["openspec", "update"]
    action = "updated"
    fallback = "run manually if needed"
else:
    cmd = ["openspec", "init", "--tools", provider_key]
    action = "initialized"
    fallback = f"run manually: openspec init --tools {provider_key}"

info(f"Running {' '.join(cmd)}...")
result = run_cmd(cmd, capture=False)
if result.returncode == 0: success(f"OpenSpec {action}")
else: warning(f"openspec {cmd[1]} failed (exit code {result.returncode}) - {fallback}")

# Step 3: Install global skills
step(3, "Installing Global Skills")
success_count, total_count = install_global_skills()
if success_count == total_count:
    success(f"Installed {success_count}/{total_count} global skills")
elif success_count > 0:
    warning(f"Installed {success_count}/{total_count} global skills (some failed)")
else:
    warning("No skills were installed successfully")

# Step 4: Create .claptrap directory
step(4, "Workflow Directory Setup")
workflow_dir = target_dir / ".claptrap"

# Code conventions
conv_src = claptrap_path / "src" / "code-conventions"
conv_dest = workflow_dir / "code-conventions"
conv_dest.mkdir(parents=True, exist_ok=True)
for f in conv_src.glob("*.md"): shutil.copy2(f, conv_dest / f.name)
success(f"Copied code conventions to {conv_dest.relative_to(target_dir)}")

# Design templates
designs_dest = workflow_dir / "designs"
designs_dest.mkdir(parents=True, exist_ok=True)
shutil.copy2(claptrap_path / "src" / "designs" / "TEMPLATE.md", designs_dest / "TEMPLATE.md")
example_src = claptrap_path / "src" / "designs" / "example-feature"
if example_src.exists(): shutil.copytree(example_src, designs_dest / "example-feature", dirs_exist_ok=True)
success(f"Copied design templates to {designs_dest.relative_to(target_dir)}")

# Memories
memories_file = workflow_dir / "memories.md"
if not memories_file.exists():
    memories_template = claptrap_path / "bootstrap" / "templates" / "memories_md.txt"
    shutil.copy2(memories_template, memories_file)
    success("Created memories.md")
else: info("memories.md already exists, skipping")

# Step 5: Copy agents, commands, skills
step(5, f"Installing to {cfg['dir']}")
provider_dir = target_dir / cfg["dir"]

# Agents
agents_count = copy_and_transform(
    claptrap_path / "src" / "agents",
    provider_dir / cfg["agents_dir"],
    provider_key,
    cfg["agent_suffix"],
)
success(f"Copied {agents_count} agents → {cfg['agents_dir']}/")

# Commands
commands_count = copy_and_transform(
    claptrap_path / "src" / "commands",
    provider_dir / cfg["commands_dir"],
    provider_key,
    cfg["command_suffix"],
)
success(f"Copied {commands_count} commands → {cfg['commands_dir']}/")

# Skills
skills_count = copy_skills(claptrap_path / "src" / "skills", provider_dir / cfg["skills_dir"])
success(f"Copied {skills_count} skill files → {cfg['skills_dir']}/")

# Clean up AGENTS.md/README.md from provider dir (they confuse AI harnesses)
cleanup_provider_dir(provider_dir)

# Step 6: Update .gitignore
step(6, "Configuring .gitignore")
update_gitignore(target_dir)

# Step 7: Update AGENTS.md
step(7, "Updating AGENTS.md")
update_agents_md(target_dir, claptrap_path)

# Step 8: Check tools
step(8, "Checking Tools")

# ripgrep
if check_ripgrep(): success("ripgrep (rg) is installed")
else: warning("ripgrep not found - install from https://github.com/BurntSushi/ripgrep")

# Step 9: Check MCP servers
step(9, "Checking MCP Servers")

for server in MCP_SERVERS:
    status = check_mcp_server(provider_key, server)
    if status is True:
        success(f"{server} MCP is configured")
    elif status is False:
        warning(f"{server} MCP not configured")
        print(f"\n  {Colors.DIM}To install, ask your AI assistant:{Colors.RESET}")
    else:
        info(f"Could not check {server} MCP status for {cfg['name']}")

# Done
header("Installation Complete! 🎉")
print(f"\n  Provider: {Colors.BOLD}{cfg['name']}{Colors.RESET}")
print(f"  Config:   {Colors.CYAN}{cfg['dir']}/{Colors.RESET}")
print(f"  Workflow: {Colors.CYAN}.claptrap/{Colors.RESET}")
print()
