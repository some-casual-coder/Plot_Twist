import json
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from google import genai
from google.genai import types as genai_types

from app.core.config import settings
from app.schemas.mystery_schemas import CharacterDossierItem
from app.services.ai_constants import *


master_gemini_client: Optional[genai.Client] = None
logger = logging.getLogger(__name__)


if settings.GEMINI_API_KEY:
    try:
        master_gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        print("INFO: Master Gemini Client initialized successfully with API key.")
    except Exception as e:
        print(
            f"ERROR: Failed to initialize Master Gemini Client: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        master_gemini_client = None
else:
    print("WARNING: GEMINI_API_KEY not found. Gemini services will fail.")


async def _call_gemini_model_with_config(
    prompt_text: str,
    system_instruction_text: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: int = 2048,
    is_json_output_expected: bool = False
) -> Dict[str, Any]:

    if not master_gemini_client:
        print("ERROR: Master Gemini Client not initialized.")
        raise ConnectionError("Master Gemini Client not initialized.")

    print(
        f"DEBUG: Calling client.models.generate_content for model '{DEFAULT_GEMINI_MODEL_NAME_STRING}'. Temp: {temperature}")

    try:
        current_contents = [genai_types.Content(
            parts=[genai_types.Part(text=prompt_text)], role="user"
        )]

        safety_settings_list = [
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
            genai_types.SafetySetting(
                category=genai_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=genai_types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            ),
        ]

        config_constructor_args = {
            "temperature": 0.8,
            "max_output_tokens": max_output_tokens,
            "safety_settings": safety_settings_list,
            "top_p": 0.85,
            "top_k": 40
        }

        if system_instruction_text:
            config_constructor_args["system_instruction"] = system_instruction_text

        generation_config_obj = genai_types.GenerateContentConfig(
            **config_constructor_args)

        call_kwargs = {
            "model": DEFAULT_GEMINI_MODEL_NAME_STRING,
            "contents": current_contents,
            "config": generation_config_obj,
        }

        response = await run_in_threadpool(
            master_gemini_client.models.generate_content,
            **call_kwargs
        )

        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
            block_reason_val = response.prompt_feedback.block_reason
            block_reason_str = block_reason_val.name if hasattr(
                block_reason_val, 'name') else str(block_reason_val)
            print(
                f"ERROR: Gemini API call blocked. Reason: {block_reason_str}.")
            raise ValueError(
                f"Gemini content generation blocked: {block_reason_str}")

        generated_text = ""
        if hasattr(response, 'text') and response.text:
            generated_text = response.text
        elif response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    generated_text += part.text

        if not generated_text:
            print(
                f"ERROR: Gemini response did not contain usable text. Response: {response}")
            raise ValueError("Gemini response was empty or malformed.")

        if is_json_output_expected:
            clean_text = generated_text.strip()
            if clean_text.lower().startswith("```json"):
                json_str = clean_text[7:-3].strip()
            elif clean_text.startswith("{") and clean_text.endswith("}"):
                json_str = clean_text
            else:
                print(
                    f"ERROR: Expected JSON from Gemini, but got: {generated_text[:300]}...")
                raise ValueError(
                    "Gemini did not return a response starting with ```json or {")
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(
                    f"ERROR: Failed to parse JSON from Gemini response: {e}. Raw text was: {generated_text}")
                raise ValueError(
                    f"Failed to parse JSON from Gemini: {e}. Raw text: {generated_text}")
        else:
            return {"raw_text": generated_text}

    except ValueError as ve:
        print(f"ValueError during Gemini call: {ve}")
        raise
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred calling Gemini SDK: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        raise ConnectionError(f"Failed to communicate with Gemini API: {e}")


async def generate_daily_mystery_content(theme: str, image_style_modifier: str) -> Dict[str, Any]:
    print(
        f"AI Service: Generating daily mystery content using google-genai SDK for theme '{theme}', style '{image_style_modifier}'")

    current_prompt = DAILY_MYSTERY_PROMPT_TEMPLATE.format(
        theme=theme,
        image_style_modifier=image_style_modifier
    )
    try:
        response_json = await _call_gemini_model_with_config(
            prompt_text=current_prompt,
            system_instruction_text=SYSTEM_INSTRUCTION_JSON_OUTPUT,
            temperature=0.8,
            max_output_tokens=4096,
            is_json_output_expected=True
        )

        expected_keys = ["base_story_text", "actual_solution_text", "initial_choices_pool",
                         "character_dossiers", "critical_path_clues", "base_image_prompts"]
        for key in expected_keys:
            if key not in response_json:
                print(
                    f"ERROR: Gemini response for daily content missing key '{key}'. Full JSON: {json.dumps(response_json, indent=2)}")
                raise ValueError(
                    f"Gemini response missing expected key: {key} in daily content.")

        parsed_dossiers = []
        if isinstance(response_json.get("character_dossiers"), list):
            for dossier_data in response_json["character_dossiers"]:
                try:
                    validated_dossier = CharacterDossierItem(**dossier_data)
                    parsed_dossiers.append(
                        validated_dossier.model_dump())
                except Exception as e:
                    print(
                        f"Warning: Could not parse/validate a character dossier: {dossier_data}. Error: {e}")

        response_json["character_dossiers"] = parsed_dossiers
        return response_json
    except Exception as e:
        print(f"ERROR in generate_daily_mystery_content: {e}")
        raise HTTPException(
            status_code=503, detail=f"AI service currently unavailable for daily content: {type(e).__name__}")


async def generate_theme_and_art_style_for_mystery_type(
    mystery_type: str
) -> Dict[str, str]:
    print(
        f"AI Service: Generating theme and art style for Mystery Type: '{mystery_type}'")

    art_style_list_string = "\n".join(
        [f"- {name}" for name in AVAILABLE_ART_STYLE_NAMES])

    current_prompt = THEME_AND_STYLE_GENERATION_PROMPT_TEMPLATE.format(
        mystery_type=mystery_type,
        art_style_list_str=art_style_list_string
    )

    try:
        response_json = await _call_gemini_model_with_config(
            prompt_text=current_prompt,
            system_instruction_text=SYSTEM_INSTRUCTION_JSON_OUTPUT,
            temperature=0.8,
            max_output_tokens=256,
            is_json_output_expected=True
        )

        if not isinstance(response_json, dict) or \
           "theme_title" not in response_json or \
           "selected_art_style" not in response_json:
            print(
                f"ERROR: AI response for theme/style missing keys. Got: {response_json}")
            raise ValueError(
                "AI response missing 'theme_title' or 'selected_art_style'.")

        theme_title = response_json["theme_title"]
        selected_art_style = response_json["selected_art_style"]

        if not isinstance(theme_title, str) or not theme_title.strip():
            print(
                f"ERROR: AI returned an invalid or empty theme_title. Got: {theme_title}")
            raise ValueError("AI returned an invalid theme_title.")

        if selected_art_style not in AVAILABLE_ART_STYLE_NAMES:
            print(
                f"ERROR: AI selected an art style ('{selected_art_style}') not in the allowed list. Defaulting.")
            raise ValueError(
                f"AI selected an invalid art style: '{selected_art_style}'. It must be from the provided list.")

        return {
            "theme_title": theme_title.strip(),
            "selected_art_style": selected_art_style
        }

    except ValueError as ve:
        print(f"ValueError during theme/style generation: {ve}")
        raise
    except ConnectionError as ce:
        print(f"ConnectionError during theme/style generation: {ce}")
        raise
    except Exception as e:
        print(
            f"ERROR in generate_theme_and_art_style (Unexpected): {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        raise ConnectionError(
            f"Unexpected error during AI theme/style generation: {type(e).__name__}")


async def generate_next_scenario_content(
    base_story_summary: str,
    actual_solution: str,
    user_choice: str,
    current_scenario_text: Optional[str],
    image_style_modifier: str,
    current_round: int,
    history_summary: Optional[str] = None
) -> Dict[str, Any]:
    logger.debug(
        f"AI Service: Generating next scenario. Round: {current_round}. Choice: '{user_choice}'. History provided: {bool(history_summary)}"
    )

    prompt_context_parts = [
        f"Mystery Base: \"{base_story_summary}\"",
        f"Actual Hidden Solution: \"{actual_solution}\" (This is the true answer. DO NOT REVEAL IT to the player. Use it to guide the story, clues, and red herrings based on the player's choices. Ensure the narrative is consistent with this solution.)",
    ]
    if history_summary:
        prompt_context_parts.append(
            f"\nPlayer's Journey So Far:\n{history_summary}")

    if current_round >= settings.MAX_ROUNDS:
        prompt_context_parts.append(
            f"\nPlayer has completed {settings.MAX_ROUNDS} rounds. The game concludes now.")
        prompt_context_parts.append(
            f"Last presented scenario before this conclusion: \"{current_scenario_text if current_scenario_text else 'Initial story context.'}\"")
        prompt_context_parts.append(
            f"Player's final choice was: \"{user_choice}\"")

        task_instruction = TASK_INSTRUCTION_FINAL.format(
            image_style_modifier=image_style_modifier
        )
    else:
        prompt_context_parts.append(
            f"\nCurrent Round to Generate: {current_round}")
        prompt_context_parts.append(
            f"Previously Displayed Scenario (that led to player's current choice): \"{current_scenario_text if current_scenario_text else 'This is the initial interaction after the base story.'}\"")
        prompt_context_parts.append(
            f"Player's Chosen Action from that scenario: \"{user_choice}\"")

        task_instruction = TASK_INSTRUCTION_ROUND.format(
            image_style_modifier=image_style_modifier,
            MAX_ROUNDS=settings.MAX_ROUNDS
        )

    full_prompt_text = "\n".join(
        prompt_context_parts) + "\n\n" + task_instruction

    try:
        response_json = await _call_gemini_model_with_config(
            prompt_text=full_prompt_text,
            system_instruction_text=SYSTEM_INSTRUCTION_JSON_OUTPUT,
            temperature=0.8,
            max_output_tokens=2048,
            is_json_output_expected=True
        )
        if not isinstance(response_json.get("is_final_round"), bool):
            raise ValueError(
                "AI response for 'is_final_round' was not a boolean.")
        if response_json.get("is_final_round") is False and response_json.get("solution_explanation") is not None:
            raise ValueError(
                "AI set 'solution_explanation' when 'is_final_round' is false.")
        if not isinstance(response_json.get("choices"), list):
            raise ValueError("AI response for 'choices' was not a list.")
        if response_json.get("is_final_round") is False and len(response_json.get("choices", [])) != 3:
            logger.warning(
                f"AI returned {len(response_json.get('choices', []))} choices instead of 3 for a non-final round. Trying to adapt or will raise error.")
            if len(response_json.get("choices", [])) != 3:
                raise ValueError(
                    "AI did not return exactly 3 choices for a non-final round.")

        return response_json
    except Exception as e:
        logger.error(
            f"ERROR in generate_next_scenario_content: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=503, detail=f"AI service currently unavailable for next scenario: {type(e).__name__}")
