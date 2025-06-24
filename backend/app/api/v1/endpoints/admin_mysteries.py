import datetime
import random
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from app.services import ai_services
from app.services.ai_constants import MYSTERY_TYPES, ART_STYLES_WITH_DESCRIPTIONS

router = APIRouter()


@router.post(
    "/daily-mysteries/generate-mock",
    summary="MOCK: Generate mystery with AI theme & style selection",
    response_model=Dict[str, Any]
)
async def generate_mock_daily_mystery_v2():
    """
    Generates a mock daily mystery:
    1. A base mystery type (e.g., "Theft/Heist") is randomly selected.
    2. AI generates a specific one-line theme/title for that type.
    3. AI selects the most suitable art style for that theme from a predefined list.
    4. AI generates the full mystery content (story, solution, etc.) based on the AI-generated theme and selected art style.
    Simpler English is requested for the mystery content.
    No DB interaction or actual image generation occurs.
    """
    selected_mystery_type = ""
    generated_theme_info: Dict[str, str] = {}
    art_style_description_for_prompt = ""

    try:
        selected_mystery_type = random.choice(MYSTERY_TYPES)
        print(
            f"Mock Gen V2: Selected base mystery type: '{selected_mystery_type}'")

        generated_theme_info = await ai_services.generate_theme_and_art_style_for_mystery_type(
            mystery_type=selected_mystery_type
        )
        ai_theme_title = generated_theme_info["theme_title"]
        ai_selected_art_style_name = generated_theme_info["selected_art_style"]
        print(
            f"Mock Gen V2: AI generated theme: '{ai_theme_title}', AI selected style name: '{ai_selected_art_style_name}'")

        selected_style_obj = next(
            (style for style in ART_STYLES_WITH_DESCRIPTIONS if style["name"] == ai_selected_art_style_name), None)
        if selected_style_obj:
            art_style_description_for_prompt = selected_style_obj["description"]
        else:
            print(
                f"Warning: Could not find description for AI selected style '{ai_selected_art_style_name}'. Using name only.")
            art_style_description_for_prompt = ai_selected_art_style_name
        ai_story_content = await ai_services.generate_daily_mystery_content(
            theme=ai_theme_title,
            image_style_modifier=art_style_description_for_prompt
        )

        image_urls = []
        for i, img_prompt_text in enumerate(ai_story_content.get("base_image_prompts", [])):
            safe_prompt_snip = "".join(
                filter(str.isalnum, img_prompt_text[:20])) if img_prompt_text else f"img{i}"
            url = f"https://mockurl.com/base_image_{i}_{safe_prompt_snip}.png"
            image_urls.append(url)

        final_response_data = {
            "selected_base_mystery_type": selected_mystery_type,
            "ai_generated_theme_title": ai_theme_title,
            "ai_selected_art_style_name": ai_selected_art_style_name,
            "art_style_description_used_for_prompts": art_style_description_for_prompt,
            "date_generated_mock": datetime.date.today().isoformat(),
            "base_story_text": ai_story_content.get("base_story_text", "N/A"),
            "actual_solution_text": ai_story_content.get("actual_solution_text", "N/A"),
            "character_dossiers": ai_story_content.get("character_dossiers", []),
            "critical_path_clues": ai_story_content.get("critical_path_clues", []),
            "base_image_prompts_received": ai_story_content.get("base_image_prompts", []),
            "base_image_mock_urls": image_urls,
            "initial_choices_pool": ai_story_content.get("initial_choices_pool", [])
        }
        return final_response_data

    except HTTPException:
        raise
    except ValueError as ve:
        print(f"Error in generate_mock_daily_mystery_v2 (ValueError): {ve}")
        partial_data = {"error": str(ve)}
        if selected_mystery_type:
            partial_data["selected_base_mystery_type"] = selected_mystery_type
        if generated_theme_info:
            partial_data["ai_generated_theme_info"] = generated_theme_info
        raise HTTPException(
            status_code=500, detail=f"Error processing AI response: {str(ve)}")
    except ConnectionError as ce:
        print(
            f"Error in generate_mock_daily_mystery_v2 (ConnectionError): {ce}")
        raise HTTPException(
            status_code=503, detail=f"AI service connection issue: {str(ce)}")
    except Exception as e:
        print(
            f"Unexpected error in generate_mock_daily_mystery_v2: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to generate mock mystery: {type(e).__name__}")
