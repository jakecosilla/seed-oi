from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union, Optional
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    app_name: str = "Seed OI API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # API Server Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security & OIDC
    secret_key: str = "super-secret-seed-oi-key"
    oidc_issuer: str = "https://example-issuer.com"
    oidc_audience: str = "seed-oi-client-id"
    oidc_jwks_uri: Optional[str] = None # Will be discovered if not set
    
    # Provisioning & RBAC
    platform_admins: List[str] = ["jake.osilla@seed-grow.com"]
    default_tenant_id: str = "00000000-0000-0000-0000-000000000000"

    # CORS Settings
    # Supports comma-separated list in .env (e.g., CORS_ORIGINS="http://localhost:3000,https://app.seed-oi.com")
    cors_origins: List[str] = ["http://localhost:3000"]
    
    @validator("cors_origins", "platform_admins", pre=True)
    def assemble_list(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
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
