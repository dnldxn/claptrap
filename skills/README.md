```bash
install_skill() {
  local name=$1
  ln -sf ~/projects/claptrap/skills/${name}/SKILL.md ~/.config/opencode/commands/${name}.md
  ln -sf ~/projects/claptrap/skills/${name} ~/.claude/skills/
}

install_skill ct-grill-me
install_skill ct-writing-plans
install_skill ct-implement
install_skill ct-close-branch
install_skill jupyter-notebooks
```
