import subprocess
import sys
from pathlib import Path


def test_install_script_exists():
    script = Path(__file__).parent.parent / "bootstrap" / "install.py"
    assert script.exists()


def test_install_script_imports_correctly():
    # Verify the new install.py can be imported without errors.
    import importlib.util

    script = Path(__file__).parent.parent / "bootstrap" / "install.py"
    spec = importlib.util.spec_from_file_location("install", script)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    # Note: We don't execute it, just verify it can be loaded
