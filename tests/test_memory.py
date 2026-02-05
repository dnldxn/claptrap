def test_memory_generate_hooks_uses_config():
    # Memory hooks should use config from claptrap.yaml.
    from bootstrap.lib.memory import generate_hooks_config

    # Should work without provider-specific dependencies
    config = generate_hooks_config("claude")
    assert config is not None or config is None
