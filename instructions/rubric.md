Project 1: The Unofficial Guide
Total Points: 25pts + 5pts bonus

Required Features
3pts	Document Pipeline — Ingestion and Chunking
1	README names the domain and identifies at least 10 documents with specific sources (URLs, subreddit names, or file descriptions).
1	Chunking strategy is explained with specific reasoning — chunk size, overlap, and why those numbers fit the structure of the documents.
1	README includes at least 5 labeled sample chunks with their source document name.
4pts	Retrieval — Relevant Chunks Returned for Queries
1	README includes at least 3 retrieval test examples, each showing the query and the top returned chunks.
1	For at least 2 of those examples, the student provides a written explanation of why the returned chunks are relevant to the query.
1	README names the embedding model used.
1	README includes a tradeoff reflection — what factors the student would weigh when choosing a model for a production deployment (e.g., cost, context length, multilingual support, local vs. API latency).
3pts	Grounded Generation with Source Attribution
1	README includes at least 2 example system responses with source attribution visible in the output text.
1	README includes one out-of-scope query example with the system's refusal response shown.
1	README explains how grounding is enforced in the prompt or pipeline.
4pts	Evaluation Report
1	All 5 test questions are documented, each with the question, the expected correct answer, and the system's actual response.
1	An accuracy judgment is given for each question (accurate / partially accurate / inaccurate).
2	At least one failure case is identified with a specific cause tied to a part of the pipeline — not just "it got it wrong," but why (e.g., "the relevant sentence was split across a chunk boundary").
2pts	Query Interface
2	README describes the interface's input and output fields and includes a sample interaction transcript showing a complete query and response.
4pts	planning.md Completeness
1	Domain — names the domain and explains why this knowledge is valuable or hard to find through official channels.
1	Documents — lists specific sources with enough detail to locate them; Chunking Strategy — states chunk size, overlap, and explains fit for the document type; Retrieval Approach — names the embedding model, states top-k value, and includes a tradeoff reflection on production model selection. All three sub-sections must be present and substantive.
1	Evaluation Plan — lists all 5 test questions with specific, verifiable expected answers (not open-ended).
1	Anticipated Challenges — names at least 2 specific risks with reasoning; AI Tool Plan — names at least one pipeline component the student planned to use AI to implement.
3pts	README Completeness
1	Domain and document sources; chunking strategy with reasoning; embedding model with tradeoff reflection; how grounded generation is enforced.
1	Full evaluation report (all 5 questions with expected answers, system responses, and accuracy judgments).
1	At least one honest failure case with a specific cause; spec reflection (one way the spec helped, one divergence and why).
2pts	AI Usage Transparency
1	Section describes at least 2 specific instances of AI tool use, naming what the student directed the AI to do in each case.
1	Each instance describes what the student reviewed, revised, or overrode. The section reads as genuine collaboration — the student was directing, not just accepting output.
Stretch Features
+2pts	Hybrid Search
README describes the hybrid approach (how BM25 and semantic scores are combined) and reports a comparison on at least 3 queries — what each method returned and which performed better.
Demo or source shows hybrid search in operation.
+1pt	Chunking Strategy Comparison
README reports comparison results across 2+ chunking strategies on the same query set. Analysis states which strategy performed better and explains why, with reference to specific query results.
+1pt	Metadata Filtering
Demo or source shows a query being filtered by at least one metadata field (source, date, or rating) with a visible effect on which results are returned.
+1pt	Conversational Memory
Demo or source shows a multi-turn exchange where the second query references context from the first, and the response reflects that memory — not just a coincidence of topic overlap.