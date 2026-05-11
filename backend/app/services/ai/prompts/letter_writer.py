from app.services.ai.prompts.template_builder import build_prompt_template


def build_prompt(language: str) -> str:
    return build_prompt_template(
        tool_name="letter-writer",
        language=language,
        task_rules=[
            "Write respectful, realistic letters and applications appropriate for Nepali schools, offices, banks, and public services.",
            "Use concise language and avoid exaggerated promises or legal claims.",
            "If key details are missing, include clearly labeled placeholders instead of inventing facts.",
            "Prefer practical wording that a user can copy and edit quickly.",
        ],
        output_format=[
            "Use headings: Subject, Greeting, Body, Closing.",
            "Use short paragraphs or bullets in Body when helpful.",
            "End with heading: Next steps and include 2 to 4 actionable edits the user should customize.",
            "Do not include markdown code blocks.",
        ],
    )
