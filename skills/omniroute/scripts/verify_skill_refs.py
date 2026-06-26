#!/usr/bin/env python3
"""Verify a skill's SKILL.md index is consistent with its references/ dir.

Usage:
    python verify_skill_refs.py <skill_dir>

Checks the index<->references invariant that an "index + references" skill
must hold after a slimming refactor:

  1. Every references/<file>.md named in SKILL.md exists on disk.
  2. Every reference file on disk is named somewhere in SKILL.md
     (no orphans -- either add a pointer or delete the file).
  3. Frontmatter `description` length is within the validator limit (<=1024).
  4. Reports SKILL.md size in bytes and approx tokens.

Exit code 0 if all checks pass, 1 if any fail, 2 on usage error.
This is a deterministic probe -- run it after every slimming pass and after
adding or removing a reference file.
"""
import re
import sys
import pathlib


def main(skill_dir: str) -> int:
    d = pathlib.Path(skill_dir)
    skill_md = d / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        return 1

    text = skill_md.read_text()
    refs_dir = d / "references"
    on_disk = {p.name for p in refs_dir.glob("*.md")} if refs_dir.exists() else set()

    # Names referenced in SKILL.md: `references/<file>.md` or a bare `<file>.md`
    # inside backticks (the compact "Full references list" style).
    named = set(re.findall(r"references/([A-Za-z0-9._-]+\.md)", text))
    named |= set(re.findall(r"`([A-Za-z0-9._-]+\.md)`", text))

    ok = True

    missing = sorted(n for n in named if n not in on_disk)
    if missing:
        ok = False
        print("MISSING (named in SKILL.md but not on disk -- content may have been dropped):")
        for n in missing:
            print(f"  - {n}")

    orphans = sorted(on_disk - named)
    if orphans:
        ok = False
        print("ORPHANS (on disk but not named in SKILL.md -- add a pointer or delete):")
        for n in orphans:
            print(f"  - {n}")

    m = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.MULTILINE)
    if m:
        dlen = len(m.group(1))
        if dlen > 1024:
            ok = False
            print(f"description: {dlen} chars  <-- EXCEEDS 1024 validator limit")
        else:
            print(f"description: {dlen} chars")

    nbytes = len(text.encode())
    print(f"SKILL.md size: {nbytes:,} bytes (~{nbytes // 4:,} tokens)")
    print(f"references: {len(on_disk)} files on disk, {len(named)} named in index")
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: verify_skill_refs.py <skill_dir>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
