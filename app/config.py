from typing import Any, Dict, List, Optional, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = True,
    )
    
    PROJECT_NAME: str = "BookStore API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # === API Settings ===
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str] | None:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # === Security ===
    SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7
    
    # === Database ===
    DATABASE_URL: PostgresDsn
    
    # === First Superuser ===
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    
    # === File Upload ===
    UPLOAD_DIR: str = "uploads/books/"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024 # 5MB
    
    @property
    def sqlalchemy_database_url(self ) -> str:
        return str(self.DATABASE_URL)
    
    
settings = Settings()

    
        