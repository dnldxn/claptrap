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
