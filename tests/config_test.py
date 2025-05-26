from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, EmailStr


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test", env_file_encoding="utf-8", case_sensitive=True, )

    # Provide default values for testing
    PROJECT_NAME: str = "BookStore API Test"
    PROJECT_DESCRIPTION: str = "Test Environment"
    APP_VERSION: str = "1.0.0"
    APP_NAME: str = "BookStore API Test"
    DEBUG: bool = True
    ENVIRONMENT: str = "test"

    # API Settings
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Security
    SECRET_KEY: str = "testsecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database - use SQLite for testing
    DATABASE_URL: str = "sqlite:///./test.db"

    # Database configurations
    POSTGRES_DB: str = "test_db"
    POSTGRES_USER: str = "test_user"
    POSTGRES_PASSWORD: str = "test_password"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"

    # First superuser
    FIRST_SUPERUSER_EMAIL: EmailStr = "test@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "testpassword"

    # File Upload
    UPLOAD_DIR: str = "uploads/books/"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    @property
    def sqlalchemy_database_url( self ) -> str:
        return str(self.DATABASE_URL)


test_settings = TestSettings()