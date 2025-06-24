from fastapi import APIRouter, HTTPException
from app.services import ai_services
import datetime

router = APIRouter()


@router.post("/daily-mysteries/generate-mock", summary="MOCK: Generate a daily mystery (no DB, no actual image gen)")
async def generate_mock_daily_mystery():
    mock_style_modifier = "in a vibrant cartoon style"
    try:
        ai_content = await ai_services.generate_daily_mystery_content(
            theme="The Case of the Mock Cookies",
            image_style_modifier=mock_style_modifier
        )

        image_urls = []
        for i, _prompt in enumerate(ai_content.get("base_image_prompts", [])):
            url = f"https://mockurl.com/base_image_{i}_{mock_style_modifier.replace(' ', '_')}.png"
            image_urls.append(url)

        generated_data = {
            "date": datetime.date.today().isoformat(),
            "theme": "The Case of the Mock Cookies",
            "base_story_text": ai_content["base_story_text"],
            "actual_solution_text": ai_content["actual_solution_text"],
            "character_dossiers": ai_content["character_dossiers"],
            "critical_path_clues": ai_content["critical_path_clues"],
            "image_style_used": mock_style_modifier,
            "base_image_urls": image_urls,
            "initial_choices_pool": ai_content["initial_choices_pool"]
        }
        return generated_data
    except Exception as e:
        # TODO log e with traceback
        print(f"Error in generate_mock_daily_mystery: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate mock mystery: {str(e)}")
