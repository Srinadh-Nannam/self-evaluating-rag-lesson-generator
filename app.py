from pathlib import Path
from dotenv import load_dotenv
from agents.workflow import LessonWorkflow


def main() -> None:
    load_dotenv()
    root = Path(__file__).resolve().parent
    workflow = LessonWorkflow(root / "output", root / "memory" / "rejection_logs.json", root / "memory" / "learning_memory.json", max_retries=2)

    topic = input("Enter the lesson topic: ").strip() or "Introduction to RAG (Retrieval-Augmented Generation)"
    audience = input("Enter the target audience: ").strip() or "12th-grade graduate in India; beginner with limited English vocabulary"
    duration = input("Enter the lesson duration (default: 30 minutes): ").strip() or "30 minutes"
    raw = input("Enter learning objectives separated by commas (optional): ").strip()
    objectives = [x.strip() for x in raw.split(",") if x.strip()] or None
    source = input("Paste any source material (optional, press Enter to skip): ").strip()

    result = workflow.generate_lesson(topic, audience, duration, objectives, source)
    print("\n=== Lesson Generation Result ===")
    print(f"Status: {result['status']}")
    print(f"Generation mode: {result['generation_mode']}")
    print(f"Attempts: {len(result['attempts'])}")
    print(f"Evaluation: {result['evaluation']}")
    print(f"Saved lesson: {result['path']}")
    print(f"Evaluation report: {result['report_path']}")
    print("\nAttempt history:")
    for item in result["attempts"]:
        print(f"  Attempt {item['attempt']}: {item['verdict']} (score {item['score']})")
        for issue in item["issues"]:
            print(f"    - {issue}")
    print("\nGenerated lesson:\n")
    print(result["lesson"])


if __name__ == "__main__":
    main()
