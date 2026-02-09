from sqlalchemy import Column, BigInteger, DECIMAL, Boolean, String, Integer, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Users(Base):
    __tablename__ = "tb_user"

    user_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    login_id = Column(String(20), nullable=False, unique=True)  # unique 추가
    password = Column(String(100), nullable=False)
    last_login_at = Column(TIMESTAMP, nullable=True)
    onboarding_completed = Column(Boolean, nullable=False, server_default="false")  # nullable=False
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    store = relationship("Store", back_populates="user", uselist=False, cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class Store(Base):
    __tablename__ = "tb_store"

    user_id = Column(BigInteger, ForeignKey("tb_user.user_id", ondelete="CASCADE"), primary_key=True)  # autoincrement 제거, FK 추가
    name = Column(String(20), nullable=True)
    employees = Column(Integer, nullable=True)
    labor_cost = Column(DECIMAL(10, 1), nullable=True)
    rent_cost = Column(DECIMAL(15, 2), nullable=True)
    include_weekly_holiday_pay = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("Users", back_populates="store", uselist=False)


class RefreshToken(Base):
    __tablename__ = "tb_refresh_token"

    refresh_token_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("tb_user.user_id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(Text, nullable=False)
    expired_at = Column(TIMESTAMP, nullable=False)
    last_used_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("Users", back_populates="refresh_tokens")