from sqlalchemy import Column, BigInteger, DECIMAL, Boolean, String, Integer, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Menu(Base):
    __tablename__ = "tb_menu"

    menu_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    menu_category_code = Column(String(20), nullable=False)
    menu_name = Column(String(100), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    cost_rate = Column(DECIMAL(10, 2), nullable=False)
    contribution_margin = Column(DECIMAL(10, 2), nullable=False)
    margin_rate = Column(DECIMAL(10, 2), nullable=False)
    margin_grade_code = Column(String(20), nullable=False)
    work_time = Column(Integer, nullable=False)
    recommended_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    recipes = relationship("Recipe", back_populates="menu", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'menu_name', name='uq_user_menu_name'),
    )


class Ingredient(Base):
    __tablename__ = "tb_ingredient"

    ingredient_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    ingredient_category_code = Column(String(20), nullable=False)
    ingredient_name = Column(String(100), nullable=False)
    unit_code = Column(String(20), ForeignKey("tb_unit.unit_code", ondelete="CASCADE"), nullable=False)
    current_unit_price = Column(DECIMAL(10, 2), nullable=False)
    supplier = Column(String(100), nullable=True)
    is_favorite = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    unit = relationship(
        "Unit",
        foreign_keys=[unit_code],
        primaryjoin="Ingredient.unit_code == Unit.unit_code",
        back_populates="ingredients"
    )
    recipes = relationship("Recipe", back_populates="ingredient", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'ingredient_name', name='uq_user_ingredient_name'),
    )


class Recipe(Base):
    __tablename__ = "tb_recipe"

    recipe_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    menu_id = Column(BigInteger, ForeignKey("tb_menu.menu_id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id = Column(BigInteger, ForeignKey("tb_ingredient.ingredient_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 3), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    menu = relationship("Menu", back_populates="recipes")
    ingredient = relationship("Ingredient", back_populates="recipes")

    __table_args__ = (
        UniqueConstraint('menu_id', 'ingredient_id', name='uq_menu_ingredient'),
    )

class Unit(Base):
    __tablename__ = "tb_unit"

    unit_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    unit_code = Column(String(20), nullable=False, unique=True)
    base_quantity = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    ingredients = relationship(
        "Ingredient",
        foreign_keys="Ingredient.unit_code",
        primaryjoin="Unit.unit_code == Ingredient.unit_code",
        back_populates="unit"
    )