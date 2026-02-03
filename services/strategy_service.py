from sqlalchemy.orm import Session
from crud.menu import menu_crud
from crud.user import user_crud
from core.guide_pipeline import run_guide_pipeline

class StrategyService:

    def __init__(self, catalog_db: Session, user_db: Session, insight_db: Session):
        self.catalog_db = catalog_db
        self.user_db = user_db
        self.insight_db = insight_db
    
    """위험 메뉴 관리 전략 생성 """
    async def create_danger_strategy(self):
        await run_guide_pipeline(self.catalog_db, self.user_db, self.insight_db)