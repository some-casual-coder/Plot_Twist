import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.db import get_async_db
from app.services import ai_services
from app.models.mystery_models import DailyMystery
from app.models.style_models import ImageStyle
from app.schemas.mystery_schemas import DailyMystery as DailyMysterySchema
import logging

from app.services.daily_mystery_service import generate_and_save_new_daily_mystery

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_image_style_by_name(db: AsyncSession, style_name: str) -> Optional[ImageStyle]:
    stmt = select(ImageStyle).where(ImageStyle.name == style_name)
    result = await db.execute(stmt)
    return result.scalars().first()


@router.post(
    "/admin/daily-mysteries/generate",
    summary="Generate and save a new daily mystery.",
    response_model=DailyMysterySchema,
    status_code=201,
    tags=["Admin - Mysteries"]
)
async def admin_trigger_generate_daily_mystery(
    force_regenerate: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    today = datetime.date.today()

    stmt_check = select(DailyMystery).options(selectinload(
        DailyMystery.image_style)).where(DailyMystery.date == today)
    result_check = await db.execute(stmt_check)
    existing_mystery = result_check.scalars().first()

    if existing_mystery and not force_regenerate:
        raise HTTPException(
            status_code=409,
            detail=f"A daily mystery for {today} already exists. Use GET /mysteries/today to fetch or set force_regenerate=true to overwrite."
        )

    if existing_mystery and force_regenerate:
        await db.delete(existing_mystery)
        await db.flush()

    try:
        new_mystery = await generate_and_save_new_daily_mystery(db, for_date=today)
        return new_mystery
    except ValueError as ve:
        logger.error(
            f"Error during mystery generation service call: {ve}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(ve))
    except (ai_services.CustomAIError, ConnectionError) as ai_ex:
        logger.error(
            f"AI service error during admin mystery generation: {ai_ex}", exc_info=True)
        raise HTTPException(
            status_code=503, detail=f"AI service error: {str(ai_ex)}")
    except Exception as e:
        logger.error(
            f"Unexpected error during admin mystery generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Unexpected error during mystery generation.")
