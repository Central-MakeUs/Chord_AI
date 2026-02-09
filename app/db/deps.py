from app.db.session import CatalogSessionLocal, UserSessionLocal, InsightSessionLocal
from typing import Generator

def get_catalog_db() -> Generator:
    db = CatalogSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_db() -> Generator:
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_insight_db() -> Generator:
    db = InsightSessionLocal()
    try:
        yield db
    finally:
        db.close()