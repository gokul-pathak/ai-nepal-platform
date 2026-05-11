from app.services.ai.prompts.template_builder import build_prompt_template


def build_prompt(language: str) -> str:
    return build_prompt_template(
        tool_name="translator",
        language=language,
        task_rules=[
            "Translate the user text accurately between Nepali and English while preserving intent, tone, and key details.",
            "Keep names, addresses, numbers, dates, and codes unchanged unless the user explicitly asks for conversion.",
            "If user intent is ambiguous, provide the most likely translation and add one brief note with an alternative.",
            "Do not add new claims, interpretations, or facts that are not in the source text.",
        ],
        output_format=[
            "Use heading: Translation.",
            "Provide only the translated text first.",
            "If needed, add heading: Notes with short bullets for ambiguity or culturally sensitive phrasing.",
            "Keep output compact and practical.",
        ],
    )
