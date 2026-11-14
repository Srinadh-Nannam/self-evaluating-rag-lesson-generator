# from pathlib import Path
# from typing import Any

# from agents.evaluator import LessonEvaluator
# from agents.generator import LessonGenerator, FallbackLessonGenerator
# from prompts.generator_prompt import build_generator_prompt
# from prompts.evaluator_prompt import build_evaluator_prompt
# from utils.document_generator import DocumentGenerator
# from utils.evaluation_utils import load_json, save_json


# class LessonWorkflow:
#     def __init__(self, output_dir: str | Path, rejection_log_path: str | Path, learning_memory_path: str | Path,
#                  generator=None, evaluator=None, max_retries: int = 2):
#         self.output_dir = Path(output_dir)
#         self.rejection_log_path = Path(rejection_log_path)
#         self.learning_memory_path = Path(learning_memory_path)
#         self.generator = generator or LessonGenerator()
#         self.evaluator = evaluator or LessonEvaluator()
#         self.document_generator = DocumentGenerator(self.output_dir)
#         self.max_retries = max(0, min(int(max_retries), 2))

#     def _read_memory(self) -> str:
#         entries = load_json(self.learning_memory_path)
#         if not entries:
#             return "No prior feedback stored."
#         return "\n".join(f"- Topic: {x.get('topic', 'unknown')}; lesson feedback: {x.get('feedback', '')}" for x in entries[-5:])

#     def _record(self, path: Path, item: dict[str, Any]) -> None:
#         rows = load_json(path)
#         rows.append(item)
#         save_json(path, rows)

#     def generate_lesson(self, topic: str, audience: str, duration: str = "30 minutes",
#                         learning_objectives: list[str] | None = None, source_material: str = "") -> dict[str, Any]:
#         objectives = learning_objectives or [f"Explain {topic} in simple words.", f"Describe how {topic} works.", f"Give a practical example of {topic}."]
#         memory = self._read_memory()
#         feedback = ""
#         attempts: list[dict[str, Any]] = []
#         lesson = ""
#         generation_mode = "unknown"

#         for attempt in range(self.max_retries + 1):
#             prompt = build_generator_prompt(topic, audience, duration, objectives, source_material, memory, feedback)
#             try:
#                 lesson = self.generator.generate(prompt)
#                 generation_mode = getattr(self.generator, "last_mode", "configured_generator")
#             except Exception as exc:
#                 # Offline mode is explicit and produces substantive RAG content, never a generic placeholder.
#                 lesson = FallbackLessonGenerator(topic, audience).generate(prompt)
#                 generation_mode = f"local_fallback ({type(exc).__name__})"

#             evaluation = self.evaluator.evaluate(
#                 lesson, topic, audience,
#                 prompt=build_evaluator_prompt(topic, audience, lesson),
#             )
#             passed = evaluation.get("verdict") == "accepted" and not evaluation.get("issues")
#             attempts.append({
#                 "attempt": attempt + 1,
#                 "verdict": "accepted" if passed else "rejected",
#                 "score": evaluation.get("score", 0),
#                 "issues": evaluation.get("issues", []),
#                 "generation_mode": generation_mode,
#             })
#             if passed:
#                 break

#             feedback = "\n".join(evaluation.get("issues", []) + evaluation.get("suggested_improvements", []))
#             log_entry = {"topic": topic, "audience": audience, "attempt": attempt + 1,
#                          "reason": evaluation.get("summary", "Mandatory rubric failed."),
#                          "issues": evaluation.get("issues", []), "feedback_sent_to_generator": feedback}
#             self._record(self.rejection_log_path, log_entry)
#             self._record(self.learning_memory_path, {
#                 "topic": topic, "audience": audience, "feedback": feedback,
#                 "failed_checkpoints": [k for k, v in evaluation.get("checks", {}).items() if not v],
#                 "attempt": attempt + 1,
#             })

#         accepted = bool(attempts and attempts[-1]["verdict"] == "accepted")
#         status = "accepted" if accepted else "rejected"
#         final_path = self.document_generator.save_lesson(lesson, "final_lesson.md") if accepted else self.document_generator.save_lesson(lesson, "rejected_lesson.md")
#         report = {
#             "topic": topic, "status": status, "max_retries": self.max_retries,
#             "attempts": attempts, "final_evaluation": evaluation,
#             "generation_mode": generation_mode,
#             "note": "Fallback generation is local template-based content; configure OPENAI_API_KEY for model-generated lessons." if "fallback" in generation_mode else "Model-generated lesson.",
#         }
#         self.document_generator.save_lesson(__import__("json").dumps(report, indent=2, ensure_ascii=False), "evaluation_report.json")
#         return {"success": accepted, "status": status, "lesson": lesson, "evaluation": evaluation,
#                 "attempts": attempts, "path": str(final_path), "report_path": str(self.output_dir / "evaluation_report.json"),
#                 "generation_mode": generation_mode}




from pathlib import Path
from typing import Any

from agents.evaluator import LessonEvaluator
from agents.generator import FallbackLessonGenerator
from prompts.generator_prompt import build_generator_prompt
from prompts.evaluator_prompt import build_evaluator_prompt
from utils.document_generator import DocumentGenerator
from utils.evaluation_utils import load_json, save_json


class LessonWorkflow:
    def __init__(
        self,
        output_dir: str | Path,
        rejection_log_path: str | Path,
        learning_memory_path: str | Path,
        generator=None,
        evaluator=None,
        max_retries: int = 2,
    ):
        self.output_dir = Path(output_dir)
        self.rejection_log_path = Path(rejection_log_path)
        self.learning_memory_path = Path(learning_memory_path)

        # Offline generation is the default.
        self.generator = generator
        self.evaluator = evaluator or LessonEvaluator()
        self.document_generator = DocumentGenerator(self.output_dir)
        self.max_retries = max(0, min(int(max_retries), 2))

    def _read_memory(self) -> str:
        entries = load_json(self.learning_memory_path)

        if not entries:
            return "No prior feedback stored."

        return "\n".join(
            f"- Topic: {x.get('topic', 'unknown')}; "
            f"lesson feedback: {x.get('feedback', '')}"
            for x in entries[-5:]
        )

    def _record(self, path: Path, item: dict[str, Any]) -> None:
        rows = load_json(path)
        rows.append(item)
        save_json(path, rows)

    def generate_lesson(
        self,
        topic: str,
        audience: str,
        duration: str = "30 minutes",
        learning_objectives: list[str] | None = None,
        source_material: str = "",
    ) -> dict[str, Any]:

        objectives = learning_objectives or [
            f"Explain {topic} in simple words.",
            f"Describe how {topic} works.",
            f"Give a practical example of {topic}.",
        ]

        memory = self._read_memory()
        feedback = ""
        attempts = []
        lesson = ""
        evaluation = {}

        for attempt in range(self.max_retries + 1):

            prompt = build_generator_prompt(
                topic,
                audience,
                duration,
                objectives,
                source_material,
                memory,
                feedback,
            )

            # Use local generation directly; no API connection.
            active_generator = self.generator

            if active_generator is None:
                active_generator = FallbackLessonGenerator(topic, audience)

            lesson = active_generator.generate(prompt)

            generation_mode = "local_fallback"

            evaluation = self.evaluator.evaluate(
                lesson,
                topic,
                audience,
                prompt=build_evaluator_prompt(topic, audience, lesson),
            )

            passed = (
                evaluation.get("verdict") == "accepted"
                and not evaluation.get("issues")
            )

            attempts.append({
                "attempt": attempt + 1,
                "verdict": "accepted" if passed else "rejected",
                "score": evaluation.get("score", 0),
                "issues": evaluation.get("issues", []),
                "generation_mode": generation_mode,
            })

            if passed:
                break

            feedback = "\n".join(
                evaluation.get("issues", [])
                + evaluation.get("suggested_improvements", [])
            )

            self._record(
                self.rejection_log_path,
                {
                    "topic": topic,
                    "audience": audience,
                    "attempt": attempt + 1,
                    "reason": evaluation.get(
                        "summary", "Mandatory rubric failed."
                    ),
                    "issues": evaluation.get("issues", []),
                    "feedback_sent_to_generator": feedback,
                },
            )

            self._record(
                self.learning_memory_path,
                {
                    "topic": topic,
                    "audience": audience,
                    "feedback": feedback,
                    "failed_checkpoints": [
                        key
                        for key, value in evaluation.get("checks", {}).items()
                        if not value
                    ],
                    "attempt": attempt + 1,
                },
            )

        accepted = bool(
            attempts and attempts[-1]["verdict"] == "accepted"
        )

        status = "accepted" if accepted else "rejected"

        filename = (
            "final_lesson.md"
            if accepted
            else "rejected_lesson.md"
        )

        final_path = self.document_generator.save_lesson(
            lesson, filename
        )

        report = {
            "topic": topic,
            "status": status,
            "max_retries": self.max_retries,
            "attempts": attempts,
            "final_evaluation": evaluation,
            "generation_mode": "local_fallback",
            "note": "Generated and evaluated locally. No API key required.",
        }

        import json

        self.document_generator.save_lesson(
            json.dumps(report, indent=2, ensure_ascii=False),
            "evaluation_report.json",
        )

        return {
            "success": accepted,
            "status": status,
            "lesson": lesson,
            "evaluation": evaluation,
            "attempts": attempts,
            "path": str(final_path),
            "report_path": str(
                self.output_dir / "evaluation_report.json"
            ),
            "generation_mode": "local_fallback",
        }
