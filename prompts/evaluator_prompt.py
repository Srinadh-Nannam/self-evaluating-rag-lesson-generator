def build_evaluator_prompt(topic: str, audience: str, lesson_content: str) -> str:
    return f'''You are a strict reviewer of beginner educational lessons.
Topic: {topic}
Audience: {audience}

Review factual correctness, beginner-friendly language, useful examples, unexplained jargon,
coverage of required concepts, and logical teaching flow. Treat each checkpoint as pass/fail.
Do not award acceptance because headings exist. Point out claims that are misleading or unsupported.
Return JSON only with keys: score (0-10), verdict (accepted/rejected), summary,
issues (array), suggested_improvements (array). This review is advisory; mandatory local checks
are applied separately by the application.

LESSON:\n{lesson_content}'''
