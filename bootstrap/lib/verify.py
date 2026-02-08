import json
from pathlib import Path

from . import installer, memory
from .common import (
    GLOBAL_SKILLS,
    GITIGNORE_ENTRIES,
    MCP_SERVERS,
    check_mcp_server,
    run_cmd,
)
from .output import info, step, success, warning


def check(name: str, passed: bool, detail: str = "") -> bool:
    # Show detail only on failure to explain what went wrong.
    msg = f"  {name}"
    if passed:
        success(msg)
    else:
        warning(msg + (f" — {detail}" if detail else ""))
    return passed


def _collect_source_files(src_dir: Path) -> list[Path]:
    return [
        src
        for src in src_dir.rglob("*")
        if src.is_file() and not installer.should_skip(src, src_dir)
    ]


def _staged_path(rel: Path, staging_dir: Path, suffix: str, is_skill: bool) -> Path:
    if is_skill or suffix == ".md":
        return staging_dir / rel
    return staging_dir / (rel.stem + suffix)


def verify_environment(env: str, claptrap_path: Path) -> tuple[int, int]:
    env_cfg = installer.CONFIG["environments"][env]
    root = Path(env_cfg["root"]).expanduser()
    src_root = claptrap_path / installer.CONFIG["source_dir"]
    staging_root = root / "claptrap"

    passed = 0
    total = 0

    for feature in ["agents", "commands", "skills"]:
        feat_cfg = installer.get_feature_config(env_cfg, feature)
        if feat_cfg is None:
            info(f"  Skipping {feature} (not supported)")
            continue

        is_skill = feature == "skills"
        suffix = ".md" if is_skill else feat_cfg.get("suffix", ".md")
        feature_dir = root / feat_cfg.get("dir", feature)
        staging_dir = staging_root / feature
        src_dir = src_root / feature

        if feature in {"commands", "skills"}:
            print()
        info(f"  {feature.capitalize()}:")
        total += 1
        passed += check(
            f"{feature} staging dir exists",
            staging_dir.exists(),
            f"expected {staging_dir}; run the installer",
        )

        source_files = _collect_source_files(src_dir)

        if is_skill:
            skill_files = {}
            for src in source_files:
                rel = src.relative_to(src_dir)
                skill_files.setdefault(rel.parts[0], []).append(src)

            for skill_name in sorted(skill_files):
                staged_exists = True
                content_valid = True
                symlink_valid = False
                detail = ""

                for src in skill_files[skill_name]:
                    rel = src.relative_to(src_dir)
                    staged = _staged_path(rel, staging_dir, suffix, is_skill)
                    if not staged.exists():
                        staged_exists = False
                        if not detail:
                            detail = f"expected at {staged}; run the installer"
                        continue

                    expected = src.read_text()
                    if staged.read_text() != expected:
                        content_valid = False
                        if not detail:
                            detail = "staged file is out of date; run the installer to update"

                link = feature_dir / skill_name
                target = staging_dir / skill_name
                is_link = link.is_symlink()
                symlink_valid = is_link and link.resolve() == target.resolve()
                if not symlink_valid and not detail:
                    if is_link:
                        detail = f"symlink target mismatch: {link.resolve()} != {target.resolve()}"
                    else:
                        detail = (
                            f"expected symlink at {link} -> {target}; run the installer"
                        )

                total += 1
                passed += check(
                    f"{skill_name} is valid",
                    staged_exists and content_valid and symlink_valid,
                    detail,
                )
            continue

        for src in source_files:
            rel = src.relative_to(src_dir)
            staged = _staged_path(rel, staging_dir, suffix, is_skill)

            staged_exists = staged.exists()
            content_valid = False
            symlink_valid = False
            detail = f"expected at {staged}; run the installer"

            if staged_exists:
                content = src.read_text()
                # Agents/commands are transformed per-environment on install.
                expected = installer.transform_model(content, env)
                content_valid = staged.read_text() == expected
                if not content_valid:
                    detail = "staged file is out of date; run the installer to update"

            link = feature_dir / staged.name
            is_link = link.is_symlink()
            symlink_valid = is_link and link.resolve() == staged.resolve()
            if not symlink_valid and staged_exists and content_valid:
                if is_link:
                    detail = f"symlink target mismatch: {link.resolve()} != {staged.resolve()}"
                else:
                    detail = (
                        f"expected symlink at {link} -> {staged}; run the installer"
                    )

            total += 1
            passed += check(
                f"{rel} is valid",
                staged_exists and content_valid and symlink_valid,
                detail,
            )

    if env_cfg.get("agents") is not False:
        agents_dir = root / (env_cfg.get("agents", {}).get("dir", "agents"))
        template = claptrap_path / "src" / "agents" / "templates" / "debate-agent.md"
        models = (
            installer.parse_debate_models(template.read_text())
            if template.exists()
            else []
        )
        if models:
            print()
            info("  Debate Agents:")
            for i in range(1, len(models) + 1):
                name = f"debate-agent-{i}.md"
                total += 1
                passed += check(
                    name,
                    (agents_dir / name).exists(),
                    f"expected at {agents_dir / name}; run the installer",
                )

    return passed, total


def verify_workflow(claptrap_path: Path, target_dir: Path) -> tuple[int, int]:
    passed = 0
    total = 0

    workflow_dir = target_dir / ".claptrap"
    conv_src = claptrap_path / "src" / "code-conventions"
    conv_dest = workflow_dir / "code-conventions"

    for src in conv_src.glob("*.md"):
        dest = conv_dest / src.name
        total += 1
        passed += check(
            f"{dest.relative_to(target_dir)} exists",
            dest.exists(),
            "run the installer to copy code conventions",
        )
        if dest.exists():
            total += 1
            passed += check(
                f"{dest.relative_to(target_dir)} content",
                dest.read_text() == src.read_text(),
                "file is out of date; run the installer to update",
            )

    enforcement_dest = workflow_dir / "enforcement.py"
    total += 1
    passed += check(
        f"{enforcement_dest.relative_to(target_dir)} exists",
        enforcement_dest.exists(),
        "run the installer to generate enforcement.py",
    )

    for name in ["memory_inbox.md", "memories.md"]:
        dest = workflow_dir / name
        total += 1
        passed += check(
            f"{dest.relative_to(target_dir)} exists",
            dest.exists(),
            "run the installer to create memory files",
        )

    return passed, total


def verify_hooks(envs: list[str], target_dir: Path) -> tuple[int, int]:
    passed = 0
    total = 0

    for env in envs:
        env_cfg = installer.CONFIG["environments"].get(env, {})
        hooks_cfg = env_cfg.get("hooks")
        if not hooks_cfg or hooks_cfg is False:
            info(f"  {env} hooks not supported")
            continue

        if env == "opencode":
            root = Path(env_cfg["root"]).expanduser()
            plugin_path = root / "plugins" / memory.ENFORCEMENT_PLUGIN
            total += 1
            passed += check(
                f"{plugin_path} exists",
                plugin_path.exists(),
                "enforcement plugin missing; run the installer",
            )
            continue

        config = memory.generate_hooks_config(env)
        if not config:
            info(f"  {env} hooks not configured")
            continue

        project_dir = hooks_cfg.get("project_dir")
        if project_dir:
            config_path = target_dir / project_dir / hooks_cfg["file"]
        else:
            root = Path(env_cfg["root"]).expanduser()
            config_path = root / hooks_cfg["file"]

        total += 1
        passed += check(
            f"{config_path} exists",
            config_path.exists(),
            "hooks config file missing; run the installer",
        )
        if not config_path.exists():
            continue

        try:
            content = config_path.read_text()
            lines = [l for l in content.split("\n") if not l.strip().startswith("//")]
            existing = json.loads("\n".join(lines))
        except json.JSONDecodeError:
            total += 1
            passed += check(
                f"{config_path} valid JSON", False, "file contains invalid JSON"
            )
            continue

        expected_hooks = config.get("hooks", {})
        existing_hooks = existing.get("hooks", {})
        for hook_name in expected_hooks.keys():
            total += 1
            passed += check(
                f"{env} hook {hook_name}",
                hook_name in existing_hooks,
                f"hook not found in {config_path}; run the installer",
            )

    return passed, total


def verify_gitignore(target_dir: Path) -> tuple[int, int]:
    gitignore = target_dir / ".gitignore"
    existing = set(gitignore.read_text().splitlines()) if gitignore.exists() else set()

    missing = [entry for entry in GITIGNORE_ENTRIES if entry not in existing]
    if not missing:
        return check(".gitignore entries present", True), 1

    passed = 0
    total = 0
    for entry in missing:
        total += 1
        passed += check(
            f"Missing {entry} in .gitignore",
            False,
            "add it manually or run the installer",
        )
    return passed, total


def verify_mcp(servers: list[str]) -> tuple[int, int]:
    passed = 0
    total = 0
    for server in servers:
        status = check_mcp_server(server)
        total += 1
        if status is None:
            detail = "neither opencode nor claude CLI found to check"
        elif status is False:
            detail = "server not found; configure it via 'opencode mcp add' or 'claude mcp add'"
        else:
            detail = "server reported as failed"
        passed += check(f"{server} MCP configured", status is True, detail)
    return passed, total


def verify_global_skills(skills: list[tuple[str, str]]) -> tuple[int, int]:
    passed = 0
    total = 0
    result = run_cmd(["npx", "-y", "skills", "list", "--global"])
    if result.returncode != 0:
        for _, skill in skills:
            total += 1
            passed += check(f"{skill} installed", False, "npx skills list failed")
        return passed, total

    output = result.stdout.lower()
    for _, skill in skills:
        total += 1
        passed += check(
            f"{skill} installed",
            skill.lower() in output,
            "run the installer or: npx skills add --global <repo> --skill " + skill,
        )
    return passed, total


def verify_all(envs: list[str], claptrap_path: Path, target_dir: Path) -> None:
    passed = 0
    total = 0
    step_num = 2

    def run(label, fn, *args):
        nonlocal passed, total, step_num
        step(step_num, label)
        step_num += 1
        p, t = fn(*args)
        passed += p
        total += t

    run("Workflow Directory Verification", verify_workflow, claptrap_path, target_dir)

    for env in envs:
        env_cfg = installer.CONFIG["environments"][env]
        root = Path(env_cfg["root"]).expanduser()
        run(
            f"Verifying {env} Features ({root})", verify_environment, env, claptrap_path
        )

    run("Hooks Configuration Verification", verify_hooks, envs, target_dir)
    run(".gitignore Verification", verify_gitignore, target_dir)
    run("MCP Server Verification", verify_mcp, MCP_SERVERS)
    run("Global Skills Verification", verify_global_skills, GLOBAL_SKILLS)

    warnings = total - passed
    print(f"\nVerification complete: {passed} passed, {warnings} warnings")
