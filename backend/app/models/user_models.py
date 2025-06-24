from sqlalchemy import (Boolean, Integer, String, DateTime, func,
                        Enum as SQLAlchemyEnum, ForeignKey)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_class import IdMixinBase
from typing import Optional
from datetime import datetime
import enum


class UserProvider(str, enum.Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"


class User(IdMixinBase):
    __tablename__="users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)

    provider: Mapped[Optional[UserProvider]] = mapped_column(
        SQLAlchemyEnum(UserProvider, name="userprovider_enum"), nullable=True)
    provider_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user_badges = relationship(
        "UserBadge", back_populates="user", cascade="all, delete-orphan")
    mystery_sessions = relationship(
        "UserMysterySession", back_populates="user", cascade="all, delete-orphan")
