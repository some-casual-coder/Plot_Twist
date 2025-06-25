from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import logging

from app.core.db import get_async_db
from app.models.mystery_models import DailyMystery
from app.schemas.gameplay_schemas import NextScenarioRequest, NextScenarioResponse
from app.services import ai_services
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/mysteries/next-scenario",
    response_model=NextScenarioResponse,
    summary="Get the next scenario in the mystery based on user's choice and history.",
    tags=["Gameplay"]
)
async def get_next_mystery_scenario(
    request_data: NextScenarioRequest,
    db: AsyncSession = Depends(get_async_db)
):
    stmt = (
        select(DailyMystery)
        .options(selectinload(DailyMystery.image_style))
        .where(DailyMystery.id == request_data.daily_mystery_id)
    )
    result = await db.execute(stmt)
    daily_mystery = result.scalars().first()

    if not daily_mystery:
        logger.warning(
            f"DailyMystery with ID {request_data.daily_mystery_id} not found.")
        raise HTTPException(status_code=404, detail="Daily mystery not found.")

    if not daily_mystery.image_style:
        logger.error(
            f"ImageStyle not loaded for DailyMystery ID {daily_mystery.id}. This should not happen with eager loading.")
        raise HTTPException(
            status_code=500, detail="Internal server error: Mystery style configuration missing.")

    image_style_modifier = daily_mystery.image_style.dalle_prompt_modifier

    current_round_for_ai = len(request_data.path_so_far) + 1

    if current_round_for_ai > settings.MAX_ROUNDS:
        logger.warning(
            f"Attempt to generate scenario for round {current_round_for_ai}, which exceeds MAX_ROUNDS ({settings.MAX_ROUNDS}).")
        raise HTTPException(
            status_code=400, detail="Game has already concluded or maximum rounds exceeded.")

    history_parts = []
    if request_data.path_so_far:
        for i, turn in enumerate(request_data.path_so_far):
            history_parts.append(
                f"Round {i+1} Scenario: \"{turn.scenario_text}\"")
            history_parts.append(
                f"Round {i+1} Player Chose: \"{turn.chosen_action}\"")
    history_summary_for_ai = "\n".join(
        history_parts) if history_parts else "This is the first choice in the game."

    previous_scenario_text_for_ai: str
    if request_data.last_presented_scenario_text is not None:
        previous_scenario_text_for_ai = request_data.last_presented_scenario_text
    elif not request_data.path_so_far:
        previous_scenario_text_for_ai = daily_mystery.base_story_text
    else:
        logger.warning(
            "last_presented_scenario_text not provided by client and path_so_far is not empty. This might lead to inconsistent AI context.")
        raise HTTPException(
            status_code=400, detail="Missing context: last_presented_scenario_text is required when path_so_far is not empty.")

    try:
        ai_response = await ai_services.generate_next_scenario_content(
            base_story_summary=daily_mystery.base_story_text,
            actual_solution=daily_mystery.actual_solution_text,
            user_choice=request_data.current_user_choice,
            current_scenario_text=previous_scenario_text_for_ai,
            image_style_modifier=image_style_modifier,
            current_round=current_round_for_ai,
            # history_summary=history_summary_for_ai # TODO add to ai_services.generate_next_scenario_content function
        )

    except (ValueError, ConnectionError) as ai_ex:
        logger.error(
            f"AI service error during next scenario generation: {ai_ex}", exc_info=True)
        raise HTTPException(
            status_code=503, detail=f"AI service error: {str(ai_ex)}")
    except Exception as e:
        logger.error(
            f"Unexpected error during AI call for next scenario: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Unexpected error during AI processing.")

    mock_image_url_str = None
    if ai_response.get("image_prompt"):
        safe_prompt_snip = "".join(
            filter(str.isalnum, ai_response["image_prompt"][:20]))
        mock_image_url_str = f"https://mockurl.com/scenario_{current_round_for_ai}_{safe_prompt_snip}.png"

    is_final = ai_response.get("is_final_round", False)
    if current_round_for_ai == settings.MAX_ROUNDS and not is_final:
        logger.warning(
            f"AI did not mark round {settings.MAX_ROUNDS} as final. Forcing it based on round count.")
        is_final = True

    response_payload = NextScenarioResponse(
        next_scenario_text=ai_response["scenario_text"],
        next_scenario_image_url=mock_image_url_str,
        next_choices=ai_response["choices"],
        current_round_generated=current_round_for_ai,
        is_final_round=is_final,
        solution_explanation=ai_response.get(
            "solution_explanation") if is_final else None
    )

    logger.info(
        f"Generated scenario for round {current_round_for_ai}. Final round: {is_final}")
    return response_payload
