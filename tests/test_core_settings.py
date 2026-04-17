from screenflix.core.settings import get_settings


def test_get_settings_uses_env_and_defaults(monkeypatch):
    monkeypatch.setenv("SCREENFLIX_APP_NAME", "My App")
    monkeypatch.setenv("SCREENFLIX_APP_DESCRIPTION", "My Description")
    monkeypatch.setenv("SCREENFLIX_APP_VERSION", "0.1.0")
    monkeypatch.setenv("SCREENFLIX_DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    monkeypatch.setenv("SCREENFLIX_OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("SCREENFLIX_OMDB_API_KEY", "omdb-key")

    settings = get_settings()

    assert settings.app_name == "My App"
    assert settings.app_description == "My Description"
    assert settings.app_version == "0.1.0"
    assert settings.log_level == "INFO"
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.database_echo is False


def test_get_settings_is_cached():
    first = get_settings()
    second = get_settings()

    assert first is second
