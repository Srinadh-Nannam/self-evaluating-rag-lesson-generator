"""Evaluation, JSON persistence, and hard pass/fail rubric utilities."""
import json
import re
from pathlib import Path
from typing import Any


def parse_json_response(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    if not text:
        return {"score": 0, "verdict": "rejected", "summary": "No evaluation returned.", "issues": ["Evaluator returned empty content."], "suggested_improvements": ["Run evaluation again."]}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        try:
            data = json.loads(text[start:end + 1]) if start >= 0 and end > start else None
        except json.JSONDecodeError:
            data = None
    if not isinstance(data, dict):
        return {"score": 0, "verdict": "rejected", "summary": "Invalid evaluator response.", "issues": ["Evaluation response was not valid JSON."], "suggested_improvements": ["Return the required JSON schema."]}
    return data


def load_json(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_json(path: str | Path, data: list[dict[str, Any]]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    temp = p.with_suffix(p.suffix + ".tmp")
    temp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(p)


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def rule_based_score(lesson_text: str, topic: str, audience: str) -> dict[str, Any]:
    """Apply non-negotiable checks. All mandatory checks must pass to accept."""
    text = re.sub(r"\s+", " ", (lesson_text or "").lower())
    is_rag = "rag" in topic.lower() or "retrieval-augmented" in topic.lower()
    checks: dict[str, bool] = {
        "title_and_overview": bool(re.search(r"(?m)^# .+", lesson_text or "")) and "overview" in text,
        "learning_objectives": "learning objectives" in text and ("understand" in text or "explain" in text),
        "beginner_friendly_explanation": _has_any(text, ("artificial intelligence", "ai is", "computer program")) and _has_any(text, ("simple words", "in simple terms", "think of", "imagine")),
        "practical_example": _has_any(text, ("real-world example", "real world example", "college", "library", "student")) and _has_any(text, ("for example", "example:")),
        "practice_and_assessment": _has_any(text, ("activities", "practice", "activity")) and _has_any(text, ("assessment", "check your understanding", "quiz")),
        "summary": "summary" in text,
        "coherent_teaching_flow": all(term in text for term in ("introduction", "how", "example", "summary")),
        "adequate_depth": len((lesson_text or "").split()) >= 450,
    }
    if is_rag:
        checks.update({
            "defines_rag": _has_any(text, ("retrieval-augmented generation", "retrieval augmented generation")) and _has_any(text, ("retrieves", "searches", "finds relevant")),
            "explains_why_rag": _has_any(text, ("why use rag", "why do we need rag", "why rag")) and _has_any(text, ("outdated", "up-to-date", "private documents", "external information", "new or private", "hallucination")),
            "explains_documents_and_chunking": "document" in text and _has_any(text, ("chunk", "smaller pieces", "small sections")),
            "explains_embeddings": "embedding" in text and _has_any(text, ("numbers", "numerical", "vector")),
            "explains_vector_database": _has_any(text, ("vector database", "vector store")) and _has_any(text, ("stores", "save", "keeps")),
            "explains_retrieval": "retrieval" in text and _has_any(text, ("search", "find", "similarity")),
            "explains_generation_and_grounding": _has_any(text, ("large language model", "llm")) and _has_any(text, ("retrieved", "search results", "source information")),
            "step_by_step_workflow": _has_any(text, ("step 1", "1.")) and _has_any(text, ("step 4", "4.")) and _has_any(text, ("step 5", "5.")),
            "traditional_ai_comparison": _has_any(text, ("traditional ai", "without rag")) and _has_any(text, ("with rag", "rag system")),
        })
    passed = sum(checks.values())
    total = len(checks)
    issues = [f"Failed checkpoint: {name.replace('_', ' ')}." for name, ok in checks.items() if not ok]
    improvements = [issue.replace("Failed checkpoint: ", "Improve: ") for issue in issues]
    return {
        "score": round(10 * passed / total),
        "verdict": "accepted" if all(checks.values()) else "rejected",
        "summary": f"Hard rubric: {passed}/{total} checkpoints passed. Acceptance requires every mandatory checkpoint to pass.",
        "checks": checks,
        "passed_checkpoints": passed,
        "total_checkpoints": total,
        "issues": issues,
        "suggested_improvements": improvements,
        "evaluation_method": "deterministic_hard_rubric",
    }
