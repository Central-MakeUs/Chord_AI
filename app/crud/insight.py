from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.insight import DangerMenuStrategy, CautionMenuStrategy, HighMarginMenuStrategy
from typing import List, Optional
from app.util.date_util import get_next_monday

class InsightCRUD:

    def save_danger_menu_strategy(self, db: Session, insight: dict, menu_id: int, user_id: int):
        db.add(DangerMenuStrategy(
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            completion_phrase=insight['completion_phrase'], 
            menu_id=menu_id,
            user_id=user_id, 
            strategy_date=get_next_monday()
            ))

    def save_caution_menu_strategy(self, db: Session, insight: dict, user_id: int):
        db.add(CautionMenuStrategy(
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            completion_phrase=insight['completion_phrase'], 
            user_id=user_id, 
            strategy_date=get_next_monday()
            ))

    def save_high_margin_menu_strategy(self, db: Session, insight: dict, user_id: int):
        db.add(HighMarginMenuStrategy(
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            completion_phrase=insight['completion_phrase'], 
            user_id=user_id, 
            strategy_date=get_next_monday()))

insight_crud = InsightCRUD()