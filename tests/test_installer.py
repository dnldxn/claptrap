import tempfile
from pathlib import Path


def test_transform_model_replaces_alias():
    from bootstrap.lib.installer import transform_model

    content = """---
name: test-agent
model: sonnet
---
Some content here.
"""
    result = transform_model(content, "opencode")
    assert "model: anthropic/claude-sonnet-4-5" in result
    assert "model: sonnet" not in result


def test_transform_model_removes_unknown_alias():
    from bootstrap.lib.installer import transform_model

    content = """---
name: test-agent
model: kimi
---
Content here.
"""
    result = transform_model(content, "claude")
    assert "model:" not in result


def test_transform_model_preserves_non_model_lines():
    from bootstrap.lib.installer import transform_model

    content = """---
name: test-agent
description: A test agent
model: opus
---
Content here.
"""
    result = transform_model(content, "claude")
    assert "name: test-agent" in result
    assert "description: A test agent" in result
    assert "model: opus" in result


def test_cleanup_removes_claptrap_symlinks():
    from bootstrap.lib.installer import cleanup

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        staging = root / "claptrap" / "agents"
        staging.mkdir(parents=True)

        (staging / "test-agent.md").write_text("test")

        agents_dir = root / "agents"
        agents_dir.mkdir()
        symlink = agents_dir / "test-agent.md"
        symlink.symlink_to(staging / "test-agent.md")

        user_file = agents_dir / "user-agent.md"
        user_file.write_text("user content")

        cleanup(root)

        assert not symlink.exists()
        assert user_file.exists()
        assert user_file.read_text() == "user content"
        assert not (root / "claptrap").exists()


def test_cleanup_preserves_external_symlinks():
    from bootstrap.lib.installer import cleanup

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        staging = root / "claptrap"
        staging.mkdir()

        agents_dir = root / "agents"
        agents_dir.mkdir()

        external_target = root / "external" / "agent.md"
        external_target.parent.mkdir()
        external_target.write_text("external")
        external_target = external_target.resolve()
        external_link = agents_dir / "external-agent.md"
        external_link.symlink_to(external_target)

        cleanup(root)

        assert external_link.is_symlink()
        assert external_link.resolve() == external_target
