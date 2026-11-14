import json
import tempfile
import unittest
from pathlib import Path

from agents.generator import FallbackLessonGenerator
from agents.workflow import LessonWorkflow
from utils.evaluation_utils import rule_based_score

TOPIC = "Introduction to RAG (Retrieval-Augmented Generation)"
AUDIENCE = "12th-grade graduate in India with limited English vocabulary; complete beginner"


class SequenceGenerator:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = 0
        self.last_mode = "test_fixture"

    def generate(self, prompt):
        self.calls += 1
        return self.outputs.pop(0)


class WorkflowTests(unittest.TestCase):
    def test_generic_bad_lesson_is_rejected(self):
        result = rule_based_score("# RAG\n## Overview\n## Learning Objectives\n## Introduction\nThis is a lesson.\n## Example\n## Activities\n## Assessment\n## Summary", TOPIC, AUDIENCE)
        self.assertEqual(result["verdict"], "rejected")
        self.assertTrue(result["issues"])

    def test_substantive_offline_rag_lesson_passes_rubric(self):
        lesson = FallbackLessonGenerator(TOPIC, AUDIENCE).generate("")
        result = rule_based_score(lesson, TOPIC, AUDIENCE)
        self.assertEqual(result["verdict"], "accepted", result["issues"])

    def test_rejection_then_regeneration_and_memory(self):
        good = FallbackLessonGenerator(TOPIC, AUDIENCE).generate("")
        bad = "# RAG\n## Overview\n## Learning Objectives\n## Introduction\n## Example\n## Activities\n## Assessment\n## Summary"
        generator = SequenceGenerator([bad, good])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            flow = LessonWorkflow(root / "output", root / "memory" / "rejections.json", root / "memory" / "learning.json", generator=generator, max_retries=2)
            result = flow.generate_lesson(TOPIC, AUDIENCE)
            self.assertEqual(result["status"], "accepted")
            self.assertEqual(len(result["attempts"]), 2)
            self.assertEqual(result["attempts"][0]["verdict"], "rejected")
            self.assertEqual(result["attempts"][1]["verdict"], "accepted")
            self.assertTrue(json.loads((root / "memory" / "rejections.json").read_text()))
            self.assertTrue(json.loads((root / "memory" / "learning.json").read_text()))
            self.assertTrue((root / "output" / "final_lesson.md").exists())

    def test_retry_limit_is_two(self):
        bad = "# RAG\n## Overview\n## Learning Objectives\n## Introduction\n## Example\n## Activities\n## Assessment\n## Summary"
        generator = SequenceGenerator([bad, bad, bad])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            flow = LessonWorkflow(root / "output", root / "rejections.json", root / "learning.json", generator=generator, max_retries=9)
            result = flow.generate_lesson(TOPIC, AUDIENCE)
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(len(result["attempts"]), 3)
            self.assertTrue((root / "output" / "rejected_lesson.md").exists())


if __name__ == "__main__":
    unittest.main()
