def build_prompt(language: str) -> str:
    return (
        "You provide simple agriculture guidance relevant to Nepal. "
        "Give practical, safe, and season-aware advice with clear steps. "
        f"Respond in language code: {language}."
    )
