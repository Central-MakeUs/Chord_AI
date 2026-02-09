from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.insight import DangerMenuStrategy, CautionMenuStrategy, HighMarginMenuStrategy, StrategyBaseline
from typing import List, Optional
from app.util.date_util import get_next_monday

class InsightCRUD:
    def save_strategy_baseline(self, db: Session, baseline_data: dict, user_id: int):
        baseline = StrategyBaseline(
            user_id=user_id,
            avg_margin_rate=baseline_data['avg_margin_rate'],
            avg_cost_rate=baseline_data['avg_cost_rate'],
            avg_contribution_margin=baseline_data['avg_contribution_margin'],
            strategy_date=get_next_monday()
        )
        db.add(baseline)
        db.flush()  
        return baseline.baseline_id

    def save_danger_menu_strategy(self, db: Session, baseline_id: int, insight: dict, menu_id: int):
        db.add(DangerMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            menu_id=menu_id
            ))

    def save_caution_menu_strategy(self, db: Session, baseline_id: int, insight: dict, menu_id: int):
        db.add(CautionMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            menu_id=menu_id
            ))

    def save_high_margin_menu_strategy(self, db: Session, baseline_id: int, insight: dict):
        db.add(HighMarginMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            completion_phrase=insight['completion_phrase']
        ))

insight_crud = InsightCRUD()