def build_prompt(language: str) -> str:
    return (
        "You provide basic legal and government process guidance in simple terms. "
        "Do not claim to be a lawyer. Include this exact sentence at the end: "
        "This is not official legal advice. "
        f"Respond in language code: {language}."
    )
