from sqlalchemy import Column, Boolean, BigInteger, Text, Date, Enum as SQLEnum
from db.base import Base
from sqlalchemy.sql import func
import enum

# strategy state
class StrategyState(str, enum.Enum):
    BEFORE = "before"
    ONGOING = "ongoing"
    COMPLETED = "completed"

class DangerMenuStrategy(Base):
    __tablename__ = "tb_danger_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    menu_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    state = Column(
    SQLEnum(StrategyState, name="strategy_state", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StrategyState.BEFORE
    )
    is_saved = Column(Boolean, nullable=False, server_default="false")

class CautionMenuStrategy(Base):
    __tablename__ = "tb_caution_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    state = Column(
        SQLEnum(StrategyState, name="strategy_state", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StrategyState.BEFORE
    )
    is_saved = Column(Boolean, nullable=False, server_default="false")


class HighMarginMenuStrategy(Base):
    __tablename__ = "tb_high_margin_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    state = Column(
        SQLEnum(StrategyState, name="strategy_state", create_type=False, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=StrategyState.BEFORE
    )
    is_saved = Column(Boolean, nullable=False, server_default="false")