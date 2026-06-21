"""
offline_bible.py — Offline Bible verse loader
===============================================
Use this if you want to run without internet access.

Downloads a public domain Bible (World English Bible) once and
saves it locally so generate.py can run fully offline.

Usage:
    python offline_bible.py download   # Download WEB Bible locally
    python offline_bible.py test John 3 16  # Test a verse lookup
"""

import json
import sys
import os
import urllib.request
from pathlib import Path

BIBLE_FILE = Path("bible_web.json")
WEB_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_web.json"


def download_bible():
    """Download the World English Bible JSON (one-time setup)."""
    if BIBLE_FILE.exists():
        print(f"Bible already downloaded at {BIBLE_FILE}")
        return

    print("Downloading World English Bible (public domain)...")
    print(f"Source: {WEB_URL}")
    urllib.request.urlretrieve(WEB_URL, BIBLE_FILE)
    print(f"Saved to {BIBLE_FILE}")
    verify_bible()


def verify_bible():
    """Quick check that the file loaded correctly."""
    data = load_bible()
    if data:
        total = sum(len(ch) for book in data for ch in book["chapters"])
        print(f"Verified: {len(data)} books, {total} verses loaded")
    else:
        print("Warning: Bible file may be corrupt")


def load_bible():
    """Load Bible data from local file."""
    if not BIBLE_FILE.exists():
        print(f"Bible not downloaded. Run: python offline_bible.py download")
        return None
    with open(BIBLE_FILE, encoding="utf-8") as f:
        return json.load(f)


# Book name normalization
BOOK_NAME_MAP = {
    "Genesis": 0, "Exodus": 1, "Leviticus": 2, "Numbers": 3,
    "Deuteronomy": 4, "Joshua": 5, "Judges": 6, "Ruth": 7,
    "1 Samuel": 8, "2 Samuel": 9, "1 Kings": 10, "2 Kings": 11,
    "1 Chronicles": 12, "2 Chronicles": 13, "Ezra": 14, "Nehemiah": 15,
    "Esther": 16, "Job": 17, "Psalms": 18, "Proverbs": 19,
    "Ecclesiastes": 20, "Song of Solomon": 21, "Isaiah": 22,
    "Jeremiah": 23, "Lamentations": 24, "Ezekiel": 25, "Daniel": 26,
    "Hosea": 27, "Joel": 28, "Amos": 29, "Obadiah": 30, "Jonah": 31,
    "Micah": 32, "Nahum": 33, "Habakkuk": 34, "Zephaniah": 35,
    "Haggai": 36, "Zechariah": 37, "Malachi": 38,
    "Matthew": 39, "Mark": 40, "Luke": 41, "John": 42, "Acts": 43,
    "Romans": 44, "1 Corinthians": 45, "2 Corinthians": 46,
    "Galatians": 47, "Ephesians": 48, "Philippians": 49, "Colossians": 50,
    "1 Thessalonians": 51, "2 Thessalonians": 52, "1 Timothy": 53,
    "2 Timothy": 54, "Titus": 55, "Philemon": 56, "Hebrews": 57,
    "James": 58, "1 Peter": 59, "2 Peter": 60, "1 John": 61,
    "2 John": 62, "3 John": 63, "Jude": 64, "Revelation": 65,
}

_bible_cache = None


def get_verse(book, chapter, verse):
    """
    Look up a verse from the local Bible file.
    Returns the verse text string, or None if not found.

    Args:
        book: Book name string (e.g. "John")
        chapter: Chapter number (1-indexed)
        verse: Verse number (1-indexed)
    """
    global _bible_cache
    if _bible_cache is None:
        _bible_cache = load_bible()
    if _bible_cache is None:
        return None

    book_idx = BOOK_NAME_MAP.get(book)
    if book_idx is None:
        return None

    try:
        book_data = _bible_cache[book_idx]
        chapter_data = book_data["chapters"][chapter - 1]
        verse_text = chapter_data[verse - 1]
        return verse_text.strip()
    except (IndexError, KeyError, TypeError):
        return None


def patch_generate_py():
    """
    Patch generate.py to use offline Bible instead of API calls.
    Run this after downloading the Bible to switch to offline mode.
    """
    generate_path = Path("generate.py")
    if not generate_path.exists():
        print("generate.py not found in current directory")
        return

    content = generate_path.read_text()

    old = "def fetch_verse_text(book, chapter, verse):\n    \"\"\"Fetch verse text from bible-api.com (requires internet).\"\"\"\n    import requests\n    ref = f\"{book}+{chapter}:{verse}\".replace(\" \", \"+\")\n    url = f\"https://bible-api.com/{ref}?translation=web\"\n    try:\n        r = requests.get(url, timeout=10)\n        data = r.json()\n        return data.get(\"text\", \"\").strip()\n    except Exception as e:\n        print(f\"  Warning: Could not fetch {book} {chapter}:{verse} — {e}\")\n        return None"

    new = "def fetch_verse_text(book, chapter, verse):\n    \"\"\"Fetch verse text from local Bible file (offline mode).\"\"\"\n    from offline_bible import get_verse\n    text = get_verse(book, chapter, verse)\n    if not text:\n        print(f\"  Warning: Could not find {book} {chapter}:{verse} in local Bible\")\n    return text"

    if old in content:
        content = content.replace(old, new)
        generate_path.write_text(content)
        print("generate.py patched for offline mode.")
    else:
        print("Could not patch generate.py — function signature may have changed.")
        print("Manually replace fetch_verse_text() to use offline_bible.get_verse()")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "download":
        download_bible()

    elif cmd == "patch":
        patch_generate_py()

    elif cmd == "test":
        if len(sys.argv) < 5:
            print("Usage: python offline_bible.py test <book> <chapter> <verse>")
            print("Example: python offline_bible.py test John 3 16")
            sys.exit(1)
        book = sys.argv[2]
        chapter = int(sys.argv[3])
        verse = int(sys.argv[4])
        text = get_verse(book, chapter, verse)
        if text:
            print(f"\n{book} {chapter}:{verse}")
            print(f'"{text}"')
        else:
            print(f"Verse not found: {book} {chapter}:{verse}")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: download, patch, test")
