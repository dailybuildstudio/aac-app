"""
Selah Feelings Index Builder
==============================
Reads all output_feelings/*.json files and compiles a master
feelings_index.json — the engine behind Selah's emotion-based search.

Run AFTER generate_feelings.py has finished.

Usage:
    python3 build_feelings_index.py
"""

import json
from pathlib import Path
from collections import defaultdict

INPUT_DIR = Path("output_feelings")
OUTPUT_FILE = Path("feelings_index.json")
OVERVIEW_FILE = Path("feelings_overview.json")


def build_index():
    if not INPUT_DIR.exists():
        print(f"No output_feelings/ folder found.")
        print("Run generate_feelings.py first.")
        return

    files = sorted(INPUT_DIR.glob("*_feelings.json"))
    if not files:
        print("No feelings files found. Run generate_feelings.py first.")
        return

    print(f"Building feelings index from {len(files)} books...")

    # Master index structure
    # feelings_index[emotion][help_type] = list of verse refs
    index = defaultdict(lambda: defaultdict(list))
    situation_index = defaultdict(list)
    all_verses = []
    total = 0

    for file in files:
        with open(file) as f:
            verses = json.load(f)

        for verse in verses:
            feelings = verse.get("feelings", {})
            if not feelings:
                continue

            ref = verse.get("reference", "")
            text = verse.get("text", "")
            headline = verse.get("headline", "")
            key_phrase = feelings.get("key_phrase", "")
            search_summary = feelings.get("search_summary", "")
            intensity = feelings.get("intensity", "both")
            help_types = feelings.get("help_types", [])
            emotions = feelings.get("emotions", [])
            situations = feelings.get("situations", [])

            # Compact verse entry for the index
            entry = {
                "ref": ref,
                "text": text,
                "headline": headline,
                "key_phrase": key_phrase,
                "search_summary": search_summary,
                "intensity": intensity,
                "help_types": help_types,
                "book": verse.get("book", ""),
                "chapter": verse.get("chapter", 0),
                "verse": verse.get("verse", 0),
            }

            # Add to emotion index by help type
            for emotion in emotions:
                emotion_key = emotion.lower().strip()
                for help_type in help_types:
                    index[emotion_key][help_type].append(entry)
                # Also add to flat list for this emotion
                if "all" not in index[emotion_key]:
                    index[emotion_key]["all"] = []
                # Avoid duplicates in all list
                refs_in_all = [e["ref"] for e in index[emotion_key]["all"]]
                if ref not in refs_in_all:
                    index[emotion_key]["all"].append(entry)

            # Add to situation index
            for situation in situations:
                sit_key = situation.lower().strip()
                sit_refs = [e["ref"] for e in situation_index[sit_key]]
                if ref not in sit_refs:
                    situation_index[sit_key].append(entry)

            all_verses.append(entry)
            total += 1

    # Build final output
    final_index = {
        "emotions": {k: dict(v) for k, v in index.items()},
        "situations": dict(situation_index),
        "meta": {
            "total_verses_tagged": total,
            "total_emotions": len(index),
            "total_situations": len(situation_index),
            "books_processed": len(files),
        }
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_index, f, indent=2, ensure_ascii=False)

    # Build a lighter overview for quick lookup
    overview = {
        "emotions": {},
        "situations": {},
        "meta": final_index["meta"]
    }

    for emotion, help_types in index.items():
        overview["emotions"][emotion] = {
            "total_verses": len(help_types.get("all", [])),
            "help_types_available": [k for k in help_types.keys() if k != "all"],
            "top_3": [
                {"ref": v["ref"], "key_phrase": v["key_phrase"]}
                for v in help_types.get("all", [])[:3]
            ]
        }

    for situation, verses in situation_index.items():
        overview["situations"][situation] = {
            "total_verses": len(verses),
            "top_3": [
                {"ref": v["ref"], "key_phrase": v["key_phrase"]}
                for v in verses[:3]
            ]
        }

    with open(OVERVIEW_FILE, "w") as f:
        json.dump(overview, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Index built successfully!")
    print(f"{'='*60}")
    print(f"  Total verses tagged:    {total:,}")
    print(f"  Emotions indexed:       {len(index)}")
    print(f"  Situations indexed:     {len(situation_index)}")
    print(f"  Books processed:        {len(files)}")
    print(f"\n  Full index →  {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size // 1024}KB)")
    print(f"  Overview   →  {OVERVIEW_FILE}")
    print(f"\nTop emotions by verse count:")

    # Show top 20 emotions
    sorted_emotions = sorted(
        overview["emotions"].items(),
        key=lambda x: x[1]["total_verses"],
        reverse=True
    )
    for emotion, data in sorted_emotions[:20]:
        bar = "█" * min(data["total_verses"] // 10, 40)
        print(f"  {emotion:<20} {data['total_verses']:>4} verses  {bar}")

    print(f"\nTop situations by verse count:")
    sorted_situations = sorted(
        overview["situations"].items(),
        key=lambda x: x[1]["total_verses"],
        reverse=True
    )
    for situation, data in sorted_situations[:15]:
        print(f"  {situation:<35} {data['total_verses']:>4} verses")


def search_feelings(emotion, help_type=None):
    """
    Quick search function — use this to test the index.
    
    Usage:
        python3 build_feelings_index.py search anxiety
        python3 build_feelings_index.py search anxiety promise
    """
    if not OUTPUT_FILE.exists():
        print("Run build_feelings_index.py first to build the index.")
        return

    with open(OUTPUT_FILE) as f:
        index = json.load(f)

    emotion_data = index["emotions"].get(emotion.lower())
    if not emotion_data:
        print(f"No verses found for emotion: {emotion}")
        # Suggest similar
        all_emotions = list(index["emotions"].keys())
        similar = [e for e in all_emotions if emotion.lower() in e or e in emotion.lower()]
        if similar:
            print(f"Did you mean: {', '.join(similar[:5])}")
        return

    if help_type:
        verses = emotion_data.get(help_type, [])
        print(f"\n{emotion.upper()} — {help_type.upper()} ({len(verses)} verses)\n")
    else:
        verses = emotion_data.get("all", [])
        print(f"\n{emotion.upper()} — ALL TYPES ({len(verses)} verses)\n")
        # Show breakdown by help type
        for ht in ["names_it", "reframes_it", "command", "story", "promise", "points_to_jesus"]:
            count = len(emotion_data.get(ht, []))
            if count:
                print(f"  {ht}: {count} verses")
        print()

    for i, verse in enumerate(verses[:10], 1):
        print(f"  {i}. {verse['ref']}")
        print(f"     \"{verse['key_phrase']}\"")
        print(f"     {verse['search_summary']}")
        print(f"     Types: {', '.join(verse['help_types'])}")
        print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "search":
        emotion = sys.argv[2] if len(sys.argv) > 2 else "anxiety"
        help_type = sys.argv[3] if len(sys.argv) > 3 else None
        search_feelings(emotion, help_type)
    else:
        build_index()
