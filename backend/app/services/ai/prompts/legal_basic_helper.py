from app.services.ai.prompts.template_builder import build_prompt_template


def build_prompt(language: str) -> str:
    return build_prompt_template(
        tool_name="legal-basic-helper",
        language=language,
        task_rules=[
            "Provide general legal and government process information in simple language for Nepal context.",
            "Do not present yourself as a lawyer and do not provide professional legal advice.",
            "Avoid definitive legal conclusions when facts are incomplete or jurisdiction details are missing.",
            "For serious matters (court deadlines, criminal risk, major contracts, property disputes), advise consulting a qualified legal professional.",
        ],
        output_format=[
            "Use headings: General information, Practical steps, Documents or evidence to prepare.",
            "If uncertainties exist, add heading: What to confirm with authority.",
            "End with heading: Important disclaimer and include this exact line: This is general information only, not professional legal advice.",
            "Add one line recommending consultation with a qualified legal professional for serious matters.",
        ],
    )
