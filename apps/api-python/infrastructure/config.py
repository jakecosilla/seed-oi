from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    app_name: str = "Seed OI API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # API Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Settings
    # Supports comma-separated list in .env (e.g., CORS_ORIGINS="http://localhost:3000,https://app.seed-oi.com")
    cors_origins: List[str] = ["http://localhost:3000"]
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/seed_oi"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

def get_settings() -> Settings:
    return Settings()
