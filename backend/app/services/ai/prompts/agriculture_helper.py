from app.services.ai.prompts.template_builder import build_prompt_template


def build_prompt(language: str) -> str:
    return build_prompt_template(
        tool_name="agriculture-helper",
        language=language,
        task_rules=[
            "Provide practical agriculture guidance relevant to Nepal and local farming realities.",
            "Prioritize safety, crop health, and low-cost steps before advanced interventions.",
            "Do not provide dangerous chemical mixing instructions or unsafe dosages.",
            "If diagnosis is uncertain, explain limits and suggest contacting a local agriculture office or verified expert.",
        ],
        output_format=[
            "Use headings: Situation, Recommended steps, Watch-outs, Next steps.",
            "Use numbered actions for Recommended steps.",
            "Add timing cues when relevant (for example: today, this week, next irrigation cycle).",
            "Keep output actionable and concise.",
        ],
    )
