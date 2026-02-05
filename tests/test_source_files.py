import re
from pathlib import Path


def test_source_files_use_aliases():
    # Source files should use model aliases, not provider-specific models.
    src_dir = Path(__file__).parent.parent / "src"

    # Valid aliases from claptrap.yaml
    valid_aliases = {
        "sonnet",
        "opus",
        "gpt5-codex",
        "haiku",
        "flash",
        "flash-preview",
        "kimi",
    }

    for md_file in src_dir.rglob("*.md"):
        if "_archive" in str(md_file) or "templates" in str(md_file):
            continue
        if md_file.name in ("AGENTS.md", "README.md", "TEMPLATE.md"):
            continue

        content = md_file.read_text()

        # Check no multi-line models: dict
        assert "models:" not in content or not re.search(
            r"^models:\s*$", content, re.MULTILINE
        ), f"{md_file} should not have models: dict (use model alias instead)"

        # Check model: uses valid alias (if model: exists)
        if match := re.search(r"^model:\s*(\S+)", content, re.MULTILINE):
            model_value = match.group(1)
            assert model_value in valid_aliases, (
                f"{md_file}: model '{model_value}' should be a valid alias: {valid_aliases}"
            )
