import subprocess
from pathlib import Path

import yaml

###################################################################################################
# Config
###################################################################################################
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((PROJECT_ROOT / "bootstrap" / "config.yml").read_text())


###################################################################################################
# Output Formatting
###################################################################################################
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def success(msg): print(f"{GREEN}✓{RESET} {msg}")
def warning(msg): print(f"{YELLOW}⚠{RESET} {msg}")
def info(msg): print(f"{CYAN}→{RESET} {msg}")
def header(msg): print(f"\n{BOLD}📦 {msg}{RESET}")
def step(num, msg): print(f"\n{BOLD}[{num}]{RESET} {msg}")


###################################################################################################
# Helper functions
###################################################################################################
def run_command(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def uninstall_features(dest_dir: Path):
    removed = 0
    for link in dest_dir.iterdir():
        if link.is_symlink():
            target = link.resolve()
            if target == PROJECT_ROOT or PROJECT_ROOT in target.parents:
                link.unlink()
                removed += 1
    info(f"Cleaned {dest_dir} ({removed} removed)")


def install_feature(rel_paths: list[str], dest_dir: Path):
    added = 0
    for rel_path in rel_paths:
        src = (PROJECT_ROOT / rel_path).resolve()
        dest = dest_dir / src.name
        if dest.exists() or dest.is_symlink():
            dest.unlink()
        dest.symlink_to(src)
        added += 1
    success(f"Installed {added} -> {dest_dir}")


###################################################################################################
# Main
###################################################################################################
header("Installing symlinks")
for provider_name, provider in CONFIG["providers"].items():
    cli = provider["cli"]
    provider_root = Path(provider["root"]).expanduser()
    header(f"{provider_name}: {provider_root}")
    result = run_command([cli, "--version"])
    if result.returncode != 0:
        warning(f"Skipping {provider_name}: {result.stderr.strip()}")
        continue
    info(f"{cli} version: {result.stdout.strip() or result.stderr.strip()}")
    for feature_name, rel_paths in CONFIG["features"].items():
        dest_dir = provider_root / feature_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        uninstall_features(dest_dir)
        install_feature(rel_paths, dest_dir)
success("Done.")
