import datetime
import random
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.db import get_async_db
from app.services import ai_services
from app.services.ai_constants import MYSTERY_TYPES, ART_STYLES_WITH_DESCRIPTIONS
from app.models.mystery_models import DailyMystery
from app.models.style_models import ImageStyle
from app.schemas.mystery_schemas import DailyMystery as DailyMysterySchema
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_image_style_by_name(db: AsyncSession, style_name: str) -> Optional[ImageStyle]:
    stmt = select(ImageStyle).where(ImageStyle.name == style_name)
    result = await db.execute(stmt)
    return result.scalars().first()


@router.post(
    "/daily-mysteries/generate",
    summary="Generate and save a new daily mystery.",
    response_model=DailyMysterySchema,
    status_code=201,
    tags=["Admin - Mysteries"]
)
async def generate_and_save_daily_mystery(
    force_regenerate: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    today = datetime.date.today()
    logger.info(
        f"Attempting to generate daily mystery for {today}. Force regenerate: {force_regenerate}")

    if not force_regenerate:
        stmt_check = select(DailyMystery).options(selectinload(
            DailyMystery.image_style)).where(DailyMystery.date == today)
        result_check = await db.execute(stmt_check)
        existing_mystery = result_check.scalars().first()
        if existing_mystery:
            raise HTTPException(
                status_code=409,
                detail=f"A daily mystery for {today} already exists. Use GET /mysteries/today to fetch or set force_regenerate=true to overwrite."
            )

    try:
        selected_mystery_type = random.choice(MYSTERY_TYPES)

        generated_theme_info = await ai_services.generate_theme_and_art_style_for_mystery_type(
            mystery_type=selected_mystery_type
        )
        ai_theme_title = generated_theme_info["theme_title"]
        ai_selected_art_style_name = generated_theme_info["selected_art_style"]

        image_style_obj = await get_image_style_by_name(db, ai_selected_art_style_name)
        if not image_style_obj:
            logger.error(
                f"ImageStyle named '{ai_selected_art_style_name}' not found in DB. Ensure styles are seeded.")
            raise HTTPException(
                status_code=500,  # Or 400 if considered a client setup error
                detail=f"ImageStyle '{ai_selected_art_style_name}' not found. Please seed image styles."
            )

        selected_style_details_for_prompt = next(
            (style for style in ART_STYLES_WITH_DESCRIPTIONS if style["name"] == ai_selected_art_style_name), None)
        art_style_description_for_prompt = image_style_obj.dalle_prompt_modifier  # Prefer DB data
        if selected_style_details_for_prompt and selected_style_details_for_prompt["description"] != art_style_description_for_prompt:
            logger.warning(
                f"Mismatch between constant description and DB prompt_modifier for {ai_selected_art_style_name}. Using DB version for AI prompt.")

        ai_story_content = await ai_services.generate_daily_mystery_content(
            theme=ai_theme_title,
            image_style_modifier=art_style_description_for_prompt
        )
    except (ValueError, ConnectionError) as ai_ex:
        logger.error(
            f"AI service error during mystery generation: {ai_ex}", exc_info=True)
        raise HTTPException(
            status_code=503, detail=f"AI service error: {str(ai_ex)}")
    except Exception as e:
        logger.error(
            f"Unexpected error during AI content generation phase: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Unexpected error during AI content generation.")

    base_image_urls_list = []
    for i, img_prompt_text in enumerate(ai_story_content.get("base_image_prompts", [])):
        if img_prompt_text:
            safe_prompt_snip = "".join(
                filter(str.isalnum, img_prompt_text[:20]))
            url = f"https_mockurl.com_base_image_{i}_{safe_prompt_snip}.png"
            base_image_urls_list.append(
                f"https://mockurl.com/base_image_{i}_{safe_prompt_snip}.png")

    new_mystery_data_for_model = {
        "date": today,
        "theme": ai_theme_title,
        "base_story_text": ai_story_content["base_story_text"],
        "actual_solution_text": ai_story_content["actual_solution_text"],
        "character_dossiers": ai_story_content.get("character_dossiers"),
        "critical_path_clues": ai_story_content.get("critical_path_clues"),
        "image_style_id": image_style_obj.id,
        "base_image_urls": base_image_urls_list,
        "initial_choices_pool": ai_story_content["initial_choices_pool"]
    }

    if force_regenerate:
        stmt_del_check = select(DailyMystery).where(DailyMystery.date == today)
        result_del_check = await db.execute(stmt_del_check)
        existing_to_delete = result_del_check.scalars().first()
        if existing_to_delete:
            await db.delete(existing_to_delete)

    db_mystery = DailyMystery(**new_mystery_data_for_model)
    db.add(db_mystery)

    try:
        await db.flush()
        await db.refresh(db_mystery)
        await db.refresh(db_mystery, attribute_names=['image_style'])

    except Exception as db_ex:
        logger.error(
            f"Database error during flush/refresh: {db_ex}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(db_ex)}")

    logger.info(
        f"Successfully generated and prepared to save DailyMystery ID: {db_mystery.id} for date: {today}")
    return db_mystery
