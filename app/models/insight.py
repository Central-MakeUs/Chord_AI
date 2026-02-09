from sqlalchemy import Column, Boolean, BigInteger, Text, String, Date, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.sql import func
import enum

# Strategy State Enum
class StrategyState(str, enum.Enum):
    BEFORE = "BEFORE"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"


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
    is_saved = Column(Boolean, nullable=False, server_default="false")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True) 
    menu_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="danger_strategies")


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
    is_saved = Column(Boolean, nullable=False, server_default="false")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True)
    menu_id = Column(BigInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="caution_strategy")


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
    is_saved = Column(Boolean, nullable=False, server_default="false")
    start_date = Column(TIMESTAMP, nullable=True)
    completion_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    baseline = relationship("StrategyBaseline", back_populates="high_margin_strategy")