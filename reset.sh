
# Remove Everything Claude Code
claude plugin uninstall everything-claude-code@everything-claude-code --scope user
claude plugin uninstall everything-claude-code@everything-claude-code --scope project
claude plugin uninstall everything-claude-code@everything-claude-code --scope local

rm -rf ~/.claude/plugins/cache/everything-claude-code

rm -rf ~/.claude/rules/common
rm -rf ~/.claude/rules/typescript ~/.claude/rules/python ~/.claude/rules/golang

claude plugin marketplace remove affaan-m/everything-claude-code


# Install Everything Claude Code
claude plugin marketplace add affaan-m/everything-claude-code

claude plugin install everything-claude-code@everything-claude-code


git clone https://github.com/affaan-m/everything-claude-code.git


# Cursor


# OpenCoide
npm install ecc-universal
