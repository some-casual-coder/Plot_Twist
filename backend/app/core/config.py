from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "PlotTwist API"
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_ECHO: bool = True

    # Database
    DATABASE_URL: str

    # API Keys
    DALLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET_NAME: Optional[str] = None
    AWS_S3_REGION_NAME: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
