from typing import Iterable


def build_generator_prompt(topic: str, audience: str, duration: str, learning_objectives: Iterable[str], source_material: str, learning_memory: str, feedback: str = "") -> str:
    objectives = "\n".join(f"- {x.strip()}" for x in learning_objectives if x.strip())
    source = source_material.strip() or "No source material was supplied. Use established, broadly accepted concepts and do not invent citations."
    return f'''You are an instructional designer and patient AI tutor.
Create a complete standalone {duration} beginner lesson on: {topic}
Learner: {audience}
Assume the learner starts from zero. Use short sentences, explain every technical term on first use,
and use familiar Indian student examples. Avoid unexplained jargon and generic filler.

Learning objectives:\n{objectives}

Source material (if supplied, prioritize it and do not claim unsupported facts):\n{source}

Lessons from previous runs:\n{learning_memory}

Evaluator feedback from the previous attempt (fix every point):\n{feedback or 'This is the first attempt; follow all requirements carefully.'}

For Introduction to RAG, cover: what AI and a large language model are; a clear definition of
Retrieval-Augmented Generation (RAG); why RAG is useful and its limits; traditional AI/LLM without
RAG versus a RAG system; documents and chunking; embeddings as numerical representations of meaning;
vector databases; retrieval; how retrieved information is given to an LLM to generate a grounded answer;
a numbered end-to-end workflow; a worked college-notes example; limitations and responsible use.
Explain the difference between retrieval and generation. Do not say RAG guarantees truth.

Required structure:
# Lesson title
## Overview
## Learning Objectives
## Prerequisites
## Lesson Content
### Introduction to AI and language models
### What is RAG and why use it?
### Important building blocks
### How RAG works step by step (at least five numbered steps)
### Traditional AI/LLM versus RAG
### Worked real-world example
### Benefits and limitations
## Activities / Practice
## Assessment / Reflection (include at least three questions and answers)
## Summary

Make the lesson detailed enough to teach, not just list terms. Output only Markdown.'''
