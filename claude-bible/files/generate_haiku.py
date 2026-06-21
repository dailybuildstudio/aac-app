"""
Selah Bible Verse Write-Up Generator
=====================================
Generates rich, pastoral study write-ups for every verse of the Bible
using the Claude API. Outputs are saved as JSON files organized by book.

Usage:
    python generate.py --book John          # Generate one book
    python generate.py --all               # Generate entire Bible
    python generate.py --book John --start 3 --end 5  # Specific chapters

Requirements:
    pip install anthropic requests tqdm
"""

import anthropic
import json
import os
import time
import argparse
import sys
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 1500
OUTPUT_DIR = Path("output")
MAX_WORKERS = 10          # Parallel API calls (keep ≤ 5 to respect rate limits)
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5          # seconds between retries

# ── Bible Data ─────────────────────────────────────────────────────────────────
# Using the World English Bible (WEB) — public domain, no license needed.
# Data fetched from a public API. For offline use, see load_local_bible().

BIBLE_API_URL = "https://bible-api.com/{reference}?translation=web"

BOOK_GENRES = {
    "Genesis": "narrative", "Exodus": "narrative", "Leviticus": "law",
    "Numbers": "narrative", "Deuteronomy": "law", "Joshua": "narrative",
    "Judges": "narrative", "Ruth": "narrative", "1 Samuel": "narrative",
    "2 Samuel": "narrative", "1 Kings": "narrative", "2 Kings": "narrative",
    "1 Chronicles": "narrative", "2 Chronicles": "narrative", "Ezra": "narrative",
    "Nehemiah": "narrative", "Esther": "narrative", "Job": "wisdom",
    "Psalms": "poetry", "Proverbs": "wisdom", "Ecclesiastes": "wisdom",
    "Song of Solomon": "poetry", "Isaiah": "prophecy", "Jeremiah": "prophecy",
    "Lamentations": "poetry", "Ezekiel": "prophecy", "Daniel": "prophecy",
    "Hosea": "prophecy", "Joel": "prophecy", "Amos": "prophecy",
    "Obadiah": "prophecy", "Jonah": "narrative", "Micah": "prophecy",
    "Nahum": "prophecy", "Habakkuk": "prophecy", "Zephaniah": "prophecy",
    "Haggai": "prophecy", "Zechariah": "prophecy", "Malachi": "prophecy",
    "Matthew": "gospel", "Mark": "gospel", "Luke": "gospel", "John": "gospel",
    "Acts": "narrative", "Romans": "epistle", "1 Corinthians": "epistle",
    "2 Corinthians": "epistle", "Galatians": "epistle", "Ephesians": "epistle",
    "Philippians": "epistle", "Colossians": "epistle", "1 Thessalonians": "epistle",
    "2 Thessalonians": "epistle", "1 Timothy": "epistle", "2 Timothy": "epistle",
    "Titus": "epistle", "Philemon": "epistle", "Hebrews": "epistle",
    "James": "epistle", "1 Peter": "epistle", "2 Peter": "epistle",
    "1 John": "epistle", "2 John": "epistle", "3 John": "epistle",
    "Jude": "epistle", "Revelation": "apocalyptic",
}

VERSE_COUNTS = {
    "Genesis": [31,25,24,26,32,22,24,22,29,32,32,20,18,24,21,16,27,33,38,18,34,24,20,67,34,35,46,22,35,43,55,32,20,31,29,43,36,30,23,23,57,38,34,34,28,34,31,22,33,26],
    "Exodus": [22,25,22,31,23,30,25,32,35,29,10,51,22,31,27,36,16,27,25,26,36,31,33,18,40,37,21,43,46,38,18,35,23,35,35,38,29,31,43,38],
    "Leviticus": [17,16,17,35,19,30,38,36,24,20,47,8,59,57,33,34,16,30,24,16,30,32,24,20,14,16,13,19,14,19,34,20,24,12,12,14,12,14,17,22,18,16,22,22],
    "Numbers": [54,34,51,49,31,27,89,26,23,36,35,16,33,45,41,50,13,32,22,29,35,41,30,25,18,65,23,31,40,16,54,42,56,29,34,13],
    "Deuteronomy": [46,37,29,49,33,25,26,20,29,22,32,32,18,29,23,22,20,22,21,20,23,30,25,22,19,19,26,68,29,20,30,52,29,12],
    "Joshua": [18,24,17,24,15,27,26,35,27,43,23,24,33,15,63,10,18,28,51,9,45,34,16,33],
    "Judges": [36,23,31,24,31,40,25,35,57,18,40,15,25,20,20,31,13,31,30,48,25],
    "Ruth": [22,23,18,22],
    "1 Samuel": [28,36,21,22,12,21,17,22,27,27,15,25,23,52,35,23,58,30,24,42,15,23,29,22,44,25,12,25,11,31,13],
    "2 Samuel": [27,32,39,12,25,23,29,18,13,19,27,31,39,33,37,23,29,33,43,26,22,51,39,25],
    "1 Kings": [53,46,28,34,18,38,51,66,28,29,43,33,34,31,34,34,24,46,21,43,29,53],
    "2 Kings": [18,25,27,44,27,33,20,29,37,36,21,21,25,29,38,20,41,37,37,21,26,20,37,20,30],
    "1 Chronicles": [54,55,24,43,26,81,40,40,44,14,47,40,14,17,29,43,27,17,19,8,30,19,32,31,31,32,34,21,30],
    "2 Chronicles": [17,18,17,22,14,42,22,18,31,19,23,16,22,15,19,14,19,34,11,37,20,12,21,27,28,23,9,27,36,27,21,33,25,33,27,23],
    "Ezra": [11,70,13,24,17,22,28,36,15,44],
    "Nehemiah": [11,20,32,23,19,19,73,18,38,39,36,47,31],
    "Esther": [22,23,15,17,14,14,10,17,32,3],
    "Job": [22,13,26,21,27,30,21,22,35,22,20,25,28,22,35,22,16,21,29,29,34,30,17,25,6,14,23,28,25,31,40,22,33,37,16,33,24,41,30,24,34,17],
    "Psalms": [6,12,8,8,12,10,17,9,20,18,7,8,6,7,5,11,15,50,14,9,13,31,6,10,22,12,14,9,11,12,24,11,22,22,28,12,40,22,13,17,13,11,5,20,28,14,9,35,30,10,15,11],
    "Proverbs": [33,22,35,27,23,35,27,36,18,32,31,28,25,35,33,33,28,24,29,30,31,29,35,34,28,28,27,28,27,33,31],
    "Ecclesiastes": [18,26,22,16,20,12,29,17,18,20,10,14],
    "Song of Solomon": [17,17,11,16,16,13,13,14],
    "Isaiah": [31,22,26,6,30,13,25,22,21,34,16,6,22,32,9,14,14,7,25,6,17,25,18,23,12,21,13,29,24,33,9,20,24,17,10,22,38,22,8,31,29,25,28,28,25,13,15,22,26,11,23,15,12,17,13,12,21,14,21,22,11,12,19,12,25,24],
    "Jeremiah": [19,37,25,31,31,30,34,22,26,25,23,17,27,22,21,21,27,23,15,18,14,30,40,10,38,24,22,17,32,24,40,44,26,22,19,32,21,28,18,16,18,22,13,30,5,28,7,47,39,46,64,34],
    "Lamentations": [22,22,66,22,22],
    "Ezekiel": [28,10,27,21,17,21,11,20,12,28,33,18,24,20,28,22,28,22,31,22,31,21,26,16,30,11,33,13,13,22,44,28,13,17,6,9,21,14,18,24,21,26,21,22,26,18,32,33,39,15],
    "Daniel": [21,49,30,37,31,28,28,27,27,21,45,13],
    "Hosea": [11,23,5,19,15,11,16,14,17,15,12,14,16,9],
    "Joel": [20,32,21],
    "Amos": [15,16,15,13,27,14,17,14,15],
    "Obadiah": [21],
    "Jonah": [17,10,10,11],
    "Micah": [16,13,12,13,15,16,20],
    "Nahum": [15,13,19],
    "Habakkuk": [17,20,19],
    "Zephaniah": [18,15,20],
    "Haggai": [15,23],
    "Zechariah": [21,13,10,14,11,15,14,23,17,12,17,14,9,21],
    "Malachi": [14,17,18,6],
    "Matthew": [25,23,17,25,48,34,29,34,38,42,30,50,58,36,39,28,27,35,30,34,46,46,39,51,46,75,66,20],
    "Mark": [45,28,35,41,43,56,37,38,50,52,33,44,37,72,47,20],
    "Luke": [80,52,38,44,39,49,50,56,62,42,54,59,35,35,32,31,37,43,48,47,38,71,56,53],
    "John": [51,25,36,54,47,71,53,59,41,42,57,50,38,31,27,33,26,40,42,31,25],
    "Acts": [26,47,26,37,42,15,60,40,43,48,30,25,52,28,41,40,34,28,41,38,40,30,35,27,27,32,44,31],
    "Romans": [32,29,31,25,21,23,25,39,33,21,36,21,14,26,33,24],
    "1 Corinthians": [31,16,23,21,13,20,40,13,27,33,34,31,13,40,58,24],
    "2 Corinthians": [24,17,18,18,21,18,16,24,15,18,33,21,13],
    "Galatians": [24,21,29,31,26,18],
    "Ephesians": [23,22,21,28,22,25],
    "Philippians": [30,18,31,21],
    "Colossians": [29,23,25,18],
    "1 Thessalonians": [10,20,13,18,28],
    "2 Thessalonians": [12,17,18],
    "1 Timothy": [20,15,16,16,25,21],
    "2 Timothy": [18,26,17,22],
    "Titus": [16,15,15],
    "Philemon": [25],
    "Hebrews": [14,18,19,16,14,20,28,13,28,39,40,29,25],
    "James": [27,26,18,17,20],
    "1 Peter": [25,25,22,19,14],
    "2 Peter": [21,22,18],
    "1 John": [10,29,24,21,21],
    "2 John": [13],
    "3 John": [14],
    "Jude": [25],
    "Revelation": [20,29,22,11,14,17,17,13,21,11,19,17,18,20,8,21,18,24,21,15,27,21],
}

# ── Prompt Templates by Genre ──────────────────────────────────────────────────

GENRE_INSTRUCTIONS = {
    "gospel": "Focus on what Jesus is revealing about himself and the Kingdom of God. Note the narrative context — who is present, what just happened, what happens next.",
    "epistle": "Identify the specific problem or question the author is addressing. Explain the theological argument being made and how this verse fits into it.",
    "poetry": "Pay attention to the poetic structure — parallelism, imagery, metaphor. Let the emotion and beauty of the language come through.",
    "prophecy": "Ground the prophecy in its historical context first, then explain its fulfillment and ongoing significance. Avoid speculation.",
    "narrative": "Tell the story. Who are the people involved? What is at stake? What does this moment reveal about God's character?",
    "law": "Explain the purpose and context of this law in ancient Israel, then show how it points forward to Christ and informs Christian ethics today.",
    "wisdom": "Draw out the practical wisdom and show how it reflects the character of God. Connect it to lived human experience.",
    "apocalyptic": "Interpret the symbolic imagery carefully. Ground the meaning in the original audience's situation while showing its timeless hope.",
}

SYSTEM_PROMPT = """You are a Bible teacher and writer for Selah, a spiritual formation app. 
Your write-ups help everyday people — not seminary students — encounter Scripture in a way 
that is both intellectually honest and spiritually alive.

Your writing is:
- Warm and pastoral, not academic or preachy
- Grounded in the original language (Greek or Hebrew) when it matters
- Rooted in historical and literary context
- Practically applicable to daily life
- Pointing toward Jesus and the larger story of Scripture

You never moralize or oversimplify. You trust the reader with complexity.
You write in plain, clear English — no jargon without explanation."""

def build_prompt(book, chapter, verse, text, genre):
    genre_instruction = GENRE_INSTRUCTIONS.get(genre, "")
    context_note = f"Genre note: This is {genre} literature. {genre_instruction}"

    return f"""Write a rich study explanation for this Bible verse for the Selah app.

Verse: {book} {chapter}:{verse}
Text: "{text}"
{context_note}

Structure your response as JSON with these exact fields:
{{
  "headline": "A single compelling sentence capturing the heart of this verse (max 12 words)",
  "word_study": "The most important word in this verse — its original Greek or Hebrew, transliteration, and what it actually means beyond the English translation (2-3 sentences)",
  "context": "What is happening in the surrounding passage? Who is speaking, to whom, and why does it matter for understanding this verse? (2-3 sentences)",
  "meaning": "The core meaning of this verse — what the original audience would have understood, what it reveals about God, humanity, or salvation (3-4 sentences)",
  "application": "How does this truth practically change how someone thinks, prays, or lives today? Be specific, not generic. (2-3 sentences)",
  "connection": "One other verse or passage in Scripture that illuminates this verse — briefly explain the connection (1-2 sentences)",
  "prayer_prompt": "A single sentence prayer prompt that flows naturally from this verse"
}}

Return ONLY valid JSON. No markdown, no preamble, no explanation outside the JSON."""


# ── Core Functions ─────────────────────────────────────────────────────────────

def fetch_verse_text(book, chapter, verse):
    """Fetch verse text from local Bible file (offline mode)."""
    from offline_bible import get_verse
    text = get_verse(book, chapter, verse)
    if not text:
        print(f"  Warning: Could not find {book} {chapter}:{verse} in local Bible")
    return text


def _repair_json(raw):
    """
    Attempt to fix common JSON issues from LLM output:
    - Trailing commas before closing brace
    - Smart quotes replaced with straight quotes
    - Unescaped newlines inside string values
    """
    import re
    # Replace smart/curly quotes with straight quotes
    raw = raw.replace("\u201c", '"').replace("\u201d", '"')
    raw = raw.replace("\u2018", "'").replace("\u2019", "'")
    # Remove trailing commas before } or ]
    raw = re.sub(r',\s*([}\]])', r'\1', raw)
    # Replace literal newlines inside JSON strings with \n
    # (only between quotes — crude but effective for common cases)
    raw = re.sub(r'(?<=": ")(.*?)(?="[,\n}])', lambda m: m.group(0).replace('\n', '\\n'), raw, flags=re.DOTALL)
    return raw


def generate_writeup(client, book, chapter, verse, text, genre, lock):
    """Call Claude API and return parsed write-up dict."""
    prompt = build_prompt(book, chapter, verse, text, genre)

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            # Strip markdown code fences if present
            if "```" in raw:
                import re
                match = re.search(r'''```(?:json)?\s*(\{.*?\})\s*```''', raw, re.DOTALL)
                if match:
                    raw = match.group(1).strip()
            # Extract just the JSON object if there is surrounding text
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                raw = raw[start:end]
            # Repair common JSON issues
            raw = _repair_json(raw)
            data = json.loads(raw)
            data["reference"] = f"{book} {chapter}:{verse}"
            data["book"] = book
            data["chapter"] = chapter
            data["verse"] = verse
            data["text"] = text
            data["genre"] = genre
            return data

        except json.JSONDecodeError as e:
            with lock:
                print(f"\n  JSON parse error for {book} {chapter}:{verse} (attempt {attempt+1}): {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
        except anthropic.RateLimitError:
            with lock:
                print(f"\n  Rate limited — waiting 30s before retry...")
            time.sleep(30)
        except anthropic.APIError as e:
            with lock:
                print(f"\n  API error for {book} {chapter}:{verse}: {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)

    return None


def get_output_path(book):
    """Return the output file path for a given book."""
    safe_name = book.replace(" ", "_").lower()
    return OUTPUT_DIR / f"{safe_name}.json"


def load_existing(book):
    """Load already-generated verses to allow resuming."""
    path = get_output_path(book)
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        return {(d["chapter"], d["verse"]): d for d in data}
    return {}


def save_book(book, verses_dict):
    """Save all verses for a book to JSON."""
    path = get_output_path(book)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sorted_verses = sorted(verses_dict.values(), key=lambda v: (v["chapter"], v["verse"]))
    with open(path, "w") as f:
        json.dump(sorted_verses, f, indent=2, ensure_ascii=False)


def process_book(client, book, start_chapter=1, end_chapter=None):
    """Generate write-ups for all verses in a book."""
    chapters = VERSE_COUNTS.get(book)
    if not chapters:
        print(f"Unknown book: {book}")
        return

    genre = BOOK_GENRES.get(book, "narrative")
    existing = load_existing(book)
    save_lock = threading.Lock()
    print_lock = threading.Lock()

    if end_chapter is None:
        end_chapter = len(chapters)

    # Build list of all verses to process
    todos = []
    for ch_idx in range(start_chapter - 1, end_chapter):
        ch_num = ch_idx + 1
        num_verses = chapters[ch_idx]
        for v_num in range(1, num_verses + 1):
            if (ch_num, v_num) not in existing:
                todos.append((ch_num, v_num))

    if not todos:
        print(f"  {book}: all verses already generated, skipping.")
        return

    print(f"\n{'='*60}")
    print(f"  {book} ({genre}) — {len(todos)} verses to generate")
    print(f"{'='*60}")

    verses_dict = dict(existing)
    completed = 0
    failed = 0

    def process_one(ch_num, v_num):
        text = fetch_verse_text(book, ch_num, v_num)
        if not text:
            return None, ch_num, v_num
        result = generate_writeup(client, book, ch_num, v_num, text, genre, print_lock)
        return result, ch_num, v_num

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_one, ch, v): (ch, v) for ch, v in todos}

        with tqdm(total=len(todos), desc=book, unit="verse") as pbar:
            for future in as_completed(futures):
                result, ch_num, v_num = future.result()
                if result:
                    with save_lock:
                        verses_dict[(ch_num, v_num)] = result
                        completed += 1
                        # Save after every 10 completions
                        if completed % 10 == 0:
                            save_book(book, verses_dict)
                else:
                    failed += 1
                pbar.update(1)

    # Final save
    save_book(book, verses_dict)
    print(f"\n  Done: {completed} generated, {failed} failed → {get_output_path(book)}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate Selah Bible verse write-ups using Claude API"
    )
    parser.add_argument("--book", help="Book name (e.g. 'John', '1 Corinthians')")
    parser.add_argument("--all", action="store_true", help="Process entire Bible")
    parser.add_argument("--start", type=int, default=1, help="Start chapter (with --book)")
    parser.add_argument("--end", type=int, default=None, help="End chapter (with --book)")
    parser.add_argument("--list-books", action="store_true", help="List all available books")
    args = parser.parse_args()

    if args.list_books:
        print("\nAvailable books:")
        for i, book in enumerate(VERSE_COUNTS.keys(), 1):
            print(f"  {i:3}. {book}")
        return

    if not API_KEY or API_KEY == "your-api-key-here":
        print("\nError: Set your API key via environment variable:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=API_KEY)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.all:
        books = list(VERSE_COUNTS.keys())
        print(f"\nGenerating write-ups for entire Bible ({len(books)} books)...")
        for book in books:
            process_book(client, book)

    elif args.book:
        # Find book with case-insensitive match
        match = next((b for b in VERSE_COUNTS if b.lower() == args.book.lower()), None)
        if not match:
            print(f"Book '{args.book}' not found. Run --list-books to see all options.")
            sys.exit(1)
        process_book(client, match, start_chapter=args.start, end_chapter=args.end)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
