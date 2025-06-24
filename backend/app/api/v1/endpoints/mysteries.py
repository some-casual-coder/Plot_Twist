from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import datetime
import random
import logging

from app.core.db import get_async_db
from app.models.mystery_models import DailyMystery
from app.schemas.mystery_schemas import DailyMysteryDisplayForUser
from app.services.daily_mystery_service import generate_and_save_new_daily_mystery

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/mysteries/today",
    response_model=DailyMysteryDisplayForUser,
    summary="Get today's mystery. Generates one if not found.",
    tags=["Mysteries"]
)
async def get_todays_mystery_for_user(db: AsyncSession = Depends(get_async_db)):
    today = datetime.date.today()
    stmt = select(DailyMystery).options(selectinload(
        DailyMystery.image_style)).where(DailyMystery.date == today)
    result = await db.execute(stmt)
    mystery = result.scalars().first()

    if not mystery:
        logger.info(
            f"No mystery found for {today}. Attempting to generate one on-the-fly.")
        try:
            mystery = await generate_and_save_new_daily_mystery(db, for_date=today)
            logger.info(
                f"Successfully generated new mystery (ID: {mystery.id}) on-the-fly for {today}.")
        except Exception as e:
            logger.error(
                f"Failed to generate mystery on-the-fly for {today}: {e}", exc_info=True)
            raise HTTPException(
                status_code=503,
                detail="Today's mystery is currently unavailable, and we failed to generate a new one. Please try again later."
            )

    if not mystery:
        logger.error(
            f"Mystery is still None after attempting generation for {today}.")
        raise HTTPException(
            status_code=500, detail="Internal server error retrieving today's mystery.")

    if not mystery.initial_choices_pool or len(mystery.initial_choices_pool) < 3:
        logger.error(
            f"Mystery ID {mystery.id} has insufficient choices in initial_choices_pool.")
        raise HTTPException(
            status_code=500, detail="Today's mystery has an invalid configuration (choices).")

    selected_choices = random.sample(
        mystery.initial_choices_pool, min(3, len(mystery.initial_choices_pool)))

    return DailyMysteryDisplayForUser(
        daily_mystery_id=mystery.id,
        theme=mystery.theme,
        base_story_text=mystery.base_story_text,
        base_image_urls=[str(url) for url in mystery.base_image_urls] if mystery.base_image_urls else [
        ],
        character_dossiers=mystery.character_dossiers,
        initial_choices=selected_choices
    )
