# Claptrap


## everything-claude-code

https://github.com/affaan-m/everything-claude-code

**Add it as a subtree:**
```bash
# from inside your existing repo
git remote add ecc https://github.com/affaan-m/everything-claude-code.git
git fetch ecc

# bring upstream main into a subdir
git subtree add --prefix=external/everything-claude-code ecc main --squash
```

**Update it:**
```bash
git fetch ecc
git subtree pull --prefix=external/everything-claude-code ecc main --squash
```

`--squash` keeps my history clean by combining all ECC updates into a single commit.