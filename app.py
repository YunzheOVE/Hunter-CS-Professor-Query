"""
app.py  —  Milestone 5: Generation and Interface

Wires together:
  1. retrieve()  from embed.py   — semantic search over ChromaDB
  2. Groq API    (llama-3.3-70b-versatile) — grounded answer generation
  3. Gradio UI   — web interface at http://localhost:7860

Grounding rule: the LLM is instructed to answer ONLY from the provided
review excerpts. If the excerpts don't cover the question, it must say so.
Source attribution is appended programmatically after generation.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
from embed import retrieve

# ── API setup ────────────────────────────────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL  = "llama-3.3-70b-versatile"

# ── Prompt templates ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a helpful assistant that answers questions about Computer Science \
professors at Hunter College based solely on student reviews from \
Rate My Professors.

STRICT RULES:
1. Answer ONLY using information found in the review excerpts provided below \
   in the user message. Do NOT use any outside knowledge.
2. If the excerpts do not contain enough information to answer the question, \
   respond with exactly: "I don't have enough information in the reviews to \
   answer that."
3. Never invent details, ratings, or quotes that are not in the excerpts.
4. Keep answers concise and factual.
"""

CONTEXT_TEMPLATE = """\
QUESTION: {question}

REVIEW EXCERPTS (use only these to answer):
{context}

Answer the question based strictly on the excerpts above."""


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block."""
    lines = []
    for i, c in enumerate(chunks, 1):
        header = f"[{i}] Professor: {c['professor']} | Course: {c['course'] or 'N/A'}"
        lines.append(header)
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def build_sources(chunks: list[dict]) -> str:
    """Programmatically build a source list from retrieved metadata."""
    seen   = set()
    source_lines = []
    for c in chunks:
        key = (c["professor"], c["source"])
        if key not in seen:
            seen.add(key)
            source_lines.append(f"- {c['professor']}  ({c['source']})")
    return "\n".join(source_lines)


def ask(question: str, k: int = 5) -> dict:
    """
    End-to-end RAG pipeline.

    Returns:
        {"answer": str, "sources": list[str], "chunks": list[dict]}
    """
    question = question.strip()
    if not question:
        return {"answer": "Please enter a question.", "sources": [], "chunks": []}

    # Step 1 — Retrieve relevant chunks
    chunks = retrieve(question, k=k)

    # Step 2 — Build context and call Groq
    context     = build_context(chunks)
    user_message = CONTEXT_TEMPLATE.format(question=question, context=context)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,   # low temperature keeps answers factual
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    # Step 3 — Programmatic source attribution
    sources_text = build_sources(chunks)

    return {
        "answer":  answer,
        "sources": sources_text,
        "chunks":  chunks,
    }


# ── Gradio UI ─────────────────────────────────────────────────────────────────
def handle_query(question: str):
    """Gradio handler: returns (answer_text, sources_text)."""
    result = ask(question)
    return result["answer"], result["sources"]


with gr.Blocks(title="Hunter CS Professor Reviews") as demo:
    gr.Markdown(
        """
        # Hunter College CS Professor Reviews
        Ask any question about CS professors at Hunter College based on
        student reviews from **Rate My Professors**.

        _Examples:_
        - "What do students say about Saad Mneimneh's exam difficulty?"
        - "Is Melissa Lynch responsive to student emails?"
        - "Which professors are known for being hard graders?"
        """
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. What do students say about Eric Schweitzer's teaching style?",
            lines=2,
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=8, interactive=False)
        sources_box = gr.Textbox(label="Sources (retrieved reviews)", lines=4, interactive=False)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

    gr.Markdown(
        "_Answers are grounded in student reviews only. "
        "If the reviews don't cover your question, the system will say so._"
    )


if __name__ == "__main__":
    print("Starting Hunter CS Professor Reviews RAG system...")
    print("Loading embedding model and vector store...")
    # Pre-warm the retriever so the first query is fast
    from embed import get_collection
    get_collection()
    print("Ready! Opening Gradio UI...")
    demo.launch()
