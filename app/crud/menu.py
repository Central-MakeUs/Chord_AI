from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.catalog import Menu, Recipe
from typing import List, Optional

class MenuCRUD:

    def get_menus(self, db: Session, user_id: int) -> List[Menu]:
        return db.query(Menu)\
            .options(
                selectinload(Menu.recipes)
                    .selectinload(Recipe.ingredient)
            )\
            .filter(Menu.user_id == user_id)\
            .order_by(Menu.contribution_margin.desc())\
            .all()
    def get_menu(self, db: Session, user_id: int, menu_id: int) -> Optional[Menu]:
        return db.query(Menu)\
            .options(
                selectinload(Menu.recipes)
                    .selectinload(Recipe.ingredient)
            )\
            .filter(
                Menu.menu_id == menu_id,
                Menu.user_id == user_id
            )\
            .first()

menu_crud = MenuCRUD()