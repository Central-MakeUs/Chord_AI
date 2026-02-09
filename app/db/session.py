from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base

# 설정
CATALOG_DATABASE_URL = (
    f"postgresql://{settings.DATASOURCE_USERNAME}:{settings.DATASOURCE_PASSWORD}"
    f"@{settings.DATASOURCE_HOST}:{settings.DATASOURCE_PORT}/{settings.CATALOG_DB_NAME}"
)

USER_DATABASE_URL = (
    f"postgresql://{settings.DATASOURCE_USERNAME}:{settings.DATASOURCE_PASSWORD}"
    f"@{settings.DATASOURCE_HOST}:{settings.DATASOURCE_PORT}/{settings.USER_DB_NAME}"
)

INSIGHT_DATABASE_URL = (
    f"postgresql://{settings.DATASOURCE_USERNAME}:{settings.DATASOURCE_PASSWORD}"
    f"@{settings.DATASOURCE_HOST}:{settings.DATASOURCE_PORT}/{settings.INSIGHT_DB_NAME}"
)

# 엔진 
catalog_engine = create_engine(CATALOG_DATABASE_URL, pool_pre_ping=True)
user_engine = create_engine(USER_DATABASE_URL, pool_pre_ping=True)
insight_engine = create_engine(INSIGHT_DATABASE_URL, pool_pre_ping=True)

# 세션
CatalogSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=catalog_engine)
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
InsightSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=insight_engine)

# Base
Base = declarative_base()