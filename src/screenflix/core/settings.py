from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix="SCREENFLIX_",
        env_file=".env",
        extra="ignore",
    )

    app_name: str
    app_description: str
    app_version: str = '0.1.0'
    log_level: str = 'INFO'

    database_url: str
    database_echo: bool = False

    openai_api_url: str = 'https://api.openai.com/v1'
    openai_api_key: str

    omdb_api_url: str = 'http://www.omdbapi.com'
    omdb_api_key: str



_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
