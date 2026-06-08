# The Unofficial Guide — Project 1

---

## Domain

This system covers student reviews of Computer Science professors at Hunter College, sourced from Rate My Professors. This knowledge is valuable because official course descriptions and the college website tell you nothing about a professor's actual teaching style, how fair their exams are, how responsive they are to students, or what grade to realistically expect. Students rely on word-of-mouth and informal reviews to make course registration decisions, but that information is scattered across individual professor pages and hard to search. This system solves that by making the reviews queryable in plain language, returning grounded answers based on real student opinions rather than official course catalog descriptions.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Melissa Lynch | Rate My Professors — 45 student reviews, CSCI127/CSCI160 | https://www.ratemyprofessors.com/professor/2505090 |
| 2 | Saad Mneimneh | Rate My Professors — 80 student reviews, CSCI150/STAT319 | https://www.ratemyprofessors.com/professor/926045 |
| 3 | Jaime Canizales | Rate My Professors — 25 student reviews, CSCI265/CSCI335 | https://www.ratemyprofessors.com/professor/2505175 |
| 4 | Eric Schweitzer | Rate My Professors — 65 student reviews, CS265 | https://www.ratemyprofessors.com/professor/257192 |
| 5 | Katherine St. John | Rate My Professors — 40 student reviews | https://www.ratemyprofessors.com/professor/2324096 |
| 6 | Justin Tojeira | Rate My Professors — 60 student reviews | https://www.ratemyprofessors.com/professor/1660967 |
| 7 | Tong Yi | Rate My Professors — 50 student reviews | https://www.ratemyprofessors.com/professor/2634841 |
| 8 | Pavel Shostak | Rate My Professors — 55 student reviews | https://www.ratemyprofessors.com/professor/1823870 |
| 9 | Tiziana Ligorio | Rate My Professors — 60 student reviews | https://www.ratemyprofessors.com/professor/815879 |
| 10 | Sven Dietrich | Rate My Professors — 38 student reviews | https://www.ratemyprofessors.com/professor/2674099 |
| 11 | Mahdi Makki | Rate My Professors — 38 student reviews | https://www.ratemyprofessors.com/professor/2157279 |
| 12 | Oyewole Oyekoya | Rate My Professors — 27 student reviews | https://www.ratemyprofessors.com/professor/2558461 |
| 13 | Ioannis Stamos | Rate My Professors — 26 student reviews | https://www.ratemyprofessors.com/professor/64427 |

---

## Chunking Strategy

**Chunk size:** 
Structure-based chunking: one student review per chunk. Each review is approximately 100–400 characters. The boundaries are defined by `[Review N]` markers that were added during the cleaning stage (`clean_documents.py`).

**Overlap:** 
None. Each review is a self-contained unit with a clear start and end boundary. There is no information that spans multiple reviews that would require overlap to preserve context.

**Why these choices fit your documents:** 
Each review is a complete thought about one professor. A single reivew chunk gives a direct and retrievable answer (limited noises, output the best answer). A fixed character chunking would be worse here because a fixed number of 500-character chunk might merge 3 short reviews together which could result in bad output (diluted, doesn't answer the question directly)

**Final chunk count:** 
609 chunks across 13 professor files.

---

## Sample Chunks
`python ingest.py`
Five representative chunks drawn from the vector store, each a complete self-contained student review:

**Chunk 1**
- Source: `jaime-canizales.txt` | Professor: Jaime Canizales | Course: CSCI265
- Quality: 5.0 | Difficulty: 2.0
- Text: *"Makes the material easier to digest and his tests were fair. As long you do the homework and have an understanding of it, then you shouldn't have a problem passing the course."*

**Chunk 2**
- Source: `eric-schweitzer.txt` | Professor: Eric Schweitzer | Course: CS265
- Quality: 5.0 | Difficulty: 4.0
- Text: *"Honestly I understand a lot of the 1 ratings and 5 difficulty the pop quizzes he gives are stress inducing. However he gives optional HW that basically mirror the quizzes so just do and understand the HW and this class should be less stressful."*

**Chunk 3**
- Source: `melissa-lynch.txt` | Professor: Melissa Lynch | Course: CSCI160
- Quality: 1.0 | Difficulty: 2.0
- Text: *"There is nothing else I can say that hasn't already been mentioned before. I don't know why the professor of a class is waiting till the very last minute to upload our grades."*

**Chunk 4**
- Source: `mahdi-makki.txt` | Professor: Mahdi Makki | Course: CSCI133
- Quality: 4.0 | Difficulty: 1.0
- Text: *"He was super understanding with me. I took his online class but was unable to complete it, and even though it was online he gave me the opportunity to credit/no credit. He was great though and reached out to me when I wasn't submitting assignments."*

**Chunk 5**
- Source: `mahdi-makki.txt` | Professor: Mahdi Makki | Course: CSCI435
- Quality: 5.0 | Difficulty: 3.0
- Text: *"I am currently enrolled in Professor Makki's Summer II online class. He cares about his students and provides comprehensive notes. He explains technical concepts simply, making it easier to understand."*

Each chunk makes sense on its own. A viewer could read any one of them and understand a student's opinion about that professor without needing any surrounding context.

---

## Embedding Model

**Model used:** 
`all-MiniLM-L6-v2` via `sentence-transformers`. This model runs entirely locally (no API key, no cost), is fast on CPU, and is well-suited for short opinion-based text like student reviews. It maps each review into a 384-dimensional vector, enabling cosine similarity search in ChromaDB.

One additional design decision: before embedding each chunk, I prepend the professor's full name and source filename to the text — e.g., `"Professor Melissa Lynch (melissa-lynch.txt): She doesn't reply to emails..."`. This means the embedding encodes the professor's identity as part of the vector signal, which significantly improved name-specific retrieval accuracy. The original review text (without the prefix) is what gets stored and returned to the user.

Overall, this additional design decision help improves retrieval for name-specific queries like "Does Lynch answer emails?". It also showed significant improvement, went from 0.4-0.5 average distance (with embedded identity) to 0.3 average distance (without embedded identity), yielding perfect top-k = 5 relevant chunking.

**Production tradeoff reflection:** 
For a real deployment, I would consider switching to OpenAI's `text-embedding-3-small` or a similar API-hosted model. 

Cost(1): the API cost for bigger and smarter model like OpenAI would be higher compared to the `all-MiniLM-L6-v2` which is free.
Accuracy(2): larger LLM will capture naunced details and synthesis a better and more subjective output especially from informal student reviews. It also allows bigger context, great for long reviews to avoid cut-off.
Latency(3): local model is limited by CPU speed, while an API model adds network latency in exchange of faster latency on hardware.

---

## Retrieval Test Results

**Query 1:** "What do students say about Saad Mneimneh exam difficulty in CSCI150?"

Top chunks returned:
  [1] Saad Mneimneh | saad-mneimneh.txt | distance: 0.286 [good]
      Class was very hard and confusing , homeworks and tests were torture , but the very good test curve is the only reason I passed

  [2] Saad Mneimneh | saad-mneimneh.txt | distance: 0.2935 [good]
      Not a bad professor, just a hard class. Makes the topic very approachable and teaches the material in a way that is easy to remember. Tests aren't the hardest but the questions can get a little too creative and confusing. Do the homework, make sure y...

  [3] Saad Mneimneh | saad-mneimneh.txt | distance: 0.305 [good]
      The exams are hard but theres partial credit. The hw was difficult too and there was 1 due every week. Despite the coursework itself being hard, he was understanding and gave a good curve for each exam. If you study well and don't fall behind on lect...

  [4] Saad Mneimneh | saad-mneimneh.txt | distance: 0.3063 [good]
      His lectures are incredibly confusing with minimal explanations to help. Even for the more simple concepts he will end up explaining in a way that makes it way more confusing then it needed to be. His tests are absurdly difficult. Any high reviews ar...

  [5] Saad Mneimneh | saad-mneimneh.txt | distance: 0.3177 [good]
      Professor Saad's class was not easy, but he really just wants you to learn as much as you can. The topics themselves are very complex and his lectures+slides make them easier to understand. He gave 1 homework a week, and it would take days of thinkin...

Why relevant: All 5 chunks are from the same professor and course, directly describing exam experiences. The name prepending strategy ensured the query matched Mneimneh's reviews specifically rather than pulling generic "hard exam" reviews from other professors.

---

**Query 2:** "Does Melissa Lynch respond to student emails?"

Top chunks returned:
  [1] Melissa Lynch | melissa-lynch.txt | distance: 0.2266 [good]
      She dont answer her emails. Shes either late 15-30 mins or doesn't even show up. Shes difficult to work with as a professor.

  [2] Melissa Lynch | melissa-lynch.txt | distance: 0.2611 [good]
      All the materials are on the class website, she explains well in lectures and can replace any bad grades by doing well in the final, overall, she is a great class and professor. One complain I do have is that she never replies to emails.

  [3] Melissa Lynch | melissa-lynch.txt | distance: 0.2926 [good]
      Nice lady but a terrible professor. No student should have to experience sending an email about opinions on doing pnc and never receive a response back.

  [4] Melissa Lynch | melissa-lynch.txt | distance: 0.2977 [good]
      The professor was unprofessional: she often arrived late, didn't respond to emails, failed to upload promised videos, didn't allow regrades, and frequently canceled classes without notice. On top of that, she assigned a heavy workload at the end of t...

  [5] Melissa Lynch | melissa-lynch.txt | distance: 0.3039 [good]
      Comes to class 30 minutes late, grades late, doesn't respond to emails, talks absolute nonsense to waste lecture time, and uploads review quizzes the night before exams, or not at all. She lied about the contents inside the final exam. The final was ...

Why relevant: "respond to emails" is a specific recurring complaint in Lynch's reviews. The embedding for the query closely matched the language students used ("doesn't respond", "ignores emails"), producing consistent and accurate retrieval.

---

**Query 3:** "Which CS professor at Hunter College is considered the easiest to get a good grade with?"

Top chunks returned:
  [1] Jaime Canizales | jaime-canizales.txt | distance: 0.2271 [good]
      He is one of the best professor in Hunter. He is one reason I am still in CS major. I feel like he understands student's problem so as long as you put your effort, he grades you. As long as you do all homework and study his lectures, you will get an ...

  [2] Tiziana Ligorio | tiziana-ligorio.txt | distance: 0.2847 [good]
      Most of the people here in these did not take many CS courses at Hunter yet and it shows. Compared to most of the other professors in the department shes really good.

  [3] Eric Schweitzer | eric-schweitzer.txt | distance: 0.3118 [good]
      The 1st time you take Eric, you'll think he's hot garbag at teaching. The 2nd time, you'll realize how much better he is compared to most CS profs at Hunter. The course was fair but difficult. Focus on quizzes (60% of your grade!!). You'll likely hav...

  [4] Melissa Lynch | melissa-lynch.txt | distance: 0.3187 [good]
      She's the best!! Honestly the best CS professor at Hunter!

  [5] Justin Tojeira | justin-tojeira.txt | distance: 0.324 [good]
      to keep it short, justin is one of the best cs professors at hunter but he SHOULD NOT be teaching 335. like everyone else said, hes EXTREMELY unorganized, late with grades/autograders/project deadlines, and had us do 2 PROJECTS + study for the final ...

Why relevant: This is a cross-professor comparison query. Retrieval returned chunks from 5 different professors because the question is broad enough to match any review that mentions grading ease. This is expected behavior given top-k = 5 (expected 5 different professors).

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a helpful assistant that answers questions about Computer Science
professors at Hunter College based solely on student reviews from
Rate My Professors.

STRICT RULES:
1. Answer ONLY using information found in the review excerpts provided below
   in the user message. Do NOT use any outside knowledge.
2. If the excerpts do not contain enough information to answer the question,
   respond with exactly: "I don't have enough information in the reviews to
   answer that."
3. Never invent details, ratings, or quotes that are not in the excerpts.
4. Keep answers concise and factual.
```

The system prompt is sent as the `"system"` role in every API call, making it a persistent constraint across all queries. Rule 1 explicitly forbids outside knowledge. Rule 2 forces a refusal response for out-of-scope questions rather than allowing the model to fill gaps with training data. Rule 3 prevents fabricated quotes.

**How source attribution is surfaced in the response:** 
The `build_sources()` function in `app.py` reads the `professor` and `source` metadata fields directly from the retrieved chunks and formats them into a source list. This list is displayed in a separate "Sources" box in the UI. The LLM does not decide which sources to cite; the code extracts them from retrieval metadata, guaranteeing that every response is traceable to actual documents.

---

## Example Responses

**Example 1 — In-scope query with source citation:**

> **Question:** "What are the main complaints students have about Sven Dietrich?"
>
> **Answer:** The main complaints students have about Sven Dietrich are:
> - Refuses to take questions
> - Poor instruction (e.g., "hieroglyphic instructions", reading word by word from PPT)
> - Unprofessional and condescending attitude
> - Slow at returning grades
> - Possibly using prerecorded videos instead of teaching live
>
> **Sources:** - Sven Dietrich (sven-dietrich.txt)

---

**Example 2 — In-scope query with source citation:**

> **Question:** "Is Jaime Canizales a good professor to take at Hunter College?"
>
> **Answer:** Yes, according to the review excerpts, Jaime Canizales is a good professor to take at Hunter College. All the reviews are extremely positive, describing him as the "GOAT", "a blessing", "genuinely nice guy", and stating that he is fair, caring, and willing to help his students.
>
> **Sources:** - Jaime Canizales (jaime-canizales.txt)

---

**Example 3 — Out-of-scope query showing refusal:**

> **Question:** "What is the best restaurant near Hunter College?"
>
> **Answer:** I don't have enough information in the reviews to answer that.
>
> **Sources:** (reviews from unrelated professors were retrieved but the LLM correctly refused to use them)

---

## Query Interface

**Input field:** 
A text box labeled "Your question" where the user types a plain-language question about any Hunter College CS professor.

**Output fields:**
- **Answer** — A multi-line text box showing the LLM-generated response.
- **Sources (retrieved reviews)** — A text box listing the professor(s) and source file(s) that the retrieved chunks came from, built programmatically from retrieval metadata.

**Triggering a query:** Either click the "Ask" button or press Enter in the question box.

**Sample interaction transcript:**

```
User:    Does Melissa Lynch respond to student emails?

Answer:  No, according to the review excerpts, Melissa Lynch does not respond
         to student emails. This is mentioned in all five excerpts.

Sources: - Melissa Lynch  (melissa-lynch.txt)
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Saad Mneimneh's exam difficulty in CSCI150? | Exams extremely difficult; curves help students pass | Exams described as "hard", "torture", "creative and confusing"; mentions partial credit | Relevant | Accurate |
| 2 | Is Jaime Canizales a good professor to take at Hunter College? | Yes — praised for clarity, caring, easy grading | Yes — described as "GOAT", "blessing", fair and caring; all reviews positive | Relevant | Accurate |
| 3 | What are the main complaints students have about Sven Dietrich? | Pop quizzes, boring lectures, condescending attitude, harsh grading | Refuses questions, reads from PPT, condescending, slow grading, prerecorded videos | Relevant | Accurate |
| 4 | Does Melissa Lynch respond to student emails? | No — multiple reviews mention she doesn't reply | No — confirmed in all 5 retrieved chunks | Relevant | Accurate |
| 5 | Which CS professor at Hunter College is considered the easiest to get a good grade with? | Jaime Canizales — easy grading, multiple attempts on assignments | Canizales identified as easiest, but sources included 5 different professors | Relevant | Accurate |

Note: For #5, since the question only asked for singular professor, the LLM only output 1 professor which is the expected and correct behavior. Changing 'professor' to 'professors' will yield multiple professors in the output.

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** 
"Does Melissa Lynch respond to student emails?"

**What the system returned (before fix):** 
The retrieval stage returned 5 chunks, but chunk #3 was a review about **Katherine St. John**, not Melissa Lynch. The review happened to contain the word "email" and a similar complaint about unresponsiveness, so its embedding vector was nearly identical to Melissa Lynch's email-complaint reviews. The system had the wrong professor's review in the context window without any way to detect it.

**Root cause (tied to a specific pipeline stage):** 
This is an embedding-stage failure. Each chunk was originally embedded using only the review text itself, no professor identity was included in the vector. This means the embedding model treated all email-complaint reviews as semantically equivalent regardless of which professor they described. A Katherine St. John review saying "she never responds to emails" and a Melissa Lynch review saying the same thing produce nearly identical vectors, because the words and meaning are the same. ChromaDB cannot distinguish between them, both vectors point in the same direction in embedding space. The query "Does Melissa Lynch respond to emails?" matched on the *topic* (email unresponsiveness) rather than the *subject* (Melissa Lynch specifically).

**What was changed to fix it:** 
Before calling `model.encode()`, I prepend the professor's full name and source filename to each chunk's text — e.g., `"Professor Melissa Lynch (melissa-lynch.txt): She never replies to emails..."`. This encodes the professor's identity into the vector itself, so name-specific queries now score much higher against the correct professor's chunks. The original review text (without the prefix) is still what gets stored in ChromaDB's `documents` field and displayed to the user, the prefix only affects the embedding, not the output.

---

## Spec Reflection

**One way the spec helped you during implementation:** 
The Architecture section in `planning.md`, specifically the five-stage ASCII pipeline diagram was directly useful when prompting Claude to build `ingest.py` and `embed.py`. Having the tools labeled at each stage (e.g., `sentence-transformers` for embedding, `ChromaDB` for vector storage) meant the generated code used the exact libraries intended without needing follow-up corrections. The diagram also made it easy to verify that the generated code matched the spec: I could check each stage against the diagram and confirm the output format of one stage matched the expected input of the next.

**One way your implementation diverged from the spec, and why:** 
The spec described embedding each chunk's `text` field directly. During implementation, retrieval for name-specific queries (e.g., "Does Melissa Lynch respond to emails?") returned off-target results, a review about Katherine St. John appeared among Melissa Lynch results because the review text alone didn't strongly signal which professor it was about. To fix this, I prepended each professor's name and source filename to the text *before* embedding (e.g., `"Professor Melissa Lynch (melissa-lynch.txt): She never replies to emails..."`). This was not in the original spec but significantly improved name-specific retrieval accuracy.

---

## AI Usage

**Instance 1 — Building `ingest.py`**

- *What I gave the AI:* The Chunking Strategy section and Architecture diagram from `planning.md`, plus a sample cleaned `.txt` file from `documents/` showing the `[Review N]` format.
- *What it produced:* A complete `ingest.py` with `parse_header()`, `parse_meta_line()`, `parse_file()`, and `load_chunks()` functions that split each file on `[Review N]` boundaries and returned a list of chunk dictionaries with `text`, `professor`, `source`, `course`, `quality`, `difficulty`, `overall_rating`, `date`, and `grade` fields.
- *What I changed or overrode:* The initial version printed truncated text (cut off at 200 characters) in the sample output. I directed the AI to increase the display limit so full review text was visible for manual inspection during testing.

**Instance 2 — Fixing retrieval accuracy in `embed.py`**

- *What I gave the AI:* The instructions document's "Fix 1: Name-prepend" suggestion, the current `embed.py` code, and the specific failing query ("Does Melissa Lynch respond to student emails?") along with the incorrect result it was returning (a Katherine St. John review).
- *What it produced:* A modified `get_collection()` function that prepends `"Professor {name} ({source}): "` to each chunk's text before calling `model.encode()`, while keeping the original text in the `documents` field for display.
- *What I changed or overrode:* I verified the fix by deleting the old `chroma_db/` folder to force re-embedding and re-running all 3 evaluation queries. I confirmed all 5 results for the Melissa Lynch query were correctly scoped to her reviews before accepting the change.
