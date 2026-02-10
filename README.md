# Claptrap


## External Tools

- https://github.com/affaan-m/everything-claude-code
- https://github.com/obra/superpowers (for brainstorming skill)

Run the following commands from inside your existing repo:

**Add as a subtree:**

```bash
# everything-claude-code
git remote add ecc https://github.com/affaan-m/everything-claude-code.git
git fetch ecc
git subtree add --prefix=external/everything-claude-code ecc main --squash

# superpowers
git remote add sp https://github.com/obra/superpowers.git
git fetch sp
git subtree add --prefix=external/superpowers sp main --squash
```

**Update:**

```bash
git fetch ecc
git fetch sp
git subtree pull --prefix=external/everything-claude-code ecc main --squash
git subtree pull --prefix=external/superpowers sp main --squash
```

`--squash` keeps the project history clean by combining all external updates into a single commit.
