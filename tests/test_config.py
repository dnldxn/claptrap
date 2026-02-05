import yaml
from pathlib import Path


def test_claptrap_yaml_loads():
    config_path = Path(__file__).parent.parent / "bootstrap" / "claptrap.yaml"
    assert config_path.exists(), "claptrap.yaml should exist"
    config = yaml.safe_load(config_path.read_text())
    assert "models" in config, "config should have models section"
    assert "environments" in config, "config should have environments section"
    assert "defaults" in config, "config should have defaults section"
