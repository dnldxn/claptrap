# Frontmatter parsing and manipulation
import re


def parse(content):
    """Extract frontmatter and rest of content; returns (frontmatter, rest) or (None, content)."""
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None, content
    return fm_match.group(1), content[fm_match.end() :]


def get_key(content, key):
    """Extract value of a key from frontmatter; handles scalars, lists, and dicts."""
    frontmatter, _ = parse(content)
    if frontmatter is None:
        return None

    lines = frontmatter.splitlines()
    i = 0
    key_pattern = rf"^{re.escape(key)}:"

    while i < len(lines):
        # Scalar value: key: value
        if match := re.match(rf"{key_pattern}\s*(.+)$", lines[i]):
            return match.group(1).strip()

        # List or dict value: key:\n  ...
        if re.match(rf"{key_pattern}\s*$", lines[i]):
            i += 1
            if i >= len(lines):
                return None

            # List: starts with -
            if re.match(r"^[ \t]+-\s+", lines[i]):
                values = []
                while i < len(lines) and (
                    match := re.match(r"^[ \t]+-\s+(.+)$", lines[i])
                ):
                    values.append(match.group(1).strip())
                    i += 1
                return values or None

            # Dict: starts with subkey:
            if re.match(r"^[ \t]+\S+:\s*", lines[i]):
                values = {}
                while i < len(lines) and re.match(r"^[ \t]+", lines[i]):
                    if m := re.match(r"^[ \t]+(\S+):\s*(.+?)\s*$", lines[i]):
                        values[m.group(1)] = m.group(2)
                    i += 1
                return values or None

            return None

        i += 1

    return None


def set_key(content, key, value):
    """Set or update a key in frontmatter; removes key if value is None."""
    frontmatter, rest = parse(content)
    if frontmatter is None:
        return content

    lines = frontmatter.splitlines()
    kept_lines = []
    i = 0
    key_pattern = rf"^{re.escape(key)}:\s*"

    while i < len(lines):
        if re.match(key_pattern, lines[i]):
            i += 1
            while i < len(lines) and re.match(r"^[ \t]+", lines[i]):
                i += 1
            continue
        kept_lines.append(lines[i])
        i += 1

    frontmatter = "\n".join(kept_lines)
    if value is not None:
        if frontmatter:
            frontmatter += "\n"
        frontmatter += f"{key}: {value}"

    return f"---\n{frontmatter.strip()}\n---{rest}"


def transform_models(content, provider_key):
    """Transform models dict in frontmatter to provider-specific model."""
    models = get_key(content, "models")
    if not models or not isinstance(models, dict):
        return content

    content = set_key(content, "models", None)
    if provider_key in models:
        content = set_key(content, "model", models[provider_key])
    return content
