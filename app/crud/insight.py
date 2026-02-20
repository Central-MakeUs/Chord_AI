from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.catalog import Menu, Ingredient, Recipe
from app.models.insight import DangerMenuStrategy, CautionMenuStrategy, HighMarginMenuStrategy, StrategyBaseline, MenuSnapshot, RecipeSnapshot, HighMarginMenuList
from typing import List, Optional
from app.util.date_util import get_next_monday

class InsightCRUD:
    def save_menu_snapshots(self, db: Session, baseline_id: int, snapshot: Menu):
        s = MenuSnapshot(
            baseline_id=baseline_id,
            menu_id=snapshot.menu_id,
            menu_category_code=snapshot.menu_category_code,
            menu_name=snapshot.menu_name,
            selling_price=snapshot.selling_price,
            total_cost=snapshot.total_cost,
            cost_rate=snapshot.cost_rate,
            contribution_margin=snapshot.contribution_margin,
            margin_rate=snapshot.margin_rate,
            margin_grade_code=snapshot.margin_grade_code,
            work_time=snapshot.work_time,
            recommended_price=snapshot.recommended_price
        )
        db.add(s)
        db.flush()
        return s.snapshot_id
        
    def save_recipe_snapshots(self, db: Session, snapshot_id: int, snapshot: Recipe):
        s = RecipeSnapshot(
            snapshot_id=snapshot_id,
            recipe_id=snapshot.recipe_id,
            ingredient_id=snapshot.ingredient.ingredient_id,
            amount=snapshot.amount,
            ingredient_name=snapshot.ingredient.ingredient_name,
            unit_code=snapshot.ingredient.unit_code,
            current_unit_price=snapshot.ingredient.current_unit_price,
            supplier=snapshot.ingredient.supplier
        )
        db.add(s)
        db.flush()
        return s.recipe_snapshot_id

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

    def save_danger_menu_strategy(self, db: Session, baseline_id: int, insight: dict, menu_id: int, type: str, snapshot_id: int):
        db.add(DangerMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            menu_id=menu_id,
            snapshot_id=snapshot_id,
            guide_code=type
            ))

    def save_caution_menu_strategy(self, db: Session, baseline_id: int, insight: dict, menu_id: int, type: str, snapshot_id: int):
        db.add(CautionMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            menu_id=menu_id,
            snapshot_id=snapshot_id,
            guide_code=type
            ))

    def save_high_margin_menu_strategy(self, db: Session, baseline_id: int, insight: dict):
        data = HighMarginMenuStrategy(
            baseline_id=baseline_id,
            summary=insight['summary'], 
            detail=insight['analysis_detail'], 
            guide=insight['action_guide'], 
            expected_effect=insight['expected_effect'],
            completion_phrase=insight['completion_phrase']
        )
        db.add(data)
        db.flush()
        return data.strategy_id
        
    def save_high_margin_menu_lists(self, db: Session, menus: List[dict]):
        """strategy_id, menu_id, snapshot_id"""
        list = []

        for menu in menus:
            list.append(HighMarginMenuList(
                strategy_id=menu['strategy_id'],
                menu_id=menu['menu_id'],
                snapshot_id=menu['snapshot_id']
            ))
        db.add_all(list)

insight_crud = InsightCRUD()