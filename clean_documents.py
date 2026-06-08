"""
clean_documents.py

Reads raw Rate My Professors copy-paste text files from documents/
and rewrites them into a clean, structured format suitable for RAG chunking.

Usage:
    python clean_documents.py

Output: overwrites each .txt file in documents/ with the cleaned version.
A backup of the original is saved as <filename>.raw.txt before overwriting.
"""

import os
import re

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")

# Lines that are pure UI/navigation boilerplate — always remove
SKIP_LINES = {
    "Logo", "Professors", "Caret Down", "Professor name", "Your school",
    "Log In", "Sign Up", "Help", "Rate", "Compare", "Arrow Icon",
    "/ 5", "Rating Distribution", "Similar Professors", "All courses",
    "Load More Ratings", "Site Guidelines", "Terms & Conditions",
    "Privacy Policy", "Copyright Compliance Policy",
    "CA Notice at Collection", "Do Not Sell My Personal Information",
    "Helpful", "Thumbs up", "Thumbs down", "Close Icon",
    "All Courses",
}

METADATA_PREFIXES = (
    "For Credit:", "Attendance:", "Would Take Again:", "Grade:", "Textbook:",
)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Known RMP professor tag labels — always strip these from review text
RMP_TAGS = {
    "Amazing lectures", "Accessible outside class", "Caring", "Respected",
    "Hilarious", "Inspirational", "Gives good feedback", "EXTRA CREDIT",
    "Extra credit", "Clear grading criteria", "Lots of homework",
    "Test heavy", "Graded by few things", "Get ready to read",
    "Lecture heavy", "Participation matters", "So many papers",
    "Tough grader", "Skip class? You won't pass.", "Group projects",
    "Would not take again", "Online class review", "Beware of pop quizzes",
    "Attendance mandatory", "No exams", "Amazing", "Brilliant",
    "Good feedback", "Would take again", "Accessible", "Respected",
}


def is_float(s):
    try:
        float(s.strip())
        return True
    except ValueError:
        return False


def is_date(s):
    return any(s.strip().startswith(m) for m in MONTHS)


def is_course_code(s):
    return bool(re.match(r'^[A-Z]{2,6}\d{3}[A-Z]?$', s.strip()))


def is_small_int(s):
    """Return True for bare single/double digit numbers (thumbs up/down counts)."""
    return bool(re.match(r'^\d{1,3}$', s.strip()))


def is_tag_line(s):
    """
    Return True if the line is an RMP tag label rather than real review text.
    First checks against the explicit known-tags list, then falls back to
    a heuristic for short all-title-case phrases with no sentence punctuation.
    """
    stripped = s.strip()
    if not stripped:
        return False

    # Explicit match against known RMP tags
    if stripped in RMP_TAGS:
        return True

    # Heuristic: short (<=5 words), no sentence-ending punctuation, no digit,
    # and every word starts with uppercase
    words = stripped.split()
    if len(words) > 5:
        return False
    if stripped[-1] in ".!?,":
        return False
    if any(c.isdigit() for c in stripped):
        return False
    if all(w[0].isupper() for w in words if w):
        return True
    return False


def extract_header_stats(lines):
    """Pull overall rating, would-take-again %, difficulty from the header block."""
    overall_rating = ""
    would_take_again = ""
    avg_difficulty = ""

    for i, line in enumerate(lines):
        stripped = line.strip()
        if "Overall Quality Based on" in stripped:
            # Rating is 2 lines before
            if i >= 2 and is_float(lines[i - 2]):
                overall_rating = lines[i - 2].strip()
            elif i >= 1 and is_float(lines[i - 1]):
                overall_rating = lines[i - 1].strip()

        if stripped == "Would take again" and i > 0:
            pct = lines[i - 1].strip()
            if pct.endswith("%"):
                would_take_again = pct

        if stripped == "Level of Difficulty" and i > 0:
            diff = lines[i - 1].strip()
            if is_float(diff):
                avg_difficulty = diff

    return overall_rating, would_take_again, avg_difficulty


def extract_prof_info(lines):
    """Extract professor name, department, college from header."""
    prof_name = ""
    department = ""
    college = ""

    for line in lines:
        m = re.match(r"Professor in the (.+) department at (.+)", line.strip())
        if m:
            department = m.group(1).strip()
            college = m.group(2).strip()
            break

    # Professor name appears just before department on its own line
    # Find the "Computer Science" (or department) line and take the line above it
    for i, line in enumerate(lines):
        if line.strip() == department and i > 0:
            candidate = lines[i - 1].strip()
            # Sanity check: looks like a name (2+ words, no digits, not boilerplate)
            if (candidate and " " in candidate and
                    not any(c.isdigit() for c in candidate) and
                    candidate not in SKIP_LINES and
                    not candidate.startswith("http")):
                prof_name = candidate
                break

    return prof_name, department, college


def parse_reviews(lines, reviews_start_idx):
    """Parse review blocks starting from reviews_start_idx."""
    reviews = []
    i = reviews_start_idx

    while i < len(lines):
        stripped = lines[i].strip()

        # Detect start of a review: "Quality" followed by a float
        if (stripped == "Quality" and
                i + 1 < len(lines) and is_float(lines[i + 1])):

            quality = lines[i + 1].strip()
            i += 2

            # Difficulty
            difficulty = ""
            if (i < len(lines) and lines[i].strip() == "Difficulty" and
                    i + 1 < len(lines) and is_float(lines[i + 1])):
                difficulty = lines[i + 1].strip()
                i += 2

            # Course code
            course = ""
            if i < len(lines) and is_course_code(lines[i].strip()):
                course = lines[i].strip()
                i += 1

            # Date
            date = ""
            if i < len(lines) and is_date(lines[i].strip()):
                date = lines[i].strip()
                i += 1

            # Metadata lines
            metadata = {}
            while i < len(lines) and any(
                    lines[i].strip().startswith(p) for p in METADATA_PREFIXES):
                meta = lines[i].strip()
                for p in METADATA_PREFIXES:
                    if meta.startswith(p):
                        metadata[p.rstrip(":")] = meta[len(p):].strip()
                        break
                i += 1

            # Collect content lines until "Helpful" or end of block
            content_lines = []
            while i < len(lines):
                cur = lines[i].strip()

                if cur == "Helpful":
                    # Skip Helpful + Thumbs up/down + counts
                    i += 1
                    while i < len(lines) and (
                        lines[i].strip() in ("Thumbs up", "Thumbs down") or
                        is_small_int(lines[i].strip())
                    ):
                        i += 1
                    break

                if not cur:
                    i += 1
                    continue

                if cur in SKIP_LINES:
                    i += 1
                    continue

                if cur.startswith("Reviewed:"):
                    i += 1
                    continue

                if cur.startswith("©") or cur.startswith("Load More"):
                    i += 1
                    continue

                # Strip RMP icon artifact that appears on some copy-pasted reviews
                cur = cur.replace("Computer Icon", "").strip()
                if cur:
                    content_lines.append(cur)
                i += 1

            # Separate real review text from tag labels
            review_text_parts = []
            for cl in content_lines:
                if not is_tag_line(cl):
                    review_text_parts.append(cl)

            review_text = " ".join(review_text_parts).strip()

            if review_text:
                reviews.append({
                    "quality": quality,
                    "difficulty": difficulty,
                    "course": course,
                    "date": date,
                    "metadata": metadata,
                    "text": review_text,
                })
        else:
            i += 1

    return reviews


def find_reviews_start(lines):
    """Return the index of the first line after 'All courses'."""
    for i, line in enumerate(lines):
        if line.strip() in ("All courses", "All Courses"):
            return i + 1
    # Fallback: start after rating distribution section
    for i, line in enumerate(lines):
        if "Student Ratings" in line:
            return i + 1
    return 0


def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip("\n") for line in f.readlines()]

    url = raw_lines[0].strip() if raw_lines and raw_lines[0].startswith("http") else ""

    overall_rating, would_take_again, avg_difficulty = extract_header_stats(raw_lines)
    prof_name, department, college = extract_prof_info(raw_lines)

    reviews_start = find_reviews_start(raw_lines)
    reviews = parse_reviews(raw_lines, reviews_start)

    # Build clean output
    out = []
    out.append(f"Professor: {prof_name}")
    out.append(f"Department: {department}")
    out.append(f"College: {college}")
    if overall_rating:
        out.append(f"Overall Rating: {overall_rating}/5")
    if would_take_again:
        out.append(f"Would Take Again: {would_take_again}")
    if avg_difficulty:
        out.append(f"Average Difficulty: {avg_difficulty}/5")
    if url:
        out.append(f"Source: {url}")
    out.append("")
    out.append("=" * 60)
    out.append("")

    for idx, review in enumerate(reviews, 1):
        out.append(f"[Review {idx}]")

        meta_parts = []
        if review["course"]:
            meta_parts.append(f"Course: {review['course']}")
        if review["date"]:
            meta_parts.append(f"Date: {review['date']}")
        if review["quality"]:
            meta_parts.append(f"Quality: {review['quality']}/5")
        if review["difficulty"]:
            meta_parts.append(f"Difficulty: {review['difficulty']}/5")
        if "Grade" in review["metadata"]:
            meta_parts.append(f"Grade: {review['metadata']['Grade']}")

        if meta_parts:
            out.append(" | ".join(meta_parts))

        out.append(review["text"])
        out.append("")

    return "\n".join(out), prof_name, len(reviews)


def main():
    txt_files = [f for f in os.listdir(DOCS_DIR)
                 if f.endswith(".txt") and not f.endswith(".raw.txt") and f != ".gitkeep"]

    print(f"Found {len(txt_files)} document(s) to clean.\n")

    for filename in sorted(txt_files):
        filepath = os.path.join(DOCS_DIR, filename)
        backup_path = filepath.replace(".txt", ".raw.txt")

        # On first run: back up the raw file. On subsequent runs: read from backup.
        if not os.path.exists(backup_path):
            with open(filepath, "r", encoding="utf-8") as f:
                raw = f.read()
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(raw)
            source_path = filepath
        else:
            # Always clean from the original raw backup, not a previous cleaned version
            source_path = backup_path

        cleaned, prof_name, review_count = clean_file(source_path)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"  {filename}: {prof_name} — {review_count} reviews extracted")

    print("\nDone. Originals preserved as .raw.txt")


if __name__ == "__main__":
    main()
