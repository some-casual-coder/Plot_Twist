from typing import Dict, Any, Optional
from app.schemas.mystery_schemas import CharacterDossierItem


async def generate_daily_mystery_content(theme: str, image_style_modifier: str) -> Dict[str, Any]:
    print(
        f"MOCK ai_services: Generating daily mystery for theme: {theme}, style: {image_style_modifier}")
    return {
        "base_story_text": "Mock base story...",
        "actual_solution_text": "Mock solution...",
        "initial_choices_pool": ["Choice 1", "Choice 2", "Choice 3", "Choice 4", "Choice 5", "Choice 6", "Choice 7", "Choice 8", "Choice 9", "Choice 10"],
        "character_dossiers": [CharacterDossierItem(character_name="Mock Character", description="A mock description").model_dump()],
        "critical_path_clues": ["Mock clue 1"],
        "base_image_prompts": ["Mock image prompt 1", "Mock image prompt 2"]
    }


async def generate_next_scenario_content(
    base_story_summary: str,
    actual_solution: str,
    user_choice: str,
    current_scenario_text: Optional[str],
    image_style_modifier: str,
    current_round: int
) -> Dict[str, Any]:
    print(
        f"MOCK ai_services: Generating next scenario for choice: {user_choice}, round: {current_round}")
    return {  # ... mock data ...
        "scenario_text": f"Mock scenario for choice '{user_choice}' at round {current_round}.",
        "image_prompt": "Mock image prompt for next scenario",
        "choices": ["Next Mock Choice 1", "Next Mock Choice 2", "Next Mock Choice 3"],
        "is_final_round": current_round >= 5,
        "solution_explanation": "Mock solution explanation if final round." if current_round >= 5 else None
    }
