from pathlib import Path


def test_generate_debate_agents_creates_files(tmp_path):
    from bootstrap.lib.installer import generate_debate_agents

    claptrap_path = Path(__file__).parent.parent
    agents_dir = tmp_path / "agents"
    count = generate_debate_agents(claptrap_path, agents_dir, "opencode")

    assert count > 0
    assert (agents_dir / "debate-agent-1.md").exists()
