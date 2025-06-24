from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.models.base_class import BaseModel, IdMixinBase


class Badge(IdMixinBase):
    __tablename__ = "badges"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_url: Mapped[str] = mapped_column(String(255), nullable=True)
    criteria: Mapped[dict] = mapped_column(JSON, nullable=True)

    user_associations = relationship(
        "app.models.badge_models.UserBadge", back_populates="badge", cascade="all, delete-orphan")


class UserBadge(BaseModel):
    __tablename__ = "userbadges"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True)
    badge_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("badges.id"), primary_key=True)
    earned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_associations")
