import os
from typing import Any

from utils.evaluation_utils import rule_based_score, parse_json_response
from prompts.evaluator_prompt import build_evaluator_prompt

try:
    from openai import OpenAI
except ImportError:  # local rubric remains available without the SDK
    OpenAI = None


class LessonEvaluator:
    """A hard local rubric is the acceptance gate; an LLM review is advisory."""
    def __init__(self, model: str | None = None, api_key: str | None = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=key) if OpenAI and key else None

    def evaluate(self, lesson_content: str, topic: str, audience: str, prompt: str | None = None) -> dict[str, Any]:
        hard_result = rule_based_score(lesson_content, topic, audience)
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt or build_evaluator_prompt(topic, audience, lesson_content)}],
                    temperature=0,
                    max_tokens=900,
                )
                advisory = parse_json_response(response.choices[0].message.content or "")
                hard_result["llm_review"] = advisory
            except Exception as exc:
                hard_result["llm_review"] = {"status": "unavailable", "reason": str(exc)[:300]}
        # Never allow a model or a numerical score to override failed hard checkpoints.
        hard_result["verdict"] = "accepted" if all(hard_result.get("checks", {}).values()) else "rejected"
        return hard_result
