"""
Selah Feelings Tag Generator
==============================
Reads your existing verse write-up JSON files and adds emotional
tags to every verse — what feelings it addresses and how it helps.

Run AFTER generate.py has finished producing output/*.json files.

Usage:
    python3 generate_feelings.py --book John
    python3 generate_feelings.py --all
"""

import anthropic
import json
import os
import time
import argparse
import sys
import threading
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 800
INPUT_DIR = Path("output")
OUTPUT_DIR = Path("output_feelings")
MAX_WORKERS = 5
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# ── Master Feelings Taxonomy ───────────────────────────────────────────────────

EMOTIONS = [
    "anxiety", "fear", "worry", "grief", "loss", "loneliness", "isolation",
    "shame", "guilt", "regret", "anger", "bitterness", "unforgiveness",
    "doubt", "confusion", "uncertainty", "hopelessness", "despair", "depression",
    "exhaustion", "burnout", "overwhelm", "inadequacy", "failure", "rejection",
    "jealousy", "envy", "pride", "temptation", "addiction", "lust",
    "joy", "gratitude", "peace", "hope", "love", "trust", "faith",
    "contentment", "courage", "strength", "comfort", "healing", "restoration"
]

SITUATIONS = [
    "waiting on God", "unanswered prayer", "suffering", "illness", "death",
    "marriage", "divorce", "parenting", "prodigal child", "infertility",
    "financial stress", "job loss", "career", "purpose", "identity",
    "persecution", "injustice", "racism", "political turmoil",
    "spiritual dryness", "feeling far from God", "new believer",
    "leadership", "serving others", "forgiveness", "reconciliation",
    "addiction recovery", "mental health", "trauma", "abuse",
    "friendship", "betrayal", "longing for community", "aging", "death of loved one"
]

SYSTEM_PROMPT = """You are a pastoral counselor and Bible scholar helping build 
a spiritual formation app called Selah. Your job is to identify which human 
emotions and life situations a Bible verse speaks to, and how it helps.

Be generous and thoughtful. A verse about God's faithfulness speaks to anxiety, 
doubt, grief, and waiting — not just one thing. Think about who would need this 
verse and why."""

def build_prompt(reference, text, meaning, application):
    emotions_list = ", ".join(EMOTIONS)
    situations_list = ", ".join(SITUATIONS)

    return f"""Analyze this Bible verse for the Selah app's feeling-based search system.

Verse: {reference}
Text: "{text}"
Meaning: {meaning}
Application: {application}

Your job is to identify:
1. Which emotions this verse speaks to (from the list OR add relevant ones not listed)
2. Which life situations this verse addresses
3. How this verse helps — categorize it into one or more of these types:
   - "names_it": directly acknowledges the feeling or situation
   - "reframes_it": shifts perspective or gives a new way of seeing
   - "command": gives something active to do
   - "story": connects to a biblical story where someone felt this way  
   - "promise": states what God will do or has done
   - "points_to_jesus": specifically shows how Jesus speaks to this

Common emotions to consider: {emotions_list}
Common situations to consider: {situations_list}

Also write a short "search_summary" — 1 sentence explaining what someone 
searching for this verse might be going through. This is what shows in search 
results to help them recognize it's for them.

Return ONLY valid JSON:
{{
  "emotions": ["emotion1", "emotion2"],
  "situations": ["situation1", "situation2"],
  "help_types": ["names_it", "promise"],
  "intensity": "comfort|challenge|both",
  "search_summary": "For someone who feels overwhelmed and needs to be reminded they are not alone.",
  "key_phrase": "The most comforting or powerful 5-8 words from this verse"
}}"""


def tag_verse(client, verse_data, lock):
    """Send a verse to Claude and get feelings tags back."""
    reference = verse_data.get("reference", "")
    text = verse_data.get("text", "")
    meaning = verse_data.get("meaning", "")
    application = verse_data.get("application", "")

    if not text:
        return None

    prompt = build_prompt(reference, text, meaning, application)

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            tags = json.loads(raw)

            # Merge tags into verse data
            result = dict(verse_data)
            result["feelings"] = {
                "emotions": tags.get("emotions", []),
                "situations": tags.get("situations", []),
                "help_types": tags.get("help_types", []),
                "intensity": tags.get("intensity", "both"),
                "search_summary": tags.get("search_summary", ""),
                "key_phrase": tags.get("key_phrase", ""),
            }
            return result

        except json.JSONDecodeError as e:
            with lock:
                print(f"\n  JSON error for {reference} (attempt {attempt+1}): {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
        except anthropic.RateLimitError:
            with lock:
                print(f"\n  Rate limited — waiting 30s...")
            time.sleep(30)
        except anthropic.APIError as e:
            with lock:
                print(f"\n  API error for {reference}: {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)

    return None


def get_output_path(book_name):
    safe = book_name.replace(" ", "_").lower()
    return OUTPUT_DIR / f"{safe}_feelings.json"


def load_existing_feelings(book_name):
    path = get_output_path(book_name)
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        return {(d["chapter"], d["verse"]): d for d in data}
    return {}


def save_book_feelings(book_name, verses_dict):
    path = get_output_path(book_name)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sorted_verses = sorted(verses_dict.values(), key=lambda v: (v["chapter"], v["verse"]))
    with open(path, "w") as f:
        json.dump(sorted_verses, f, indent=2, ensure_ascii=False)


def process_book(client, book_name):
    """Add feelings tags to all verses in a book."""
    # Find input file
    safe = book_name.replace(" ", "_").lower()
    input_path = INPUT_DIR / f"{safe}.json"

    if not input_path.exists():
        print(f"  No input file found for {book_name} at {input_path}")
        print(f"  Make sure generate.py has run first.")
        return

    with open(input_path) as f:
        verses = json.load(f)

    existing = load_existing_feelings(book_name)
    save_lock = threading.Lock()
    print_lock = threading.Lock()

    # Find verses that need tagging
    todos = [v for v in verses if (v["chapter"], v["verse"]) not in existing]

    if not todos:
        print(f"  {book_name}: all verses already tagged, skipping.")
        return

    print(f"\n{'='*60}")
    print(f"  {book_name} — tagging {len(todos)} verses with feelings")
    print(f"{'='*60}")

    verses_dict = dict(existing)
    completed = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(tag_verse, client, v, print_lock): v for v in todos}

        with tqdm(total=len(todos), desc=book_name, unit="verse") as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    with save_lock:
                        verses_dict[(result["chapter"], result["verse"])] = result
                        completed += 1
                        if completed % 10 == 0:
                            save_book_feelings(book_name, verses_dict)
                else:
                    failed += 1
                pbar.update(1)

    save_book_feelings(book_name, verses_dict)
    print(f"\n  Done: {completed} tagged, {failed} failed → {get_output_path(book_name)}")


def get_all_books():
    """Get list of books from existing output files."""
    if not INPUT_DIR.exists():
        return []
    files = sorted(INPUT_DIR.glob("*.json"))
    books = []
    for f in files:
        # Convert filename back to book name
        name = f.stem.replace("_", " ").title()
        # Fix known multi-word books
        fixes = {
            "1 Samuel": "1 Samuel", "2 Samuel": "2 Samuel",
            "1 Kings": "1 Kings", "2 Kings": "2 Kings",
            "1 Chronicles": "1 Chronicles", "2 Chronicles": "2 Chronicles",
            "Song Of Solomon": "Song of Solomon",
            "1 Corinthians": "1 Corinthians", "2 Corinthians": "2 Corinthians",
            "1 Thessalonians": "1 Thessalonians", "2 Thessalonians": "2 Thessalonians",
            "1 Timothy": "1 Timothy", "2 Timothy": "2 Timothy",
            "1 Peter": "1 Peter", "2 Peter": "2 Peter",
            "1 John": "1 John", "2 John": "2 John", "3 John": "3 John",
        }
        books.append(fixes.get(name, name))
    return books


def main():
    parser = argparse.ArgumentParser(
        description="Add feelings tags to Selah verse write-ups"
    )
    parser.add_argument("--book", help="Book name (e.g. 'John')")
    parser.add_argument("--all", action="store_true", help="Process all books")
    args = parser.parse_args()

    if not API_KEY:
        print("\nError: Set your API key via:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=API_KEY)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.all:
        books = get_all_books()
        if not books:
            print(f"No JSON files found in {INPUT_DIR}/")
            print("Run generate.py first.")
            sys.exit(1)
        print(f"Processing {len(books)} books...")
        for book in books:
            process_book(client, book)

    elif args.book:
        process_book(client, args.book)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
