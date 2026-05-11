from app.services.ai.prompts.template_builder import build_prompt_template


def build_prompt(language: str) -> str:
    return build_prompt_template(
        tool_name="form-helper",
        language=language,
        task_rules=[
            "Help users fill forms correctly with clear, concise entries.",
            "Identify required fields and explain what to write in plain language.",
            "Do not invent personal data, IDs, legal numbers, or official references.",
            "If a field is unclear, provide 1 short clarification question or a safe generic template.",
        ],
        output_format=[
            "Use heading: Form guidance.",
            "Provide bullets in this order: Field, What to write, Example.",
            "When useful, add heading: Common mistakes to avoid with 2 to 5 bullets.",
            "Keep examples realistic for Nepal context.",
        ],
    )
