#!/usr/bin/env python3
# Claptrap Installer - Installs agents, commands, skills to all environments.
#
# Usage: python bootstrap/install.py [--env ENV]
#
# Options:
#     --env ENV    Install only to specified environment (default: all)

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lib import installer, mcp, memory, verify
from lib.common import GLOBAL_SKILLS, GITIGNORE_ENTRIES, run_cmd, select_environment
from lib.output import BOLD, CYAN, RESET, header, info, step, success, warning


# Check if a global skill is already symlinked into every environment's skills dir.
def is_global_skill_installed(skill: str, envs: list[str]) -> bool:
    agents_skills = Path("~/.agents/skills").expanduser()
    for env in envs:
        env_cfg = installer.CONFIG["environments"].get(env, {})
        skills_cfg = installer.get_feature_config(env_cfg, "skills")
        if not skills_cfg: continue

        skill_path = Path(env_cfg["root"]).expanduser() / skills_cfg.get("dir", "skills") / skill
        if not skill_path.is_symlink(): return False
        try:
            if not skill_path.resolve().is_relative_to(agents_skills): return False
        except (OSError, ValueError): return False
    return True


def install_global_skills(envs: list[str]):
    success_count = 0
    for repo, skill in GLOBAL_SKILLS:
        if is_global_skill_installed(skill, envs):
            info(f"{skill} already installed, skipping")
            success_count += 1
            continue

        info(f"Installing {skill} from {repo}...")
        result = run_cmd(
            ["npx", "-y", "skills", "add", "--yes", "--global", repo, "--skill", skill]
        )
        if result.returncode == 0: success_count += 1
        else: warning(f"Failed to install {skill}")
    return success_count, len(GLOBAL_SKILLS)


def setup_workflow_dir(target_dir: Path, claptrap_path: Path):
    workflow_dir = target_dir / ".claptrap"
    conv_dest = workflow_dir / "code-conventions"
    conv_dest.mkdir(parents=True, exist_ok=True)
    for f in (claptrap_path / "src" / "code-conventions").glob("*.md"):
        shutil.copy2(f, conv_dest / f.name)
    success(f"Copied code conventions -> {conv_dest.relative_to(target_dir)}")
    return workflow_dir


def update_gitignore(target_dir: Path):
    gitignore = target_dir / ".gitignore"
    existing = set(gitignore.read_text().splitlines()) if gitignore.exists() else set()

    added = [e for e in GITIGNORE_ENTRIES if e not in existing]
    if added:
        with open(gitignore, "a") as f:
            f.write("\n".join(added) + "\n")
        success(f"Added to .gitignore: {', '.join(added)}")
    else:
        info(".gitignore already configured")


def install_to_environment(env: str, claptrap_path: Path):
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

    if env_cfg.get("agents") is not False:
        installer.generate_debate_agents(
            claptrap_path,
            root / (env_cfg.get("agents", {}).get("dir", "agents")),
            env,
        )

    return root


def resolve_envs(selected_env: str | None, verb: str) -> list[str]:
    if selected_env:
        success(f"Selected: {selected_env}")
        return [selected_env]
    success(f"{verb} all environments")
    return list(installer.CONFIG["environments"].keys())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="install", choices=["install", "verify", "mcp"])
    parser.add_argument("--env", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    claptrap_path = Path(__file__).resolve().parent.parent
    target_dir = Path.cwd()

    if args.command == "mcp": header("Claptrap MCP Installer")
    elif args.command == "verify": header("Claptrap Verification")
    else: header("Claptrap Installer")

    info(f"Claptrap path: {claptrap_path}")
    info(f"Target project: {target_dir}")

    step(1, "Environment Selection")
    if args.env:
        if args.env not in installer.CONFIG["environments"]:
            warning(f"Unknown environment: {args.env}")
            raise SystemExit(1)
        selected_env = args.env
    else:
        selected_env = select_environment()
    verb = "Verifying" if args.command == "verify" else "Installing to"
    envs_to_use = resolve_envs(selected_env, verb)

    if args.command == "mcp":
        step(2, "Installing MCP Servers")
        mcp.install_all(envs_to_use)

        step(3, "Checking MCP Servers")
        mcp.check_all(envs_to_use)

        header("MCP Installation Complete!")
        print(f"\n  Environments: {BOLD}{', '.join(envs_to_use)}{RESET}")
        print()
        return

    if args.command == "verify":
        verify.verify_all(envs_to_use, claptrap_path, target_dir)
        return

    step(2, "Installing Global Skills")
    success_count, total_count = install_global_skills(envs_to_use)
    if success_count == total_count:
        success(f"Installed {success_count}/{total_count} global skills")
    elif success_count > 0:
        warning(f"Installed {success_count}/{total_count} global skills (some failed)")
    else:
        warning("No skills were installed successfully")

    step(3, "Workflow Directory Setup")
    setup_workflow_dir(target_dir, claptrap_path)

    step(4, "Memory System Setup")
    for env in envs_to_use:
        memory.install(env, target_dir, claptrap_path)

    step(5, "Installing Features")
    for env in envs_to_use:
        install_to_environment(env, claptrap_path)

    step(6, "Configuring .gitignore")
    update_gitignore(target_dir)

    step(7, "Checking MCP Servers")
    mcp.check_all(envs_to_use)

    header("Installation Complete!")
    print(f"\n  Environments: {BOLD}{', '.join(envs_to_use)}{RESET}")
    print(f"  Workflow:     {CYAN}.claptrap/{RESET}")
    print(f"  Memory:       {CYAN}.claptrap/memory_inbox.md, memories.md{RESET}")
    print()


if __name__ == "__main__":
    main()
