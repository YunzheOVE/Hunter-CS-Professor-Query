"""
ingest.py

Reads all cleaned professor review files from documents/ and splits them
into individual review chunks. Each chunk is one student review with
associated metadata.

Chunking strategy (from planning.md):
  - Structure-based: one review per chunk
  - Boundary: [Review N] markers in each file
  - No overlap: each review is already a self-contained unit
  - Expected output: ~608 chunks across 13 professors

Each chunk is a dict with:
  text         — the student review text
  professor    — professor full name
  source       — filename (e.g. melissa-lynch.txt)
  overall_rating — professor's overall RMP rating
  course       — course code from the review metadata (may be empty)
  quality      — quality score from the review (may be empty)
  difficulty   — difficulty score from the review (may be empty)
  date         — date the review was posted (may be empty)

Usage:
    python ingest.py               # prints 5 sample chunks + total count
    from ingest import load_chunks # import in other scripts
"""

import os
import re
import random

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")


def parse_header(lines):
    """
    Extract professor-level metadata from the top of a cleaned .txt file.
    Returns a dict with professor, overall_rating, would_take_again, avg_difficulty.
    """
    meta = {
        "professor": "",
        "overall_rating": "",
        "would_take_again": "",
        "avg_difficulty": "",
    }
    for line in lines:
        line = line.strip()
        if line.startswith("Professor:"):
            meta["professor"] = line[len("Professor:"):].strip()
        elif line.startswith("Overall Rating:"):
            meta["overall_rating"] = line[len("Overall Rating:"):].strip()
        elif line.startswith("Would Take Again:"):
            meta["would_take_again"] = line[len("Would Take Again:"):].strip()
        elif line.startswith("Average Difficulty:"):
            meta["avg_difficulty"] = line[len("Average Difficulty:"):].strip()
        elif line.startswith("=" * 10):
            break  # end of header
    return meta


def parse_meta_line(line):
    """
    Parse a pipe-separated review metadata line like:
    'Course: CSCI160 | Date: May 29th, 2026 | Quality: 1.0/5 | Difficulty: 3.0/5 | Grade: B'
    Returns a dict with course, date, quality, difficulty, grade.
    """
    result = {"course": "", "date": "", "quality": "", "difficulty": "", "grade": ""}
    parts = [p.strip() for p in line.split("|")]
    for part in parts:
        if part.startswith("Course:"):
            result["course"] = part[len("Course:"):].strip()
        elif part.startswith("Date:"):
            result["date"] = part[len("Date:"):].strip()
        elif part.startswith("Quality:"):
            result["quality"] = part[len("Quality:"):].strip().replace("/5", "")
        elif part.startswith("Difficulty:"):
            result["difficulty"] = part[len("Difficulty:"):].strip().replace("/5", "")
        elif part.startswith("Grade:"):
            result["grade"] = part[len("Grade:"):].strip()
    return result


def parse_file(filepath):
    """
    Parse one cleaned professor .txt file into a list of chunk dicts.
    """
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()

    # Extract header metadata (professor name, overall rating, etc.)
    header = parse_header(lines)

    # Split the content on [Review N] markers
    # re.split keeps the delimiter groups so we can pair markers with content
    review_pattern = re.compile(r"^\[Review \d+\]$", re.MULTILINE)
    parts = review_pattern.split(content)

    # parts[0] is the header section; parts[1:] are the review blocks
    review_blocks = parts[1:]

    chunks = []
    for block in review_blocks:
        block_lines = [l for l in block.strip().splitlines() if l.strip()]

        if not block_lines:
            continue

        # First line of the block is the metadata line (Course | Date | Quality...)
        first_line = block_lines[0]
        review_meta = parse_meta_line(first_line)

        # Remaining lines are the review text
        text_lines = block_lines[1:]
        text = " ".join(text_lines).strip()

        # Skip empty or trivially short reviews
        if len(text) < 5:
            continue

        chunk = {
            "text": text,
            "professor": header["professor"],
            "source": filename,
            "overall_rating": header["overall_rating"],
            "would_take_again": header["would_take_again"],
            "avg_difficulty": header["avg_difficulty"],
            "course": review_meta["course"],
            "date": review_meta["date"],
            "quality": review_meta["quality"],
            "difficulty": review_meta["difficulty"],
            "grade": review_meta["grade"],
        }
        chunks.append(chunk)

    return chunks


def load_chunks():
    """
    Load and return all chunks from every professor file in documents/.
    This is the main function imported by embed.py.
    """
    all_chunks = []

    txt_files = [
        f for f in os.listdir(DOCS_DIR)
        if f.endswith(".txt")
        and not f.endswith(".raw.txt")
        and f != ".gitkeep"
    ]

    for filename in sorted(txt_files):
        filepath = os.path.join(DOCS_DIR, filename)
        chunks = parse_file(filepath)
        all_chunks.extend(chunks)

    return all_chunks


def print_sample_chunks(chunks, n=5):
    """Print n random chunks for manual inspection."""
    print(f"\n{'='*60}")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(f"{'='*60}")

    sample = random.sample(chunks, min(n, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Sample Chunk {i} ---")
        print(f"Professor : {chunk['professor']}")
        print(f"Source    : {chunk['source']}")
        print(f"Course    : {chunk['course'] or '(not listed)'}")
        print(f"Date      : {chunk['date'] or '(not listed)'}")
        print(f"Quality   : {chunk['quality'] or '(not listed)'}/5")
        print(f"Difficulty: {chunk['difficulty'] or '(not listed)'}/5")
        print(f"Grade     : {chunk['grade'] or '(not listed)'}")
        print(f"Text      : {chunk['text'][:300]}{'...' if len(chunk['text']) > 300 else ''}")


def print_stats(chunks):
    """Print a per-professor breakdown of chunk counts."""
    print(f"\n{'='*60}")
    print("CHUNKS PER PROFESSOR")
    print(f"{'='*60}")
    from collections import Counter
    counts = Counter(c["professor"] for c in chunks)
    for prof, count in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {prof}: {count} chunks")


if __name__ == "__main__":
    chunks = load_chunks()
    print_stats(chunks)
    print_sample_chunks(chunks, n=5)
