#!/usr/bin/env python3
# Claptrap Installer - Installs agents, commands, skills to all environments.
#
# Usage: python bootstrap/install.py [--env ENV]
#
# Options:
#     --env ENV    Install only to specified environment (default: all)

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib import installer, memory
from lib.output import BOLD, CYAN, RESET, header, info, step, success, warning

GLOBAL_SKILLS = [
    ("https://github.com/anthropics/skills", "skill-creator"),
    ("https://github.com/anthropics/skills", "frontend-design"),
    ("https://github.com/forrestchang/andrej-karpathy-skills", "karpathy-guidelines"),
]

MCP_SERVERS = ["serena", "context7", "snowflake"]


def run_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def select_environment():
    # Prompt user to select environment or install to all.
    envs = list(installer.CONFIG["environments"].keys())

    print("\nSelect installation target:\n")
    print(f"  {BOLD}0{RESET}) All environments")
    for i, env in enumerate(envs, 1):
        root = Path(installer.CONFIG["environments"][env]["root"]).expanduser()
        print(f"  {BOLD}{i}{RESET}) {env} ({root})")
    print()

    while True:
        try:
            choice = input(f"Enter 0-{len(envs)} [0]: ").strip() or "0"
            idx = int(choice)
            if idx == 0:
                return None
            if 1 <= idx <= len(envs):
                return envs[idx - 1]
        except ValueError:
            pass
        except KeyboardInterrupt:
            print("\nAborted.")
            raise SystemExit(1)
        print(f"Please enter a number between 0 and {len(envs)}.")


def install_global_skills():
    # Install global skills via npx.
    success_count = 0
    for repo, skill in GLOBAL_SKILLS:
        info(f"Installing {skill} from {repo}...")
        result = run_cmd(
            ["npx", "-y", "skills", "add", "--yes", "--global", repo, "--skill", skill]
        )
        if result.returncode == 0:
            success_count += 1
        else:
            warning(f"Failed to install {skill}")
    return success_count, len(GLOBAL_SKILLS)


def setup_workflow_dir(target_dir: Path, claptrap_path: Path):
    # Create .claptrap directory with code conventions and design templates.
    workflow_dir = target_dir / ".claptrap"

    conv_dest = workflow_dir / "code-conventions"
    conv_dest.mkdir(parents=True, exist_ok=True)
    for f in (claptrap_path / "src" / "code-conventions").glob("*.md"):
        shutil.copy2(f, conv_dest / f.name)
    success(f"Copied code conventions -> {conv_dest.relative_to(target_dir)}")

    designs_dest = workflow_dir / "designs"
    designs_dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        claptrap_path / "src" / "designs" / "TEMPLATE.md",
        designs_dest / "TEMPLATE.md",
    )
    example_src = claptrap_path / "src" / "designs" / "example-feature"
    if example_src.exists():
        shutil.copytree(
            example_src, designs_dest / "example-feature", dirs_exist_ok=True
        )
    success(f"Copied design templates -> {designs_dest.relative_to(target_dir)}")

    return workflow_dir


def update_gitignore(target_dir: Path):
    # Add standard entries to .gitignore.
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

    added = [e for e in entries if e not in existing]
    if added:
        with open(gitignore, "a") as f:
            f.write("\n".join(added) + "\n")
        success(f"Added to .gitignore: {', '.join(added)}")
    else:
        info(".gitignore already configured")


def check_mcp_server(server_name: str) -> bool | None:
    # Check if MCP server is available.
    for cmd in [["opencode", "mcp", "list"], ["claude", "mcp", "list"]]:
        try:
            result = run_cmd(cmd)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if server_name.lower() in line.lower():
                        return "failed" not in line.lower()
                return False
        except FileNotFoundError:
            continue
    return None


def install_to_environment(env: str, claptrap_path: Path):
    # Install agents, commands, skills to a single environment.
    env_cfg = installer.CONFIG["environments"][env]
    root = Path(env_cfg["root"]).expanduser()

    info(f"Installing to {env} ({root})")

    installer.cleanup(root)

    src_root = claptrap_path / installer.CONFIG["source_dir"]
    staging = root / "claptrap"

    for feature in ["agents", "commands", "skills"]:
        feat_cfg = installer.get_feature_config(env_cfg, feature)
        if feat_cfg is None:
            info(f"  Skipping {feature} (not supported)")
            continue

        is_skill = feature == "skills"
        suffix = ".md" if is_skill else feat_cfg.get("suffix", ".md")
        feature_dir = root / feat_cfg.get("dir", feature)

        count = installer.install_feature(
            src_dir=src_root / feature,
            staging_dir=staging / feature,
            feature_dir=feature_dir,
            suffix=suffix,
            env=env,
            is_skill=is_skill,
        )
        success(f"  Installed {count} {feature} -> {feature_dir}")

    return root


def main():
    header("Claptrap Installer")

    claptrap_path = Path(__file__).resolve().parent.parent
    target_dir = Path.cwd()

    info(f"Claptrap path: {claptrap_path}")
    info(f"Target project: {target_dir}")

    step(1, "Environment Selection")
    selected_env = select_environment()
    if selected_env:
        success(f"Selected: {selected_env}")
        envs_to_install = [selected_env]
    else:
        success("Installing to all environments")
        envs_to_install = list(installer.CONFIG["environments"].keys())

    step(2, "Installing Global Skills")
    success_count, total_count = install_global_skills()
    if success_count == total_count:
        success(f"Installed {success_count}/{total_count} global skills")
    elif success_count > 0:
        warning(f"Installed {success_count}/{total_count} global skills (some failed)")
    else:
        warning("No skills were installed successfully")

    step(3, "Workflow Directory Setup")
    setup_workflow_dir(target_dir, claptrap_path)

    step(4, "Memory System Setup")
    for env in envs_to_install:
        memory.install(env, target_dir, claptrap_path)
        break

    step(5, "Installing Features")
    for env in envs_to_install:
        install_to_environment(env, claptrap_path)

    step(6, "Configuring .gitignore")
    update_gitignore(target_dir)

    step(7, "Checking MCP Servers")
    for server in MCP_SERVERS:
        status = check_mcp_server(server)
        if status is True:
            success(f"{server} MCP is configured")
        elif status is False:
            warning(f"{server} MCP not configured")
        else:
            info(f"Could not check {server} MCP status")

    header("Installation Complete!")
    print(f"\n  Environments: {BOLD}{', '.join(envs_to_install)}{RESET}")
    print(f"  Workflow:     {CYAN}.claptrap/{RESET}")
    print(f"  Memory:       {CYAN}.claptrap/memory_inbox.md, memories.md{RESET}")
    print()


if __name__ == "__main__":
    main()
