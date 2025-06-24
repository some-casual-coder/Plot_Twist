from sqlalchemy import (Integer, String, Text, Date,
                        Boolean, DateTime, ForeignKey, func, JSON)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base_class import IdMixinBase
from typing import Optional, List, Dict, Any
from datetime import date as DateType, datetime as DateTimeType


class DailyMystery(IdMixinBase):
    date: Mapped[DateType] = mapped_column(
        Date, unique=True, nullable=False, index=True)
    theme: Mapped[str] = mapped_column(String(100), nullable=False)
    base_story_text: Mapped[str] = mapped_column(Text, nullable=False)
    actual_solution_text: Mapped[str] = mapped_column(Text, nullable=False)
    character_dossiers: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON, nullable=True)
    critical_path_clues: Mapped[Optional[List[str]]
                                ] = mapped_column(JSON, nullable=True)

    image_style_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("imagestyles.id"), nullable=False)
    image_style = relationship("ImageStyle")

    base_image_urls: Mapped[Optional[List[str]]
                            ] = mapped_column(JSON, nullable=True)
    initial_choices_pool: Mapped[List[str]
                                 ] = mapped_column(JSON, nullable=False)

    user_sessions = relationship(
        "UserMysterySession", back_populates="daily_mystery", cascade="all, delete-orphan")


class UserMysterySession(IdMixinBase):
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True, index=True)
    daily_mystery_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dailymysteries.id"), nullable=False, index=True)

    start_time: Mapped[DateTimeType] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    end_time: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True)
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    current_round: Mapped[int] = mapped_column(Integer, default=0)

    path_taken: Mapped[Optional[List[Dict[str, Any]]]
                       ] = mapped_column(JSON, nullable=True)
    detective_rank: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True)
    final_video_url: Mapped[Optional[str]
                            ] = mapped_column(String, nullable=True)

    collected_clues: Mapped[Optional[List[Dict[str, Any]]]
                            ] = mapped_column(JSON, nullable=True)
    notebook_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="mystery_sessions")
    daily_mystery = relationship(
        "DailyMystery", back_populates="user_sessions")
