# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
This system covers student reviews of Computer Science professors at Hunter College, sourced from RateMyProfessors. This knowledge is valuable because official course descriptions and the college website tell you nothing about a professor's actual teaching style, how fair their exams are, how responsive they are to students, or what grade to realistically expect. Students rely on word-of-mouth and informal reviews to make course registration decisions, but that information is scattered and difficult to come up with a decision. This system solves this problem by making it queryable in plain language and gives a objective opinion based on students' informal reviews on RateMyProfessors.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Melissa Lynch | CS professor reviews — 45 student reviews, CSCI127/CSCI160 | https://www.ratemyprofessors.com/professor/2505090 |
| 2 | Saad Mneimneh | CS professor reviews — 80 student reviews, CSCI150/STAT319 | https://www.ratemyprofessors.com/professor/926045 |
| 3 | Jaime Canizales | CS professor reviews — 25 student reviews, CSCI265/CSCI335 | https://www.ratemyprofessors.com/professor/2505175 |
| 4 | Eric Schweitzer | CS professor reviews — 65 student reviews | https://www.ratemyprofessors.com/professor/257192 |
| 5 | Katherine St. John | CS professor reviews — 40 student reviews | https://www.ratemyprofessors.com/professor/2324096 |
| 6 | Justin Tojeira | CS professor reviews — 60 student reviews | https://www.ratemyprofessors.com/professor/1660967 |
| 7 | Tong Yi | CS professor reviews — 50 student reviews | https://www.ratemyprofessors.com/professor/2634841 |
| 8 | Pavel Shostak | CS professor reviews — 55 student reviews | https://www.ratemyprofessors.com/professor/1823870 |
| 9 | Tiziana Ligorio | CS professor reviews — 60 student reviews | https://www.ratemyprofessors.com/professor/815879 |
| 10 | Sven Dietrich | CS professor reviews — 38 student reviews | https://www.ratemyprofessors.com/professor/2674099 |
| 11 | Mahdi Makki | CS professor reviews — 38 student reviews | https://www.ratemyprofessors.com/professor/2157279 |
| 12 | Oyewole Oyekoya | CS professor reviews — 27 student reviews | https://www.ratemyprofessors.com/professor/2558461 |
| 13 | Ioannis Stamos | CS professor reviews — 26 student reviews | https://www.ratemyprofessors.com/professor/64427 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
Chunk size: Structure-based chunking. One review per chunk (about 100-400 characters per review). Each review are already organized and structured this way in the documents folder.
**Overlap:**
None since each review is already structured in a self-contained unit with a clear boundary.
**Reasoning:**
Each review is a complete thought about one professor. A single reivew chunk gives a direct and retrievable answer. A fixed character chunking would be worse here because a fixed number of 500-character chunk might merge 3 short reviews together which could result in bad output (doesn't answer the question directly)

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
Embedding model: all-MiniLM-L6-v2 via sentence-transformers. Runs locally, fast, and well-suited for short, opinion-based text like reviews.
**Top-k:**
Top-k: 5. This gives the LLM good amount of student reviews to formulate an answer from. Not too much to generate noises and not too little to lose context/relevant info.
**Production tradeoff reflection:**
For a production deployment perspective, I would consider switching to a larger LLM model like OpenAI's text-embedding-3-small. The main tradeoffs would be the cost(1), accuracy(2), and latency(3). 

Cost(1): the API cost for bigger and smarter model like OpenAI would be higher compared to the all-MiniLM-L6-v2 which is free.
Accuracy(2): larger LLM will capture naunced details and synthesis a better and more subjective output especially from informal student reviews. It also allows bigger context, great for long reviews to avoid cut-off.
Latency(3): local model is limited by CPU speed, while an API model adds network latency in exchange of faster latency on hardware.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Saad Mneimneh's exam difficulty in CSCI150? | Students consistently describe exams as extremely difficult, requiring 1–2 weeks of studying. However, he curves exams and offers extra credit, which helps students pass. |
| 2 | Is Jaime Canizales a good professor to take at Hunter College? | Yes — students overwhelmingly praise him (4.9/5 overall, 100% would take again). Reviews call him clear, caring, and approachable, with an easy grading structure. |
| 3 | What are the main complaints students have about Sven Dietrich? | Students complain about pop quizzes on random topics, individual printed exams, boring slide-reading lectures, harsh grading, and a condescending attitude toward students. |
| 4 | Does Melissa Lynch respond to student emails? | No — multiple reviews across CSCI127 and CSCI160 specifically mention that she does not respond to emails, which is one of the most repeated complaints about her. |
| 5 | Which CS professor at Hunter College is considered the easiest to get a good grade with? | Jaime Canizales is mentioned most often as easy to pass, with students saying the minimum exam grade is a 70 and that he allows multiple attempts on assignments. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Professor name variation in queries: Students in reviews sometimes refer to professors by first name or last name only or nickname. This could be an issue because if a user query uses a different form of the name than what appears in the chunks, the embedding similarity may be low and retrieval may return reviews from unrelated professors.

2. Comparison from multiple professors: Questions like "Who is the best professor?" require the system to retrieve and compare chunks across all professors. However, since the top-k = 5, the retrieval may return chunks from only 1-2 professors, disregarding other good professors, making the response somewhat inaccurate.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

┌─────────────────────────────────────────────────────────────────────┐
│                        USER QUERY                                   │
│                  (plain-language question)                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 1 — Document Ingestion                                        │
│  Tool: Python (clean_documents.py)                                   │
│  • Read 13 .txt files from documents/                                │
│  • Each file contains cleaned Rate My Professors reviews             │
│  • Output: raw text per professor file                               │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 2 — Chunking                                                  │
│  Strategy: Structure-based (one review per chunk)                    │
│  • Split each file on [Review N] boundaries                          │
│  • Each chunk = one student review + metadata header                 │
│  • No overlap (reviews are already self-contained units)             │
│  • Expected output: ~608 chunks across 13 professors                 │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 3 — Embedding + Vector Store                                  │
│  Embedding model: all-MiniLM-L6-v2 (sentence-transformers)           │
│  Vector store: ChromaDB (local)                                      │
│  • Each chunk is converted to a 384-dimension vector                 │
│  • Stored in ChromaDB with metadata: professor name, source file     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 4 — Retrieval                                                 │
│  • User query is embedded with the same all-MiniLM-L6-v2 model       │
│  • ChromaDB performs cosine similarity search                        │
│  • Returns top-k=5 most relevant chunks + their source metadata      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 5 — Generation                                                │
│  LLM: Groq API (llama-3.3-70b-versatile)                             │
│  Interface: Gradio web UI                                            │
│  • Retrieved chunks passed as context in system prompt               │
│  • LLM instructed to answer only from provided context               │
│  • Response includes source attribution (professor name + file)      │
└──────────────────────────────────────────────────────────────────────┘

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will give Claude the Chunking Strategy section and the Architecture diagram from this planning.md, along with a sample cleaned .txt file from documents/ so it can see the exact format. I will ask it to implement an ingest.py script that reads all .txt files in documents/, splits each file into individual review chunks by detecting [Review N] boundaries, and stores each chunk as a dictionary with keys: text, source, professor, course, quality, difficulty. I will verify the output by printing 5 random chunks and confirming each one is a single complete review with no HTML artifacts, no empty strings, and correct source attribution.

**Milestone 4 — Embedding and retrieval:**
I will give Claude the Retrieval Approach section and the Architecture diagram from this planning.md. I will ask it to implement an embed.py script that loads chunks from ingest.py, embeds them using sentence-transformers (all-MiniLM-L6-v2), stores them in a local ChromaDB collection with professor name and source file as metadata, and exposes a retrieve(query, k=5) function that returns the top-k chunks and their distance scores. I will verify by running 3 of my evaluation plan queries and checking that the returned chunks visibly relate to each question and have distance scores below 0.5.

**Milestone 5 — Generation and interface:**
I will give Claude the Generation requirements from documents.md (grounding instruction, source attribution, out-of-scope refusal) and the Gradio skeleton code provided in the project spec. I will ask it to implement an app.py that wires together retrieve() and a Groq API call using llama-3.3-70b-versatile, with a system prompt that instructs the model to answer only from retrieved chunks and to cite the source professor and file in every response. I will verify by testing an in-scope query (checking that the answer cites a source), an out-of-scope query (checking that the system declines rather than hallucinating), and comparing the response text against the retrieved chunks to confirm grounding.
