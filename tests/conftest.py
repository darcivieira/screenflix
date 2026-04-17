import os

import pytest


# Ensure required settings are always present during test collection/import.
os.environ.setdefault("SCREENFLIX_APP_NAME", "Screenflix Test")
os.environ.setdefault("SCREENFLIX_APP_DESCRIPTION", "Screenflix test suite")
os.environ.setdefault("SCREENFLIX_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/screenflix")
os.environ.setdefault("SCREENFLIX_OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("SCREENFLIX_OMDB_API_KEY", "test-omdb-key")


@pytest.fixture(autouse=True)
def reset_settings_cache():
    import screenflix.core.settings as settings_module

    settings_module._settings = None
    yield
    settings_module._settings = None
