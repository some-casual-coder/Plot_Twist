from pydantic import HttpUrl
from typing import Optional, Any, Dict
from datetime import datetime
from app.schemas.base_schema import BaseSchema, IDModelMixin


class BadgeBase(BaseSchema):
    name: str
    description: str
    icon_url: Optional[HttpUrl] = None
    criteria: Optional[Dict[str, Any]] = None


class BadgeCreate(BadgeBase):
    pass


class BadgeUpdate(BadgeBase):
    pass


class Badge(BadgeBase, IDModelMixin):
    pass


class UserBadgeBase(BaseSchema):
    user_id: int
    badge_id: int


class UserBadgeCreate(UserBadgeBase):
    pass


class UserBadge(UserBadgeBase):
    earned_at: datetime
    badge: Badge
