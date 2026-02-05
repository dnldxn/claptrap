import tempfile
from pathlib import Path


def test_full_install_creates_expected_structure():
    # Integration test: verify install creates correct structure.
    from bootstrap.lib import installer

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        claptrap_path = Path(__file__).parent.parent
        src_root = claptrap_path / installer.CONFIG["source_dir"]

        env = "opencode"
        staging = root / "claptrap"

        agents_cfg = installer.get_feature_config(
            installer.CONFIG["environments"][env], "agents"
        )
        agents_dir = root / agents_cfg["dir"]

        count = installer.install_feature(
            src_dir=src_root / "agents",
            staging_dir=staging / "agents",
            feature_dir=agents_dir,
            suffix=agents_cfg.get("suffix", ".md"),
            env=env,
            is_skill=False,
        )

        assert (staging / "agents").exists()
        assert agents_dir.exists()
        assert count > 0

        for item in agents_dir.iterdir():
            if item.is_symlink():
                target = item.resolve()
                assert str(staging) in str(target.parent)


def test_model_transform_produces_valid_yaml():
    # Verify transformed content is valid YAML.
    import yaml
    from bootstrap.lib.installer import transform_model

    content = """---
name: test-agent
description: A test agent
model: sonnet
---
Content here.
"""
    result = transform_model(content, "opencode")

    if result.startswith("---"):
        end = result.find("---", 3)
        frontmatter = result[3:end].strip()
        parsed = yaml.safe_load(frontmatter)
        assert parsed["name"] == "test-agent"
        assert parsed["model"] == "anthropic/claude-sonnet-4-5"
