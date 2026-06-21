"""
test_single.py — Test a single verse write-up
===============================================
Run this first to validate your API key and prompt quality
before running the full generator.

Usage:
    python test_single.py
    python test_single.py John 15 5
    python test_single.py Psalms 23 1
"""

import anthropic
import json
import os
import sys

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Import the prompt builder and system prompt from generate.py
sys.path.insert(0, ".")
from generate import build_prompt, SYSTEM_PROMPT, BOOK_GENRES, MODEL


def test_verse(book="John", chapter=15, verse=5):
    if not API_KEY:
        print("Error: Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    # Simple text lookup for test (you can hardcode or pass in)
    sample_texts = {
        ("John", 15, 5): "I am the vine, you are the branches. He who remains in me and I in him bears much fruit, for apart from me you can do nothing.",
        ("Psalms", 23, 1): "The LORD is my shepherd; I shall lack nothing.",
        ("Romans", 8, 28): "We know that all things work together for good for those who love God, to those who are called according to his purpose.",
        ("Philippians", 4, 13): "I can do all things through Christ, who strengthens me.",
    }

    text = sample_texts.get((book, chapter, verse))
    if not text:
        print(f"No sample text for {book} {chapter}:{verse}.")
        print("Add it to sample_texts in test_single.py, or run generate.py directly.")
        sys.exit(1)

    genre = BOOK_GENRES.get(book, "narrative")
    print(f"\nTesting: {book} {chapter}:{verse} ({genre})")
    print(f'Text: "{text[:80]}..."' if len(text) > 80 else f'Text: "{text}"')
    print("\nCalling Claude API...")

    client = anthropic.Anthropic(api_key=API_KEY)
    prompt = build_prompt(book, chapter, verse, text, genre)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw)
        print("\n" + "="*60)
        print(f"HEADLINE: {data.get('headline', '')}")
        print("="*60)
        print(f"\nWORD STUDY:\n{data.get('word_study', '')}")
        print(f"\nCONTEXT:\n{data.get('context', '')}")
        print(f"\nMEANING:\n{data.get('meaning', '')}")
        print(f"\nAPPLICATION:\n{data.get('application', '')}")
        print(f"\nCROSS-REFERENCE:\n{data.get('connection', '')}")
        print(f"\nPRAYER PROMPT:\n{data.get('prayer_prompt', '')}")
        print("\n" + "="*60)
        print("\nFull JSON output:")
        print(json.dumps(data, indent=2))

        # Usage stats
        usage = response.usage
        print(f"\nTokens used: {usage.input_tokens} in / {usage.output_tokens} out")
        est_cost = (usage.input_tokens / 1_000_000 * 3) + (usage.output_tokens / 1_000_000 * 15)
        print(f"Estimated cost for this verse: ~${est_cost:.4f}")
        print(f"Estimated cost for full Bible (31,102 verses): ~${est_cost * 31102:.0f}")

    except json.JSONDecodeError as e:
        print(f"\nJSON parse error: {e}")
        print("Raw response:")
        print(raw)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        book = sys.argv[1]
        chapter = int(sys.argv[2])
        verse = int(sys.argv[3])
        test_verse(book, chapter, verse)
    else:
        test_verse()
