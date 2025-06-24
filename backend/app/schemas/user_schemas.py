from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Optional
from app.models.user_models import UserProvider
from app.schemas.base_schema import BaseSchema, IDModelMixin, DateTimeModelMixin


class UserBase(BaseSchema):
    email: EmailStr
    display_name: Optional[Annotated[str, StringConstraints(
        min_length=1, max_length=50)]] = None


class UserCreate(UserBase):
    provider: Optional[UserProvider] = None
    provider_id: Optional[str] = None


class UserUpdate(BaseSchema):
    display_name: Optional[Annotated[str, StringConstraints(
        min_length=1, max_length=50)]] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class User(UserBase, IDModelMixin, DateTimeModelMixin):
    is_active: bool
    is_superuser: bool
    provider: Optional[UserProvider] = None


class UserInDBBase(UserBase, IDModelMixin, DateTimeModelMixin):
    is_active: bool = True
    is_superuser: bool = False
    provider: Optional[UserProvider] = None
    provider_id: Optional[str] = None
