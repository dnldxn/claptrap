npx skills update -g

python3 -m pip install --user --upgrade mnemosyne-memory mnemosyne-hermes

opencode upgrade

curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
rtk init -g
rtk init --agent hermes
rtk init -g --agent cursor

npm install -g @getpaseo/cli
paseo daemon restart

hermes update --yes

npm install -g omniroute
omniroute repair
omniroute setup-claude
omniroute setup-codex
omniroute stop
omniroute serve --daemon --no-open --no-tray
