from typing import Annotated
from pydantic import BaseModel, StringConstraints
from app.schemas.base_schema import BaseSchema, IDModelMixin


class ImageStyleBase(BaseSchema):
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    dalle_prompt_modifier: Annotated[str, StringConstraints(min_length=1)]


class ImageStyleCreate(ImageStyleBase):
    pass


class ImageStyleUpdate(ImageStyleBase):
    pass


class ImageStyle(ImageStyleBase, IDModelMixin):
    pass
