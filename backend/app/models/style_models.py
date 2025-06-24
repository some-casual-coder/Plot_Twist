from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base_class import IdMixinBase


class ImageStyle(IdMixinBase):
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    dalle_prompt_modifier: Mapped[str] = mapped_column(Text, nullable=False)
