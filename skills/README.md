```bash
install_skill() {
  local name=$1
  ln -sf ~/projects/claptrap/skills/${name}/SKILL.md ~/.config/opencode/commands/${name}.md
  ln -sf ~/projects/claptrap/skills/${name} ~/.claude/skills/
  ln -sf ~/projects/claptrap/skills/${name} ~/.hermes/skills/claptrap/
}

remove_skill() {
  local name=$1
  rm -f ~/.config/opencode/commands/${name}.md
  rm -f ~/.claude/skills/${name}
  rm -f ~/.hermes/skills/claptrap/${name}
}

remove_skill ct-grill-me
remove_skill ct-writing-plans
remove_skill ct-implement
remove_skill ct-close-branch

# Shared skill
ln -sf ~/projects/claptrap/skills/ct-manage-state-file ~/.claude/skills/
ln -sf ~/projects/claptrap/skills/ct-manage-state-file ~/.agents/skills/
ln -sf ~/projects/claptrap/skills/ct-manage-state-file ~/.hermes/skills/claptrap/

rm -f ~/.claude/skills/ct-manage-state-file
rm -f ~/.agents/skills/ct-manage-state-file
rm -f ~/.hermes/skills/claptrap/ct-manage-state-file


mkdir -p ~/.config/opencode/commands/
mkdir -p ~/.claude/skills/github-projects
mkdir -p ~/.agents/skills/github-projects
mkdir -p ~/.hermes/skills/claptrap/github-projects

ln -sf ~/projects/claptrap/skills/github-projects/gh-implement ~/.claude/skills/github-projects/
ln -sf ~/projects/claptrap/skills/github-projects/gh-implement ~/.agents
```
