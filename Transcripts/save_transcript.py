#!/usr/bin/env python3
"""Fetch a YouTube video's transcript + metadata and save to ~/claude-projects/Transcripts/."""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

OUT_DIR = Path.home() / "claude-projects" / "Transcripts"


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:120] or "untitled"


def fetch_metadata(url: str) -> dict:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    upload_date = info.get("upload_date")  # YYYYMMDD
    iso_date = (
        f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        if upload_date
        else datetime.now().strftime("%Y-%m-%d")
    )
    return {
        "video_id": info.get("id"),
        "title": info.get("title"),
        "channel": info.get("channel") or info.get("uploader"),
        "publish_date": iso_date,
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "duration_seconds": info.get("duration"),
        "url": info.get("webpage_url") or url,
    }


def fetch_transcript(video_id: str) -> str:
    segments = YouTubeTranscriptApi().fetch(video_id)
    return "\n".join(s.text for s in segments)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube video URL")
    args = parser.parse_args()

    meta = fetch_metadata(args.url)
    if not meta["video_id"]:
        print("Could not resolve video ID", file=sys.stderr)
        return 1

    transcript = fetch_transcript(meta["video_id"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    basename = f"{meta['publish_date']}_{slugify(meta['title'])}"
    txt_path = OUT_DIR / f"{basename}.txt"
    json_path = OUT_DIR / f"{basename}.json"

    txt_path.write_text(transcript)
    json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"Transcript: {txt_path}")
    print(f"Metadata:   {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
