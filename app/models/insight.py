from sqlalchemy import Column, Boolean, BigInteger, Text, String, Date, TIMESTAMP, Enum as SQLEnum
from db.session import Base
from sqlalchemy.sql import func
import enum

# strategy state
class StrategyState(str, enum.Enum):
    BEFORE = "BEFORE"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"

class DangerMenuStrategy(Base):
    __tablename__ = "tb_danger_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    menu_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    start_date = Column(Date)
    completion_date = Column(Date)
    state = Column(String(50), nullable=False, default=StrategyState.BEFORE.value)
    is_saved = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

class CautionMenuStrategy(Base):
    __tablename__ = "tb_caution_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    start_date = Column(Date)
    completion_date = Column(Date)
    state = Column(String(50), nullable=False, default=StrategyState.BEFORE.value)
    is_saved = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class HighMarginMenuStrategy(Base):
    __tablename__ = "tb_high_margin_menu_strategy"

    strategy_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    detail = Column(Text, nullable=False)
    guide = Column(Text, nullable=False)
    completion_phrase = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    strategy_date = Column(Date, nullable=False, server_default=func.current_date())
    start_date = Column(Date)
    completion_date = Column(Date)
    state = Column(String(50), nullable=False, default=StrategyState.BEFORE.value)
    is_saved = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())