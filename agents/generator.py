import os
from typing import Any

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LessonGenerator:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key) if OpenAI and self.api_key else None
        self.last_mode = "openai" if self.client else "local_fallback"

    def generate(self, prompt: str) -> str:
        if self.client is None:
            raise RuntimeError("OpenAI is not configured; use the explicit local fallback generator.")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=3500,
        )
        self.last_mode = "openai"
        return response.choices[0].message.content or ""


class FallbackLessonGenerator:
    """Substantive offline lesson for the fixed RAG assignment, not a generic placeholder."""
    def __init__(self, topic: str, audience: str):
        self.topic, self.audience = topic, audience

    def generate(self, prompt: str) -> str:
        return f'''# Introduction to RAG (Retrieval-Augmented Generation)

## Overview
This 30-minute beginner lesson explains how an AI system can search trusted documents before writing an answer. It is written for {self.audience}. No previous knowledge of Artificial Intelligence is needed.

## Learning Objectives
By the end of this lesson, you will be able to:
- Explain Artificial Intelligence (AI), a Large Language Model (LLM), and Retrieval-Augmented Generation (RAG) in simple words.
- Explain why RAG is useful and what it cannot guarantee.
- Describe documents, chunks, embeddings, a vector database, retrieval, and generation.
- Explain the RAG workflow step by step and compare an LLM without RAG with a RAG system.
- Give a real-world example of RAG using college documents.

## Prerequisites
You only need to know how to read a document and ask a question. A document can be a PDF, a Word file, a webpage, or a text file.

## Lesson Content

### Introduction to AI and language models
Artificial Intelligence (AI) means computer systems doing tasks that normally need human thinking, such as understanding a question or finding a pattern. Generative AI is a type of AI that creates new content, such as text, images, or code.

A Large Language Model (LLM) is an AI model trained on a very large amount of text. It can understand a question and write a response. A chatbot is one familiar way to use an LLM. An LLM can sometimes give an incorrect answer or may not know information from a new or private document.

### What is RAG and why use it?
RAG means **Retrieval-Augmented Generation**. In simple terms, a RAG system first searches for useful information in documents and then gives the selected information to an LLM. The LLM uses that retrieved information to generate an answer.

The word retrieval means finding and bringing back useful information. Augmented means added or supported. Generation means creating a response. So RAG combines searching with answer writing.

**Why use RAG?** An ordinary LLM may not have access to your college's latest timetable, company policy, or private notes. RAG can search those external documents at question time. This can make an answer more relevant and easier to check. It can also reduce unsupported answers, but RAG does not guarantee that every answer is true. The documents, search results, and generated answer still need checking.

### Important building blocks

**1. Documents:** These are the information sources used by the system, such as college notes, PDF files, manuals, or approved webpages. The quality and freshness of these documents matter.

**2. Chunking:** A long document is divided into smaller pieces called chunks. Imagine dividing a 100-page textbook into short sections. Smaller chunks help the system search for the part related to a question instead of sending the whole book every time.

**3. Embeddings:** An embedding is a list of numbers that represents the meaning of a piece of text. A computer can compare these numerical representations to find text with a similar meaning. Text with related meaning may have embeddings that are close in the vector space. An embedding is not a summary and does not prove that the text is correct.

**4. Vector database:** A vector database (also called a vector store) stores embeddings and links them to their text chunks and document details. It helps search for chunks whose meaning is similar to the user's question. It is like a searchable digital library organized for meaning, not only exact words.

**5. Retrieval:** Retrieval is the search step. The system converts the user's question into an embedding and searches the vector database for relevant chunks. It selects the best matching information. A search can miss useful information, so retrieval quality matters.

**6. Generation:** The selected chunks are placed into a prompt with the user's question. The Large Language Model reads the question and the retrieved source information, then writes an answer. A well-designed system can also show which documents support the answer.

### How RAG works step by step

1. **Collect documents:** The system receives approved files, such as a student's college notes or an employee handbook.
2. **Split into chunks:** It divides each document into smaller sections while keeping enough surrounding context.
3. **Create embeddings:** An embedding model changes each chunk into a numerical representation of its meaning.
4. **Store in a vector database:** The system saves each embedding with its text and source details.
5. **Receive a question:** A user asks a question. The system creates an embedding for that question.
6. **Retrieve relevant chunks:** The vector database searches for chunks with similar meaning and returns the most useful matches.
7. **Generate an answer:** The system gives the retrieved text and the question to the LLM. The LLM writes an answer based on the supplied information.
8. **Show and check the answer:** The application displays the answer and, where possible, its source documents. A person should check important information.

The first four steps are usually called document preparation or indexing. The last four steps happen when a user asks a question.

### Traditional AI/LLM versus RAG

| Without RAG | With RAG |
|---|---|
| The LLM answers using information available in its model and the current prompt. | The system searches selected external documents and gives useful results to the LLM. |
| It may not know a new college notice or private company policy. | It can use a current notice or approved policy if that document is indexed and retrieved. |
| It may be difficult to check where a detail came from. | The application can show the retrieved source chunks. |
| It does not perform a document search as part of this workflow. | Retrieval is an explicit part of the workflow. |

RAG does not replace the LLM. It gives the LLM extra information at answer time. The LLM still writes the final response.

### Worked real-world example: asking about college notes

Imagine your college has uploaded a PDF containing its attendance rules. A student asks, “How many days can I be absent and still meet the attendance rule?”

First, the college PDF is split into chunks. The system creates embeddings for those chunks and stores them in a vector database. When the student asks the question, the system creates an embedding for the question and retrieves the chunk about attendance. It sends that chunk and the question to the LLM. The LLM writes a simple answer and may point to the attendance section of the PDF.

If the correct attendance rule is not present in the PDF, the system should say that it cannot find the information rather than inventing a number. This example shows how RAG uses college documents to answer a student's question.

### Benefits and limitations

Benefits: RAG can use private or recently updated documents, make answers more relevant to a specific organization, and provide source references for checking.

Limitations: The documents may be old or incorrect; chunking may remove important context; retrieval may find the wrong section; and the LLM may misunderstand the retrieved text. RAG is not a guarantee of truth, privacy, or perfect search. Sensitive documents need access controls, and important answers need human verification.

## Activities / Practice
1. In your own words, explain why a college might use RAG for its student handbook.
2. Match each term to its job: chunking (splitting text), embedding (turning meaning into numbers), vector database (storing and searching vectors), retrieval (finding useful text), generation (writing the answer).
3. Draw eight boxes for the eight workflow steps and connect them with arrows.
4. Ask what could go wrong if the college handbook is out of date. Write one safe response the system should give.

## Assessment / Reflection

**1. What does RAG stand for?**  
Answer: Retrieval-Augmented Generation. It searches for useful information and gives it to an LLM to help create an answer.

**2. What is an embedding?**  
Answer: It is a list of numbers that represents the meaning of text so a computer can compare related pieces of text.

**3. What does a vector database do?**  
Answer: It stores embeddings with their text chunks and helps find chunks related to a question.

**4. Does RAG guarantee a correct answer?**  
Answer: No. The source documents or search results may be wrong or incomplete, and the LLM may still make a mistake.

## Summary
RAG stands for Retrieval-Augmented Generation. It connects document search with AI answer writing. Documents are split into chunks, chunks are converted into embeddings, and a vector database stores them. When a user asks a question, retrieval finds useful chunks. An LLM uses those chunks to generate an answer. RAG is useful when answers need information from selected or updated documents, but people must still check important answers and sources.
'''
