from pydantic import ConfigDict, HttpUrl, StringConstraints
from typing import Annotated, List, Optional, Any, Dict
from datetime import date, datetime
from app.schemas.base_schema import BaseSchema, IDModelMixin
from app.schemas.style_schemas import ImageStyle as ImageStyleSchema
from app.schemas.user_schemas import User as UserSchema


class CharacterDossierItem(BaseSchema):
    character_name: Annotated[str, StringConstraints(min_length=1)]
    description: str
    potential_secrets_or_motives: Optional[str] = None


class DailyMysteryBase(BaseSchema):
    date: date
    theme: str
    base_story_text: str
    actual_solution_text: str
    character_dossiers: Optional[List[CharacterDossierItem]] = None
    critical_path_clues: Optional[List[str]] = None
    image_style_id: int
    base_image_urls: Optional[List[HttpUrl]] = None
    initial_choices_pool: List[str]


class DailyMysteryCreate(DailyMysteryBase):
    pass


class DailyMysteryUpdate(BaseSchema):
    theme: Optional[str] = None


class DailyMystery(DailyMysteryBase, IDModelMixin):
    image_style: ImageStyleSchema


class UserMysterySessionBase(BaseSchema):
    daily_mystery_id: int
    user_id: Optional[int] = None


class UserMysterySessionCreate(UserMysterySessionBase):
    pass


class UserMysterySessionUpdate(BaseSchema):
    current_round: Optional[int] = None
    is_solved: Optional[bool] = None
    path_taken: Optional[List[Dict[str, Any]]] = None
    detective_rank: Optional[str] = None
    final_video_url: Optional[HttpUrl] = None
    collected_clues: Optional[List[Dict[str, Any]]] = None
    notebook_text: Optional[str] = None
    end_time: Optional[datetime] = None


class UserMysterySession(UserMysterySessionBase, IDModelMixin):
    start_time: datetime
    end_time: Optional[datetime] = None
    is_solved: bool
    current_round: int
    path_taken: Optional[List[Dict[str, Any]]] = None
    detective_rank: Optional[str] = None
    final_video_url: Optional[HttpUrl] = None
    collected_clues: Optional[List[Dict[str, Any]]] = None
    notebook_text: Optional[str] = None

    daily_mystery: DailyMystery
    user: Optional[UserSchema] = None

    model_config = ConfigDict(from_attributes=True)
