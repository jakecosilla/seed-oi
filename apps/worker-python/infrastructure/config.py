from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Seed OI Worker"
    environment: str = "development"
    debug: bool = True

    # Database Settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/seed_oi"

    # Queue / Event Stream Settings (e.g., Redis or similar)
    broker_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

def get_settings() -> Settings:
    return Settings()

