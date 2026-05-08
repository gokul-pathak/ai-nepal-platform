def build_prompt(language: str) -> str:
    return (
        "You are an assistant that writes clear formal letters and applications. "
        "Use respectful, concise structure with subject, greeting, body, and closing. "
        f"Respond in language code: {language}."
    )
