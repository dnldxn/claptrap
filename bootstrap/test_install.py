import unittest

from bootstrap.install import transform_frontmatter


class TransformFrontmatterTests(unittest.TestCase):
    def test_opencode_four_space_models_block_removes_all_models_lines(self) -> None:
        content = """---
name: Code Reviewer
description: "Review an OpenSpec change proposal for correctness, safety, and spec alignment."
model: claude-sonnet-4.5
models:
    cursor: anthropic/claude-sonnet-4.5
    github-copilot: claude-sonnet-4.5
    claude: sonnet
    opencode: openai/gpt-5.2-codex
    gemini: gemini-2.5-pro
    codex: gpt-5.1-codex
---
body
"""
        transformed = transform_frontmatter(content, "opencode")

        self.assertIn("model: openai/gpt-5.2-codex", transformed)
        self.assertNotIn("\nmodels:\n", transformed)
        self.assertNotIn("\n    codex:", transformed)
        self.assertTrue(transformed.endswith("\nbody\n"))

    def test_two_space_models_block_replaces_model(self) -> None:
        content = """---
name: X
model: a
models:
  codex: b
---
"""
        transformed = transform_frontmatter(content, "codex")
        self.assertIn("model: b", transformed)
        self.assertNotIn("\nmodels:\n", transformed)

    def test_no_models_block_no_change(self) -> None:
        content = """---
name: X
model: a
---
"""
        transformed = transform_frontmatter(content, "codex")
        self.assertEqual(content, transformed)


if __name__ == "__main__":
    unittest.main()

