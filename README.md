# Self-Evaluating RAG Lesson Generator

A Python-based self-evaluating lesson generation workflow that creates a beginner-friendly lesson on Retrieval-Augmented Generation (RAG), evaluates it against mandatory educational quality checks, and regenerates rejected lessons using feedback.

The project runs completely offline and does not require an API key.

## What It Does

1. Collects the lesson topic, target audience, duration, learning objectives, and optional source material.
2. Builds a generation prompt using previous feedback stored in memory.
3. Generates a beginner-friendly RAG lesson using the local offline generator.
4. Evaluates the lesson using a deterministic hard rubric with 17 mandatory checkpoints.
5. Rejects lessons that fail mandatory checks.
6. Uses rejection feedback for regeneration, with a maximum of two retries (three total attempts).
7. Stores rejection history and learning feedback for future runs.
8. Saves accepted lessons and evaluation reports.

## Architecture

- `app.py` – Command-line application entry point.
- `agents/generator.py` – Lesson generation and offline fallback implementation.
- `agents/evaluator.py` – Lesson evaluation and acceptance logic.
- `agents/workflow.py` – Workflow orchestration, retries, rejection logs, and memory.
- `prompts/` – Generator and evaluator prompt builders.
- `utils/evaluation_utils.py` – Rubric checks and JSON persistence utilities.
- `memory/` – Persistent learning memory and rejection history.
- `output/` – Generated lesson and evaluation report.
- `tests/` – Automated tests for lesson acceptance, rejection, regeneration, memory, and retry limits.

## Setup

### Requirements

- Python 3
- Windows, Linux, or macOS

### Windows Setup

Create a virtual environment:

```bash
py -m venv env
```

Activate it:

```bash
env\Scripts\activate
```

Install dependencies:

```bash
py -m pip install -r requirements.txt
```

No OpenAI API key or internet connection is required to run the offline workflow.

## Run the Application

```bash
py app.py
```

Enter the requested topic, audience, duration, learning objectives, and optional source material.

The application generates the lesson, evaluates it, and saves the result.

## Run Automated Tests

```bash
py -m unittest discover -s tests -v
```

The tests run without an API key or network connection.

## Evaluation Policy

The evaluator uses 17 mandatory pass/fail checkpoints.

These include:

- Lesson title and overview
- Learning objectives
- Beginner-friendly explanation
- Practical example
- Activities and assessment
- Summary
- Coherent teaching flow
- Adequate lesson depth
- Definition and purpose of RAG
- Documents and chunking
- Embeddings
- Vector database
- Retrieval
- Generation and grounding
- Step-by-step RAG workflow
- Comparison between a traditional LLM workflow and RAG

Every mandatory checkpoint must pass for a lesson to be accepted. A numerical score alone cannot approve a lesson.

## Retry and Memory Mechanism

The workflow supports an initial generation attempt and a maximum of two retries.

When a lesson is rejected:

1. The evaluator identifies failed checkpoints.
2. Rejection reasons are stored in the rejection log.
3. Feedback is stored in persistent learning memory.
4. The feedback is included in the next generation prompt.
5. The regenerated lesson is evaluated again.

The memory mechanism stores feedback and makes it available to future prompts. It does not train or fine-tune an AI model.

## Output Files

- `output/final_lesson.md` – Final accepted lesson.
- `output/rejected_lesson.md` – Lesson saved when all attempts fail.
- `output/evaluation_report.json` – Evaluation results and attempt history.
- `memory/rejection_logs.json` – Rejection history.
- `memory/learning_memory.json` – Stored feedback from previous attempts.

## Limitations

- The offline generator uses predefined, template-authored RAG lesson content rather than live LLM generation.
- The deterministic rubric checks required content and structure but cannot guarantee complete factual accuracy.
- Human review is recommended before publishing educational material.
- The workflow's persistent memory stores feedback; it does not independently learn by modifying model weights.

## Project Verification

The project has been tested using automated unit tests.

Latest test results:

- 4 automated tests passed.
- 17 out of 17 evaluation checkpoints passed for the generated RAG lesson.
- Rejection and regeneration workflow verified.
- Maximum retry limit verified.
- Offline execution verified without an API key.

## Execution Mode

**Default mode:** Offline/local fallback.

**API key required:** No.

The project is designed to demonstrate a self-evaluating lesson generation workflow without requiring paid API access.