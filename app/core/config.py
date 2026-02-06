from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATASOURCE_HOST: str
    DATASOURCE_PORT: int = 5432
    DATASOURCE_USERNAME: str
    DATASOURCE_PASSWORD: str
    
    CATALOG_DB_NAME: str = "catalog"
    USER_DB_NAME: str = "user"
    INSIGHT_DB_NAME: str = "insight"
    
    GOOGLE_API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()