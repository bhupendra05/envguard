import os, pytest
from envguard import env, Required, Opt, EnvError

def test_valid_env(monkeypatch):
    monkeypatch.setenv("MY_HOST", "localhost")
    monkeypatch.setenv("MY_PORT", "5432")

    @env
    class Cfg:
        MY_HOST: str = Required()
        MY_PORT: int = Opt(8000)

    assert Cfg.MY_HOST == "localhost"
    assert Cfg.MY_PORT == 5432

def test_missing_required_raises(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    with pytest.raises(EnvError):
        @env
        class Bad:
            MISSING_VAR: str = Required()

def test_bool_conversion(monkeypatch):
    monkeypatch.setenv("FLAG", "true")
    @env
    class C:
        FLAG: bool = Opt(False)
    assert C.FLAG is True
