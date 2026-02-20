from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.user import Users
from typing import List, Optional

class UserCRUD:
    
    def get_users(self, db: Session) -> List[Users]:
        return db.query(Users)\
            .options(
                joinedload(Users.store)
            )\
            .filter(
                Users.onboarding_completed == True
            )\
            .all()
    def get_user(self, db: Session, user_id: int) -> Optional[Users]:
        return db.query(Users)\
            .options(
                joinedload(Users.store)
            )\
            .filter(
                Users.onboarding_completed == True,
                Users.user_id == user_id
            )\
            .first()

user_crud = UserCRUD()