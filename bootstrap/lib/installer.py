import re
import shutil
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).parent.parent / "claptrap.yaml"
CONFIG = yaml.safe_load(_CONFIG_PATH.read_text()) if _CONFIG_PATH.exists() else {}
MODELS = CONFIG.get("models", {})
DEFAULTS = CONFIG.get("defaults", {})
SKIP_NAMES = {"AGENTS.md", "README.md"}


def transform_model(content: str, env: str) -> str:
    def replace(m):
        alias = m.group(1)
        if alias in MODELS and env in MODELS[alias]:
            return f"model: {MODELS[alias][env]}"
        return ""

    return re.sub(r"^model:\s*(\S+)\s*$", replace, content, flags=re.MULTILINE)


def cleanup(root: Path) -> None:
    staging = root / "claptrap"

    for feature in ["agents", "commands", "skills"]:
        feature_dir = root / feature
        if not feature_dir.exists():
            continue

        for item in feature_dir.iterdir():
            if item.is_symlink():
                try:
                    item.resolve().relative_to(staging)
                    item.unlink()
                except (ValueError, OSError):
                    pass

    shutil.rmtree(staging, ignore_errors=True)


def should_skip(src_file: Path, src_dir: Path) -> bool:
    if src_file.name in SKIP_NAMES:
        return True

    rel_path = src_file.relative_to(src_dir)
    parts = rel_path.parts

    return "templates" in parts or "_archive" in parts


def get_feature_config(env_cfg: dict, feature: str) -> dict | None:
    feat_cfg = env_cfg.get(feature, DEFAULTS.get(feature))

    if feat_cfg is False:
        return None

    if isinstance(feat_cfg, dict):
        return {**DEFAULTS.get(feature, {}), **feat_cfg}

    return DEFAULTS.get(feature, {})


def install_feature(
    src_dir: Path,
    staging_dir: Path,
    feature_dir: Path,
    suffix: str,
    env: str,
    is_skill: bool,
) -> int:
    staging_dir.mkdir(parents=True, exist_ok=True)
    feature_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    created_skill_links = set()

    for src in src_dir.rglob("*"):
        if not src.is_file() or should_skip(src, src_dir):
            continue

        rel = src.relative_to(src_dir)

        if is_skill:
            staged = staging_dir / rel
        else:
            staged = (
                staging_dir / (rel.stem + suffix)
                if suffix != ".md"
                else staging_dir / rel
            )

        staged.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text()
        staged.write_text(content if is_skill else transform_model(content, env))
        count += 1

        if is_skill:
            skill_name = rel.parts[0]
            if skill_name not in created_skill_links:
                link = feature_dir / skill_name
                target = staging_dir / skill_name
                if link.is_symlink():
                    link.unlink()
                if not link.exists() and target.is_dir():
                    link.symlink_to(Path("..") / "claptrap" / "skills" / skill_name)
                    created_skill_links.add(skill_name)
        else:
            link = feature_dir / staged.name
            if link.is_symlink():
                link.unlink()
            if not link.exists():
                link.symlink_to(
                    Path("..") / "claptrap" / feature_dir.name / staged.name
                )

    return count


def generate_debate_agents(claptrap_path: Path, agents_dir: Path, env: str) -> int:
    template_path = claptrap_path / "src" / "agents" / "templates" / "debate-agent.md"
    if not template_path.exists():
        return 0

    content = template_path.read_text()

    models = []
    if match := re.search(r"^debate-models:\s*$", content, re.MULTILINE):
        for line in content[match.end() :].splitlines():
            if line.strip().startswith("- "):
                models.append(line.strip()[2:].strip())
            elif line.strip() and not line.startswith(" "):
                break

    if not models:
        return 0

    content = re.sub(
        r"^debate-models:.*?(?=^[a-z]|\Z)",
        "",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    agents_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for i, model in enumerate(models, 1):
        agent_content = content.replace("{NAME}", str(i)).replace("{MODEL}", model)
        dest = agents_dir / f"debate-agent-{i}.md"
        dest.write_text(agent_content)
        count += 1

    return count
