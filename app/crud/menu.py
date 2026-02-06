from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from models.catalog import Menu, Recipe
from typing import List, Optional

class MenuCRUD:

    def get_menus(self, db: Session, user_id: int) -> List[Menu]:
        return db.query(Menu)\
            .options(
                selectinload(Menu.recipes)
                    .selectinload(Recipe.ingredient)
            )\
            .filter(Menu.user_id == user_id)\
            .all()

menu_crud = MenuCRUD()