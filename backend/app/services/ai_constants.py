
DEFAULT_GEMINI_MODEL_NAME_STRING = "gemini-2.0-flash"

DAILY_MYSTERY_PROMPT_TEMPLATE = """
Generate a complete daily mystery game setup.

**Core Requirements:**
- **Theme:** "{theme}"
- **Visual Style for Images:** Evoke "{image_style_modifier}" (this should primarily influence the 'base_image_prompts').
- **Target Audience Engagement:** The mystery must be intriguing yet solvable by a general audience, using clear, conversational language.
- **Red Herrings:** Include at least two subtle red herrings woven into character secrets or events to mislead players.
- **Twist:** The 'actual_solution_text' must include an unexpected twist that is logical, fresh, and not a cliché (avoid overusing faked deaths or insurance fraud).

**Output Structure (Strict JSON Object):**
Output a single JSON object with these exact keys and value types:
- "base_story_text": (String) An engaging, clear opening narrative for the mystery (approximately 150–250 words). Introduce the setting, the main characters, and the core puzzle or incident. Use simple, vivid language suitable for a broad audience — avoid overly complex words.
- "actual_solution_text": (String) The true solution to the mystery (100–150 words). Reveal the hidden truth and clearly explain how the player could deduce it from the clues. Do not repeat the entire story setup; focus on what was truly happening behind the scenes and why.
- "initial_choices_pool": (Array of exactly 10 Strings) Ten unique, plausible initial actions or questions a player might use to investigate. Make each choice specific to the mystery’s people, objects, or locations — avoid generic actions like “Investigate further.”
- "character_dossiers": (Array of 4 to 5 Objects) Each object represents a key character with these exact keys:
    - "character_name": (String) The character’s full name.Use unique character names.
    - "description": (String) A concise physical description and their initial connection to the mystery. (30–50 words)
    - "potential_secrets_or_motives": (String) Hints of secrets, quirks, or possible motives — ideally including at least one misleading clue to serve as a red herring. (30–50 words)
- "critical_path_clues": (Array of 2 to 3 Strings) Essential clues, observations, or pieces of information that a player must find to logically deduce the solution. Ensure they connect clearly to the twist.
- "base_image_prompts": (Array of exactly 2 Strings) Two detailed DALL·E image prompts depicting vivid scenes from the 'base_story_text'. Incorporate the visual style: "{image_style_modifier}". Example: "A cluttered detective’s desk lit by a single desk lamp, old case files scattered around, in style: {image_style_modifier}."

**Additional Quality Guidelines:**
- **Clarity & Simplicity:** Use short, clear sentences. Avoid unnecessarily complex or literary vocabulary.
- **Immersive Details:** Characters, settings, and choices should feel rich and authentic to the mystery’s theme.
- **Red Herrings:** Each character dossier must subtly mislead the player about their guilt or involvement.
- **Solution Variety:** Each mystery’s solution should feel fresh and not repeat common twists more than once in a week.
- **Consistency:** All parts must align logically — clues, story, and solution must fit together with no contradictions.

Respond with only the JSON object and no extra text.
"""


THEME_AND_STYLE_GENERATION_PROMPT_TEMPLATE = """
You are a creative assistant for a mystery game.
Your task is to generate a compelling, one-line mystery theme/title and select the most suitable art style for it.

**Input Information:**
1.  **Mystery Type:** {mystery_type}
2.  **Available Art Styles (Choose ONE from this list):**
    {art_style_list_str}

**Task:**
1.  Based on the given **Mystery Type**, create a succinct, intriguing, one-line theme or title for a mystery story. The title itself should be the theme.
2.  From the **Available Art Styles** list, select the ONE art style that you believe would best visually represent the generated theme and the given mystery type.

**Output Requirements (Strict JSON Object):**
Your entire response MUST be a single, valid JSON object with the following exact keys:
- "theme_title": (String) The generated one-line mystery theme/title.
- "selected_art_style": (String) The name of the ONE art style chosen from the provided list. It must be an exact match to one of the names in the "Available Art Styles" list.
"""

SYSTEM_INSTRUCTION_JSON_OUTPUT = """
You are a creative assistant meticulously generating content for a mystery game.
Your output MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting outside of this JSON object.
The JSON object must strictly adhere to the schema provided in the user prompt, including all specified keys and data types.
Pay close attention to array and object structures.
"""

MYSTERY_TYPES = [
    "Classic Murder Mystery: Whodunit",
    "Theft/Heist: Who stole the MacGuffin?",
    "Missing Person/Pet: Where did they go?",
    "Sabotage: Who is trying to ruin the event/company?",
    "Supernatural/Paranormal: Is it a ghost, or a clever human?",
    "Espionage/Intrigue: Uncover the spy or secret plot",
    "Silly/Comedic Mystery: e.g., 'Who replaced all the office coffee with decaf?'",
    "Historical Mystery: Solve a cold case from a bygone era",
    "Sci-Fi Mystery: e.g., on a space station, future tech involved"
]

ART_STYLES_WITH_DESCRIPTIONS = [
    {"name": "Film Noir", "description": "Stark black and white, dramatic shadows, gritty classic detective feel."},
    {"name": "Gritty Comic Book",
        "description": "Bold lines, strong inks, dynamic action, graphic novel feel."},
    {"name": "Watercolor Illustration",
        "description": "Soft, blended colors, ethereal, dreamlike quality, ambiguity."},
    {"name": "Pixel Art", "description": "Retro, nostalgic, charmingly simplified, for lighthearted/puzzle focus."},
    {"name": "Neo-Expressionist",
        "description": "Distorted figures, vibrant clashing colors, intense emotion, unease."},
    {"name": "Low Poly 3D",
        "description": "Geometric shapes, minimalist 3D rendering, modern and stylized."},
    {"name": "Victorian Engraving",
        "description": "Highly detailed, intricate linework, historical, macabre feel."},
    {"name": "Psychedelic Pop",
        "description": "Bright, contrasting colors, swirling patterns, surreal vibe."},
    {"name": "Traditional Japanese Woodblock Print",
        "description": "Bold outlines, flat colors, classic Ukiyo-e aesthetic."},
    {"name": "Art Deco Illustration",
        "description": "Elegant lines, geometric patterns, sophisticated 1920s/30s glamour."},
    {"name": "Gothic Revival Painting",
        "description": "Dark, dramatic, ornate, historical detail, foreboding sense."},
    {"name": "Cyberpunk Dystopian",
        "description": "Neon lights, rain-slicked streets, advanced tech, dark futuristic."},
    {"name": "Impressionistic Brushstrokes",
        "description": "Blurry, soft edges, focus on light/atmosphere, fleeting moments."},
    {"name": "Hand-Drawn Sketch",
        "description": "Raw, unfinished look, artist's notebook, authentic intimate feel."}
]

# For the AI prompt, we only need the names of the art styles
AVAILABLE_ART_STYLE_NAMES = [style["name"]
                             for style in ART_STYLES_WITH_DESCRIPTIONS]
