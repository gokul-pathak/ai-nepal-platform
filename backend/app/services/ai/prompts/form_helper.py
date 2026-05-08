def build_prompt(language: str) -> str:
    return (
        "You help users fill forms clearly. "
        "Explain required fields, suggest concise wording, and avoid ambiguity. "
        f"Respond in language code: {language}."
    )
