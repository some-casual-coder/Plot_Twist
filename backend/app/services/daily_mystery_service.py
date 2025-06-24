import datetime
import random
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import logging

from app.models.mystery_models import DailyMystery
from app.models.style_models import ImageStyle
from app.services import ai_services
from app.services.ai_constants import MYSTERY_TYPES

logger = logging.getLogger(__name__)


async def get_image_style_by_name(db: AsyncSession, style_name: str) -> Optional[ImageStyle]:
    stmt = select(ImageStyle).where(ImageStyle.name == style_name)
    result = await db.execute(stmt)
    return result.scalars().first()


async def generate_and_save_new_daily_mystery(db: AsyncSession, for_date: datetime.date) -> DailyMystery:
    """
    Core logic to generate AI content for a new daily mystery and save it to the database.
    This function assumes a mystery for 'for_date' does NOT already exist or is intended to be overwritten.
    (The calling function should handle checks for existing mysteries or force_overwrite logic).
    """
    logger.info(
        f"Initiating AI generation for daily mystery for date: {for_date}")

    selected_mystery_type = random.choice(MYSTERY_TYPES)
    logger.debug(
        f"Selected base mystery type: '{selected_mystery_type}' for {for_date}")

    generated_theme_info = await ai_services.generate_theme_and_art_style_for_mystery_type(
        mystery_type=selected_mystery_type
    )
    ai_theme_title = generated_theme_info["theme_title"]
    ai_selected_art_style_name = generated_theme_info["selected_art_style"]
    logger.debug(
        f"AI generated theme: '{ai_theme_title}', style: '{ai_selected_art_style_name}' for {for_date}")

    image_style_obj = await get_image_style_by_name(db, ai_selected_art_style_name)
    if not image_style_obj:
        logger.error(
            f"ImageStyle '{ai_selected_art_style_name}' not found. Cannot generate mystery for {for_date}.")
        raise ValueError(
            f"ImageStyle '{ai_selected_art_style_name}' not found. Ensure styles are seeded.")

    art_style_description_for_prompt = image_style_obj.dalle_prompt_modifier

    ai_story_content = await ai_services.generate_daily_mystery_content(
        theme=ai_theme_title,
        image_style_modifier=art_style_description_for_prompt
    )
    logger.debug(f"AI story content generated for {for_date}")

    base_image_urls_list = []
    for i, img_prompt_text in enumerate(ai_story_content.get("base_image_prompts", [])):
        if img_prompt_text:
            safe_prompt_snip = "".join(
                filter(str.isalnum, img_prompt_text[:20]))
            url = f"https://mockurl.com/base_image_{i}_{safe_prompt_snip}.png"
            base_image_urls_list.append(url)

    new_mystery_data_for_model = {
        "date": for_date,
        "theme": ai_theme_title,
        "base_story_text": ai_story_content["base_story_text"],
        "actual_solution_text": ai_story_content["actual_solution_text"],
        "character_dossiers": ai_story_content.get("character_dossiers"),
        "critical_path_clues": ai_story_content.get("critical_path_clues"),
        "image_style_id": image_style_obj.id,
        "base_image_urls": base_image_urls_list,
        "initial_choices_pool": ai_story_content["initial_choices_pool"]
    }

    db_mystery = DailyMystery(**new_mystery_data_for_model)
    db.add(db_mystery)
    await db.flush()  # Get ID
    await db.refresh(db_mystery)
    await db.refresh(db_mystery, attribute_names=['image_style'])

    logger.info(
        f"Successfully generated and saved DailyMystery ID: {db_mystery.id} for date: {for_date}")
    return db_mystery
