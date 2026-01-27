#!/usr/bin/env python3
# Claptrap Installer - Sets up AI agent workflows for your project.
# Usage: cd /path/to/your/project && python ~/projects/claptrap/bootstrap/install.py

import re
import shutil
import subprocess
from pathlib import Path

########################################################################################################################
# Pretty Output
########################################################################################################################


class Colors:
    GREEN, YELLOW, CYAN, RED, BOLD, DIM, RESET = (
        "\033[92m",
        "\033[93m",
        "\033[96m",
        "\033[91m",
        "\033[1m",
        "\033[2m",
        "\033[0m",
    )


def success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")


def info(msg):
    print(f"{Colors.CYAN}→{Colors.RESET} {msg}")


def header(msg):
    print(f"\n{Colors.BOLD}📦 {msg}{Colors.RESET}")


def step(num, msg):
    print(f"\n{Colors.BOLD}[{num}]{Colors.RESET} {msg}")


########################################################################################################################
# Installation Configuration
########################################################################################################################

GLOBAL_SKILLS = [
    {"repo": "https://github.com/anthropics/skills", "skill": "skill-creator"},
    {"repo": "https://github.com/anthropics/skills", "skill": "frontend-design"},
    {"repo": "https://github.com/obra/superpowers", "skill": "brainstorming"},
]

MCP_SERVERS = ["serena", "context7", "snowflake"]

########################################################################################################################
# Provider Configuration
########################################################################################################################

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
        "global_dir": Path.home() / ".cursor",
        "has_agents": True,
        "has_commands": True,
        "has_skills": False,
        "mcp_cmd": ["agent", "mcp", "list"],
    },
    "github-copilot": {
        "name": "GitHub Copilot",
        "dir": ".github",
        "commands_dir": "prompts",
        "agent_suffix": ".agent.md",
        "command_suffix": ".prompt.md",
        "has_agents": True,
        "has_commands": True,
        "has_skills": False,
    },
    "opencode": {
        "name": "OpenCode",
        "dir": ".opencode",
        "global_dir": Path.home() / ".config" / "opencode",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "mcp_cmd": ["opencode", "mcp", "list"],
    },
    "claude": {
        "name": "Claude",
        "dir": ".claude",
        "global_dir": Path.home() / ".claude",
        "has_agents": True,
        "has_commands": True,
        "has_skills": True,
        "mcp_cmd": ["claude", "mcp", "list"],
    },
    "codex": {
        "name": "Codex",
        "dir": ".codex",
        "global_dir": Path.home() / ".codex",
        "has_agents": False,
        "has_commands": False,
        "has_skills": True,
        "mcp_cmd": ["codex", "mcp", "list"],
    },
    "gemini": {
        "name": "Gemini",
        "dir": ".gemini",
        "global_dir": Path.home() / ".gemini",
        "has_agents": False,
        "has_commands": True,
        "has_skills": False,
        "commands_format": "toml",
        "mcp_cmd": ["gemini", "mcp", "list"],
    },
}

# Provider key order for menu display
PROVIDER_ORDER = ["opencode", "cursor", "github-copilot", "claude", "codex", "gemini"]


def get_provider(key):
    return {**DEFAULT_PROVIDER, **PROVIDERS[key]}


def get_provider_display_dir(cfg):
    return str(cfg["global_dir"]) if cfg.get("global_dir") else cfg["dir"]


########################################################################################################################
# Helper Functions
########################################################################################################################


def run_cmd(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True, check=False)


def get_openspec_version():
    result = run_cmd(["npm", "list", "-g", "@fission-ai/openspec", "--depth=0"])
    if result.returncode != 0:
        return None
    match = re.search(r"@fission-ai/openspec@([\d.]+)", result.stdout)
    return match.group(1) if match else None


def get_latest_openspec_version():
    result = run_cmd(["npm", "view", "@fission-ai/openspec", "version"])
    return result.stdout.strip() if result.returncode == 0 else None


def install_or_upgrade_openspec():
    current = get_openspec_version()
    latest = get_latest_openspec_version()

    if current:
        if latest and current == latest:
            success(f"OpenSpec v{current} is up to date")
            return True
        version_msg = f"v{current} → v{latest}" if latest else f"v{current} → latest"
        info(f"Upgrading OpenSpec: {version_msg}")
    else:
        version_msg = f"v{latest}" if latest else "latest"
        info(f"Installing OpenSpec ({version_msg})")

    result = run_cmd(["npm", "install", "-g", "@fission-ai/openspec@latest"])
    if result.returncode == 0:
        action = "Upgraded to" if current else "Installed OpenSpec"
        success(f"{action} {f'v{latest}' if latest else 'latest'}")
        return True

    msg = (
        "Upgrade failed, continuing with current version"
        if current
        else "Installation failed - install manually: npm install -g @fission-ai/openspec@latest"
    )
    warning(msg)
    return False


def init_or_update_openspec_project(project_dir, provider_key):
    openspec_dir = project_dir / "openspec"
    if openspec_dir.exists():
        cmd, action, fallback = (
            ["openspec", "update"],
            "updated",
            "run manually if needed",
        )
    else:
        cmd, action, fallback = (
            ["openspec", "init", "--tools", provider_key],
            "initialized",
            f"run manually: openspec init --tools {provider_key}",
        )

    info(f"Running {' '.join(cmd)}...")
    result = run_cmd(cmd, capture=False)
    if result.returncode == 0:
        success(f"OpenSpec {action}")
        return True
    warning(f"openspec {cmd[1]} failed (exit code {result.returncode}) - {fallback}")
    return False


def select_provider():
    print("\n🎯 Select your AI provider:\n")
    for i, key in enumerate(PROVIDER_ORDER, 1):
        cfg = get_provider(key)
        print(f"  {Colors.BOLD}{i}{Colors.RESET}) {cfg['name']} ({get_provider_display_dir(cfg)})")

    print()
    while True:
        try:
            choice = input(f"Enter 1-{len(PROVIDER_ORDER)} [1]: ").strip() or "1"
            idx = int(choice) - 1
            if 0 <= idx < len(PROVIDER_ORDER):
                return PROVIDER_ORDER[idx]
        except ValueError: pass
        except KeyboardInterrupt:
            print("\nAborted.")
            raise SystemExit(1)
        print(f"Please enter a number between 1 and {len(PROVIDER_ORDER)}.")


def get_provider_root_dir(provider_key):
    cfg = get_provider(provider_key)
    return cfg["global_dir"] if cfg.get("global_dir") else target_dir / cfg["dir"]


def get_install_dir(provider_key, feature):
    cfg = get_provider(provider_key)
    return get_provider_root_dir(provider_key) / cfg[f"{feature}_dir"]


def can_install_feature(cfg, feature):
    if not cfg.get(f"has_{feature}"): return False, "not supported"
    if feature == "commands" and cfg.get("commands_format") == "toml":
        return False, "requires TOML format (manual setup)"
    return True, None


def transform_frontmatter(content, provider_key):
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match: return content

    frontmatter = fm_match.group(1)
    rest = content[fm_match.end() :]

    # Extract models: block
    models = {}
    frontmatter_lines = frontmatter.splitlines()
    kept_lines = []
    i = 0

    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if re.match(r"^models:\s*$", line):
            i += 1
            while i < len(frontmatter_lines) and re.match(
                r"^[ \t]+", frontmatter_lines[i]
            ):
                m = re.match(r"^[ \t]+(\S+):\s*(.+?)\s*$", frontmatter_lines[i])
                if m:
                    models[m.group(1)] = m.group(2)
                i += 1
            continue
        kept_lines.append(line)
        i += 1

    if not models: return content

    frontmatter = "\n".join(kept_lines)

    # Update model: line if provider-specific model exists
    if provider_key in models:
        new_model = models[provider_key]
        if re.search(r"^model:\s*.*$", frontmatter, re.MULTILINE):
            frontmatter = re.sub(
                r"^model:\s*.*$",
                f"model: {new_model}",
                frontmatter,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            frontmatter = (
                frontmatter + "\n" if frontmatter else ""
            ) + f"model: {new_model}"

    return f"---\n{frontmatter.strip()}\n---{rest}"


def copy_and_transform(src_dir, dest_dir, provider_key, new_suffix):
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for src_file in src_dir.rglob("*.md"):
        if src_file.name in ("AGENTS.md", "README.md"): continue

        rel_path = src_file.relative_to(src_dir)

        # Preserve subdirectory structure
        if len(rel_path.parts) > 1:
            new_name = (
                rel_path.parts[-1].replace(".md", new_suffix)
                if new_suffix != ".md"
                else rel_path.parts[-1]
            )
            dest_file = dest_dir / rel_path.parent / new_name
        else:
            dest_file = dest_dir / (src_file.stem + new_suffix)

        dest_file.parent.mkdir(parents=True, exist_ok=True)
        if dest_file.is_symlink(): dest_file.unlink()

        content = transform_frontmatter(src_file.read_text(), provider_key)
        dest_file.write_text(content)
        count += 1

    return count


def copy_skills(src_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for src_file in src_dir.rglob("*"):
        if not src_file.is_file() or src_file.name in ("AGENTS.md", "README.md"):
            continue

        rel_path = src_file.relative_to(src_dir)
        dest_file = dest_dir / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        count += 1

    return count


def cleanup_feature_dirs(feature_dirs):
    for feature_dir in feature_dirs:
        if not feature_dir.exists(): continue
        for pattern in ("AGENTS.md", "README.md"):
            for f in feature_dir.rglob(pattern):
                f.unlink()
                info(f"Removed {f.relative_to(feature_dir.parent)}")


def update_gitignore(target_dir):
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

    existing = set(gitignore.read_text().splitlines()) if gitignore.exists() else set()

    added = []
    with open(gitignore, "a") as f:
        for entry in entries:
            if entry not in existing:
                f.write(f"{entry}\n")
                added.append(entry)

    success(f"Added to .gitignore: {', '.join(added)}") if added else info(".gitignore already configured")


def find_legacy_provider_dirs(target_dir):
    legacy_dirs = {}
    for provider_key in PROVIDERS:
        cfg = get_provider(provider_key)
        if "global_dir" not in cfg:
            continue

        provider_dir = target_dir / cfg["dir"]
        feature_dirs = [
            feature_dir
            for feature in ("agents", "commands", "skills")
            if (feature_dir := provider_dir / cfg[f"{feature}_dir"]).exists()
        ]
        if feature_dirs: legacy_dirs[provider_key] = feature_dirs

    return legacy_dirs


def update_agents_md(agents_md_path, claptrap_path):
    agents_md_path.parent.mkdir(parents=True, exist_ok=True)
    template = claptrap_path / "bootstrap" / "templates" / "agents_md.txt"
    claptrap_content = template.read_text()

    if agents_md_path.exists():
        content = agents_md_path.read_text()
        if "<!-- CLAPTRAP:START -->" in content:
            content = re.sub(
                r"<!-- CLAPTRAP:START -->.*?<!-- CLAPTRAP:END -->",
                claptrap_content.strip(),
                content,
                flags=re.DOTALL,
            )
            success(f"Updated existing CLAPTRAP section in {agents_md_path}")
        else:
            insert_after = (
                "<!-- OPENSPEC:END -->\n\n"
                if "<!-- OPENSPEC:END -->" in content
                else ""
            )
            content = (
                content.replace(
                    "<!-- OPENSPEC:END -->",
                    f"<!-- OPENSPEC:END -->\n\n{claptrap_content}",
                )
                if insert_after
                else content + "\n\n" + claptrap_content
            )
            success(f"Added CLAPTRAP section to {agents_md_path}")
        agents_md_path.write_text(content)
    else:
        agents_md_path.write_text(claptrap_content)
        success(f"Created {agents_md_path} with CLAPTRAP section")


def check_ripgrep():
    return shutil.which("rg") is not None


def check_mcp_server(provider_key, server_name):
    cfg = get_provider(provider_key)
    mcp_cmd = cfg.get("mcp_cmd")
    if not mcp_cmd: return None

    try:
        result = run_cmd(mcp_cmd)
        if result.returncode == 0:
            return server_name.lower() in result.stdout.lower()
    except FileNotFoundError: pass

    return None


def install_global_skills():
    success_count = 0
    for skill in GLOBAL_SKILLS:
        info(f"Installing {skill['skill']} from {skill['repo']}...")
        result = run_cmd(
            [
                "npx",
                "-y",
                "skills",
                "add",
                "--yes",
                "--global",
                skill["repo"],
                "--skill",
                skill["skill"],
            ]
        )
        if result.returncode == 0: success_count += 1
        else: warning(f"Failed to install {skill['skill']}")
    return success_count, len(GLOBAL_SKILLS)


def install_feature(feature_name, cfg, provider_key, claptrap_path, copy_func):
    can_install, reason = can_install_feature(cfg, feature_name)
    if not can_install:
        warning(f"Skipping {feature_name} for {cfg['name']} - {reason}")
        return None, 0

    dest_dir = get_install_dir(provider_key, feature_name)
    src_dir = claptrap_path / "src" / feature_name

    if feature_name == "skills":
        count = copy_func(src_dir, dest_dir)
    else:
        suffix = cfg[f"{feature_name.rstrip('s')}_suffix"]
        count = copy_func(src_dir, dest_dir, provider_key, suffix)

    success(f"Copied {count} {feature_name} → {dest_dir}")
    return dest_dir, count


########################################################################################################################
# Main Installation
########################################################################################################################

header("Claptrap Installer")

claptrap_path = Path(__file__).resolve().parent.parent
target_dir = Path.cwd()

info(f"Claptrap path: {claptrap_path}")
info(f"Target project: {target_dir}")

# Step 1: Select provider
step(1, "Provider Selection")
provider_key = select_provider()
cfg = get_provider(provider_key)
success(f"Selected: {cfg['name']} ({get_provider_display_dir(cfg)})")

# Step 2: OpenSpec
step(2, "OpenSpec Installation")
install_or_upgrade_openspec()
init_or_update_openspec_project(target_dir, provider_key)

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
conv_dest = workflow_dir / "code-conventions"
conv_dest.mkdir(parents=True, exist_ok=True)
for f in (claptrap_path / "src" / "code-conventions").glob("*.md"):
    shutil.copy2(f, conv_dest / f.name)
success(f"Copied code conventions to {conv_dest.relative_to(target_dir)}")

# Design templates
designs_dest = workflow_dir / "designs"
designs_dest.mkdir(parents=True, exist_ok=True)
shutil.copy2(
    claptrap_path / "src" / "designs" / "TEMPLATE.md", designs_dest / "TEMPLATE.md"
)
example_src = claptrap_path / "src" / "designs" / "example-feature"
if example_src.exists():
    shutil.copytree(example_src, designs_dest / "example-feature", dirs_exist_ok=True)
success(f"Copied design templates to {designs_dest.relative_to(target_dir)}")

# Memories
memories_file = workflow_dir / "memories.md"
if not memories_file.exists():
    shutil.copy2(claptrap_path / "bootstrap" / "templates" / "memories_md.txt", memories_file)
    success("Created memories.md")
else:
    info("memories.md already exists, skipping")

# Step 5: Copy agents, commands, skills
provider_root_dir = get_provider_root_dir(provider_key)
step(5, f"Installing to {provider_root_dir}")

installed_dirs = []
for feature, copy_func in [
    ("agents", copy_and_transform),
    ("commands", copy_and_transform),
    ("skills", copy_skills),
]:
    dest_dir, _ = install_feature(feature, cfg, provider_key, claptrap_path, copy_func)
    if dest_dir: installed_dirs.append(dest_dir)

cleanup_feature_dirs(installed_dirs)

# Step 6: Update .gitignore
step(6, "Configuring .gitignore")
update_gitignore(target_dir)

# Step 7: Update AGENTS.md
step(7, "Updating AGENTS.md")
if cfg.get("global_dir"): update_agents_md(cfg["global_dir"] / "AGENTS.md", claptrap_path)

# Step 8: Check tools
step(8, "Checking Tools")
success("ripgrep (rg) is installed") if check_ripgrep() else warning(
    "ripgrep not found - install from https://github.com/BurntSushi/ripgrep"
)

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
print(f"  Config:   {Colors.CYAN}{get_provider_display_dir(cfg)}/{Colors.RESET}")
print(f"  Workflow: {Colors.CYAN}.claptrap/{Colors.RESET}")
print()
