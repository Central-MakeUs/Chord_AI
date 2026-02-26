from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class BaseAppSettings(BaseSettings):
    DATASOURCE_HOST: str
    DATASOURCE_PORT: int = 5432
    DATASOURCE_USERNAME: str
    DATASOURCE_PASSWORD: str

    CATALOG_DB_NAME: str = "catalog"
    USER_DB_NAME: str = "user"
    INSIGHT_DB_NAME: str = "insight"

    GOOGLE_API_KEY: str
    OPENAI_API_KEY: str

class LocalSettings(BaseAppSettings):
    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"

class ProdSettings(BaseAppSettings):
    class Config:
        env_file = None
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> BaseAppSettings:
    env = os.getenv("ENV", "local")
    if env == "prod":
        return ProdSettings()
    return LocalSettings()

settings = get_settings()