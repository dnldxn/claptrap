import pytest


def test_check_prints_and_returns_bool(capsys) -> None:
    from bootstrap.lib import verify

    assert verify.check("sample", True) is True
    out = capsys.readouterr().out
    assert "sample" in out

    assert verify.check("sample-fail", False) is False
    out = capsys.readouterr().out
    assert "sample-fail" in out


def test_verify_all_accepts_empty_envs(monkeypatch, tmp_path) -> None:
    from bootstrap.lib import verify

    monkeypatch.setattr(verify, "verify_global_skills", lambda _skills: (0, 0))
    monkeypatch.setattr(verify, "verify_mcp", lambda _servers: (0, 0))

    # Should not raise when no environments are passed.
    verify.verify_all([], tmp_path, tmp_path)
