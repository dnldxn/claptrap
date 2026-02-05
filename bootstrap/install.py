#!/usr/bin/env python3
# Claptrap Installer - Sets up AI agent workflows for your project.
# Usage: cd /path/to/your/project && python ~/projects/claptrap/bootstrap/install.py

import re
import shutil
import subprocess
from pathlib import Path

# Add bootstrap dir to path for lib imports
import sys

sys.path.insert(0, str(Path(__file__).parent))

from lib import frontmatter
from lib import memory
from lib import providers
from lib.output import BOLD, CYAN, DIM, RESET, header, info, step, success, warning


########################################################################################################################
# Installation Configuration
########################################################################################################################

GLOBAL_SKILLS = [
    {"repo": "https://github.com/anthropics/skills", "skill": "skill-creator"},
    {"repo": "https://github.com/anthropics/skills", "skill": "frontend-design"},
    {
        "repo": "https://github.com/forrestchang/andrej-karpathy-skills",
        "skill": "karpathy-guidelines",
    },
    # {"repo": "https://github.com/softaworks/agent-toolkit", "skill": "codex"},
    # {"repo": "https://github.com/softaworks/agent-toolkit", "skill": "gemini"},
    # {"repo": "https://github.com/softaworks/agent-toolkit", "skill": "mermaid-diagrams"},
    # {"repo": "https://github.com/obra/superpowers", "skill": "subagent-driven-development"},
    # {"repo": "https://github.com/jezweb/claude-skills", "skill": "streamlit-snowflake"},
]

MCP_SERVERS = ["serena", "context7", "snowflake"]

########################################################################################################################
# Helper Functions
########################################################################################################################


def run_cmd(cmd, capture=True):
    return subprocess.run(cmd, capture_output=capture, text=True, check=False)


def select_provider():
    print("\n🎯 Select your AI provider:\n")
    for i, key in enumerate(providers.PROVIDER_ORDER, 1):
        cfg = providers.get(key)
        print(f"  {BOLD}{i}{RESET}) {cfg['name']} ({providers.get_display_dir(cfg)})")

    print()
    while True:
        try:
            choice = (
                input(f"Enter 1-{len(providers.PROVIDER_ORDER)} [1]: ").strip() or "1"
            )
            idx = int(choice) - 1
            if 0 <= idx < len(providers.PROVIDER_ORDER):
                return providers.PROVIDER_ORDER[idx]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nAborted.")
            raise SystemExit(1)
        print(f"Please enter a number between 1 and {len(providers.PROVIDER_ORDER)}.")


def copy_and_transform(src_dir, dest_dir, provider_key, new_suffix):
    dest_dir.mkdir(parents=True, exist_ok=True)
    count = 0

    for src_file in src_dir.rglob("*.md"):
        if src_file.name in ("AGENTS.md", "README.md"):
            continue

        rel_path = src_file.relative_to(src_dir)
        if rel_path.parts[0] == "templates" or "_archive" in rel_path.parts:
            continue

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
        if dest_file.is_symlink():
            dest_file.unlink()

        content = frontmatter.transform_models(src_file.read_text(), provider_key)
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
        if "_archive" in rel_path.parts:
            continue

        dest_file = dest_dir / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        count += 1

    return count


def cleanup_feature_dirs(feature_dirs):
    for feature_dir in feature_dirs:
        if not feature_dir.exists():
            continue
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

    if added:
        success(f"Added to .gitignore: {', '.join(added)}")
    else:
        info(".gitignore already configured")


def update_agents_md(agents_md_path, claptrap_path, provider_key):
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

    if "claude" in provider_key.lower():
        setup_claude_md()


def setup_claude_md():
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    claude_md.parent.mkdir(parents=True, exist_ok=True)
    content = claude_md.read_text() if claude_md.exists() else ""
    if "@~/.claude/AGENTS.md" not in content:
        claude_md.write_text("@~/.claude/AGENTS.md\n\n---\n\n" + content)
        success(f"Added @~/.claude/AGENTS.md to {claude_md}")


def check_ripgrep():
    return shutil.which("rg") is not None


def check_mcp_server(provider_key, server_name):
    cfg = providers.get(provider_key)
    mcp_cmd = cfg.get("mcp_cmd")
    if not mcp_cmd:
        return None

    try:
        result = run_cmd(mcp_cmd)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if server_name.lower() in line.lower():
                    return False if "failed" in line.lower() else True
            return False
    except FileNotFoundError:
        pass

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
        if result.returncode == 0:
            success_count += 1
        else:
            warning(f"Failed to install {skill['skill']}")
    return success_count, len(GLOBAL_SKILLS)


def generate_debate_agents(claptrap_path, agents_dir):
    template_path = claptrap_path / "src" / "agents" / "templates" / "debate-agent.md"
    content = template_path.read_text()
    models = frontmatter.get_key(content, "debate-models")
    if not models:
        return
    content = frontmatter.set_key(content, "debate-models", None)

    agents_dir.mkdir(parents=True, exist_ok=True)
    for i, model in enumerate(models, 1):
        agent_content = content.replace("{NAME}", str(i)).replace("{MODEL}", model)
        (agents_dir / f"debate-agent-{i}.md").write_text(agent_content)

    success(f"Generated {len(models)} debate agents → {agents_dir}")


def install_feature(
    feature_name, cfg, provider_key, claptrap_path, target_dir, copy_func
):
    can_install, reason = providers.can_install_feature(cfg, feature_name)
    if not can_install:
        warning(f"Skipping {feature_name} for {cfg['name']} - {reason}")
        return None, 0

    dest_dir = providers.get_install_dir(provider_key, feature_name, target_dir)
    src_dir = claptrap_path / "src" / feature_name

    if feature_name == "skills":
        count = copy_func(src_dir, dest_dir)
    else:
        count = copy_func(
            src_dir, dest_dir, provider_key, cfg[f"{feature_name.rstrip('s')}_suffix"]
        )

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
cfg = providers.get(provider_key)
success(f"Selected: {cfg['name']} ({providers.get_display_dir(cfg)})")

# Step 2: Install global skills
step(2, "Installing Global Skills")
success_count, total_count = install_global_skills()
if success_count == total_count:
    success(f"Installed {success_count}/{total_count} global skills")
elif success_count > 0:
    warning(f"Installed {success_count}/{total_count} global skills (some failed)")
else:
    warning("No skills were installed successfully")

# Step 3: Create .claptrap directory with code conventions and design templates
step(3, "Workflow Directory Setup")
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

# Step 4: Memory system (inbox, memories, enforcement, hooks)
step(4, "Memory System Setup")
memory.install(provider_key, target_dir, claptrap_path)

# Step 5: Copy agents, commands, skills
provider_root_dir = providers.get_root_dir(provider_key, target_dir)
step(5, f"Installing to {provider_root_dir}")

installed_dirs = []
for feature, copy_func in [
    ("agents", copy_and_transform),
    ("commands", copy_and_transform),
    ("skills", copy_skills),
]:
    dest_dir, _ = install_feature(
        feature, cfg, provider_key, claptrap_path, target_dir, copy_func
    )
    if dest_dir:
        installed_dirs.append(dest_dir)

# Generate debate agents from template (OpenCode only)
if provider_key == "opencode" and cfg.get("has_agents"):
    generate_debate_agents(
        claptrap_path, providers.get_install_dir(provider_key, "agents", target_dir)
    )

cleanup_feature_dirs(installed_dirs)

# Step 6: Update .gitignore
step(6, "Configuring .gitignore")
update_gitignore(target_dir)

# Step 7: Update AGENTS.md
step(7, "Updating AGENTS.md")
if cfg.get("global_dir"):
    update_agents_md(cfg["global_dir"] / "AGENTS.md", claptrap_path, provider_key)

# Step 8: Check tools
step(8, "Checking Tools")
if check_ripgrep():
    success("ripgrep (rg) is installed")
else:
    warning("ripgrep not found - install from https://github.com/BurntSushi/ripgrep")

# Step 9: Check MCP servers
step(9, "Checking MCP Servers")
for server in MCP_SERVERS:
    status = check_mcp_server(provider_key, server)
    if status is True:
        success(f"{server} MCP is configured")
    elif status is False:
        warning(f"{server} MCP not configured")
        print(f"\n  {DIM}To install, ask your AI assistant:{RESET}")
    else:
        info(f"Could not check {server} MCP status for {cfg['name']}")

# Done
header("Installation Complete! 🎉")
print(f"\n  Provider: {BOLD}{cfg['name']}{RESET}")
print(f"  Config:   {CYAN}{providers.get_display_dir(cfg)}/{RESET}")
print(f"  Workflow: {CYAN}.claptrap/{RESET}")
print(f"  Memory:   {CYAN}.claptrap/memory_inbox.md, memories.md{RESET}")
print()
