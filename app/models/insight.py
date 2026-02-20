from sqlalchemy import Column, Boolean, BigInteger, INT, Text, String, Date, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.sql import func
import enum

# Strategy State Enum
class StrategyState(str, enum.Enum):
    BEFORE = "BEFORE"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"

class MenuSnapshot(Base):
    """전략 생성 시점의 메뉴 스냅샷"""
    __tablename__ = "tb_menu_snapshots"

    snapshot_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    baseline_id = Column(BigInteger, ForeignKey("tb_strategy_baselines.baseline_id", ondelete="CASCADE"), nullable=False)

    menu_id = Column(BigInteger, nullable=False)
    menu_category_code = Column(String(20), nullable=False)
    menu_name = Column(String(100), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    cost_rate = Column(DECIMAL(10, 2), nullable=False)
    contribution_margin = Column(DECIMAL(10, 2), nullable=False)
    margin_rate = Column(DECIMAL(10, 2), nullable=False)
    margin_grade_code = Column(String(20), nullable=False)
    work_time = Column(INT, nullable=False)
    recommended_price = Column(DECIMAL(10, 2), nullable=False)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="menu_snapshots")
    recipe_snapshots = relationship("RecipeSnapshot", back_populates="menu_snapshot", cascade="all, delete-orphan")

class RecipeSnapshot(Base):
    """메뉴 스냅샷 기준 레시피 스냅샷"""
    __tablename__ = "tb_recipe_snapshots"

    recipe_snapshot_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    snapshot_id = Column(BigInteger, ForeignKey("tb_menu_snapshots.snapshot_id", ondelete="CASCADE"), nullable=False)

    recipe_id = Column(BigInteger, nullable=False)
    ingredient_id = Column(BigInteger, nullable=False)
    amount = Column(DECIMAL(10, 3), nullable=False)

    ingredient_name = Column(String(100), nullable=False)
    unit_code = Column(String(20), nullable=False)
    current_unit_price = Column(DECIMAL(10, 2), nullable=False)
    supplier = Column(String(100), nullable=True)

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    # Relationships
    menu_snapshot = relationship("MenuSnapshot", back_populates="recipe_snapshots")

class StrategyBaseline(Base):
    """전략 생성 시점의 카페 메트릭 스냅샷"""
    __tablename__ = "tb_strategy_baselines"

    baseline_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    avg_margin_rate = Column(DECIMAL(10, 2), nullable=False)
    avg_cost_rate = Column(DECIMAL(10, 2), nullable=False)
    avg_contribution_margin = Column(DECIMAL(10, 2), nullable=False)
    strategy_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    # Relationships
    danger_strategies = relationship("DangerMenuStrategy", back_populates="baseline", cascade="all, delete-orphan")
    caution_strategy = relationship("CautionMenuStrategy", back_populates="baseline", cascade="all, delete-orphan")
    high_margin_strategy = relationship("HighMarginMenuStrategy", back_populates="baseline", cascade="all, delete-orphan")
    menu_snapshots = relationship("MenuSnapshot", back_populates="baseline", cascade="all, delete-orphan")
    
class DangerMenuStrategy(Base):
    """위험 메뉴 개별 전략"""
    __tablename__ = "tb_danger_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    baseline_id = Column(BigInteger, ForeignKey("tb_strategy_baselines.baseline_id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    expected_effect = Column(Text, nullable=False)
    state = Column(String(10), nullable=False, server_default="BEFORE")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True) 
    menu_id = Column(BigInteger, nullable=False)
    snapshot_id = Column(BigInteger, ForeignKey("tb_menu_snapshots.snapshot_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    guide_code = Column(String(10), nullable=False)
    
    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="danger_strategies")
    menu_snapshot = relationship("MenuSnapshot")


class CautionMenuStrategy(Base):
    """주의 메뉴 통합 전략"""
    __tablename__ = "tb_caution_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    baseline_id = Column(BigInteger, ForeignKey("tb_strategy_baselines.baseline_id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    expected_effect = Column(Text, nullable=False)
    state = Column(String(10), nullable=False, server_default="BEFORE")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True)
    menu_id = Column(BigInteger, nullable=False)
    snapshot_id = Column(BigInteger, ForeignKey("tb_menu_snapshots.snapshot_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    guide_code = Column(String(10), nullable=False)

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="caution_strategy")
    menu_snapshot = relationship("MenuSnapshot")


class HighMarginMenuStrategy(Base):
    """고마진 메뉴 통합 전략"""
    __tablename__ = "tb_high_margin_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    baseline_id = Column(BigInteger, ForeignKey("tb_strategy_baselines.baseline_id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    expected_effect = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    state = Column(String(10), nullable=False, server_default="BEFORE")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="high_margin_strategy")
    menu_list = relationship(
        "HighMarginMenuList",
        back_populates="strategy",
        cascade="all, delete-orphan"
    )

class HighMarginMenuList(Base):
    __tablename__ = "tb_high_margin_menu_list"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    strategy_id = Column(
        BigInteger,
        ForeignKey("tb_high_margin_menu_strategy.strategy_id", ondelete="CASCADE"),
        nullable=False
    )

    menu_id = Column(BigInteger, nullable=False)

    snapshot_id = Column(
        BigInteger,
        ForeignKey("tb_menu_snapshots.snapshot_id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    # Relationships
    strategy = relationship(
        "HighMarginMenuStrategy",
        back_populates="menu_list"
    )
    menu_snapshot = relationship("MenuSnapshot")