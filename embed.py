"""
embed.py

Embeds all professor review chunks into a ChromaDB vector store and
exposes a retrieve() function for semantic search.

From planning.md:
  Embedding model : all-MiniLM-L6-v2 (sentence-transformers, runs locally)
  Vector store    : ChromaDB (persisted to disk at ./chroma_db/)
  Top-k           : 5 chunks per query

On first run, all 609 chunks are embedded and stored.
On subsequent runs, the existing collection is reused (no re-embedding).

Usage:
    python embed.py          # embeds chunks and runs 3 test queries
    from embed import retrieve  # import in app.py
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_chunks

# ── Configuration ────────────────────────────────────────────────────────────
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME  = "hunter_cs_reviews"
CHROMA_DIR       = os.path.join(os.path.dirname(__file__), "chroma_db")
TOP_K            = 5

# ── Globals (loaded once, reused across calls) ────────────────────────────────
_model      = None
_collection = None


def get_model():
    """Load the embedding model once and cache it."""
    global _model
    if _model is None:
        print("Loading embedding model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def get_collection():
    """Return the ChromaDB collection, creating and populating it if needed."""
    global _collection
    if _collection is not None:
        return _collection

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Check if the collection already exists and has data
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        _collection = client.get_collection(COLLECTION_NAME)
        count = _collection.count()
        if count > 0:
            print(f"Loaded existing collection '{COLLECTION_NAME}' ({count} chunks).")
            return _collection
        else:
            # Collection exists but is empty — delete and rebuild
            client.delete_collection(COLLECTION_NAME)

    # Build the collection from scratch
    print("Building vector store — this runs once and takes ~30 seconds...")
    _collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity (lower = more similar)
    )

    model = get_model()
    chunks = load_chunks()

    # Embed in batches to avoid memory issues
    BATCH_SIZE = 64
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]

        # This improves retrieval for name-specific queries like "Does Lynch answer emails?" 
        # Significant improvement, went from 0.4-0.5 average distance to 0.3 average distance.
        texts_to_embed = [
            f"Professor {c['professor']} ({c['source']}): {c['text']}"
            for c in batch
        ]
        texts = [c["text"] for c in batch]  # store original text (without prefix) in ChromaDB
        embeddings = model.encode(texts_to_embed, show_progress_bar=False).tolist()

        _collection.add(
            ids=[f"chunk_{start + i}" for i in range(len(batch))],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {
                    "professor":      c["professor"],
                    "source":         c["source"],
                    "course":         c["course"],
                    "date":           c["date"],
                    "quality":        c["quality"],
                    "difficulty":     c["difficulty"],
                    "overall_rating": c["overall_rating"],
                }
                for c in batch
            ],
        )

        loaded = min(start + BATCH_SIZE, len(chunks))
        print(f"  Embedded {loaded}/{len(chunks)} chunks...", end="\r")

    print(f"\nDone. {len(chunks)} chunks stored in ChromaDB.")
    return _collection


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed a query and return the top-k most relevant chunks.

    Returns a list of dicts, each with:
        text       — the review text
        professor  — professor name
        source     — source filename
        course     — course code
        distance   — cosine distance (lower = more similar; < 0.5 is good)
    """
    model      = get_model()
    collection = get_collection()

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text":      doc,
                "professor": meta.get("professor", ""),
                "source":    meta.get("source", ""),
                "course":    meta.get("course", ""),
                "distance":  round(dist, 4),
            }
        )

    return chunks


def print_retrieval_test(query: str, results: list[dict]):
    """Pretty-print retrieval results for manual inspection."""
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    for i, r in enumerate(results, 1):
        dist_label = "[good]" if r["distance"] < 0.5 else "[weak]"
        print(f"\n  [{i}] {r['professor']} | {r['source']} | distance: {r['distance']} {dist_label}")
        print(f"      {r['text'][:250]}{'...' if len(r['text']) > 250 else ''}")


if __name__ == "__main__":
    # Initialize collection (embeds on first run, loads on subsequent runs)
    get_collection()

    # Test with 3 evaluation plan queries
    test_queries = [
        "What do students say about Saad Mneimneh's exam difficulty in CSCI150?",
        "What are the main complaints students have about Sven Dietrich?",
        "Does Melissa Lynch respond to student emails?",
    ]

    for query in test_queries:
        results = retrieve(query)
        print_retrieval_test(query, results)

    print("\n\nRetrieval test complete.")
    print("Check: are returned chunks relevant? Are distances below 0.5?")
