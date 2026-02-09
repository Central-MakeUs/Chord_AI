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

user_crud = UserCRUD()