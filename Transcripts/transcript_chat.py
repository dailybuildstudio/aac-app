#!/usr/bin/env python3
"""Local Gradio chat over YouTube transcripts using the Anthropic API."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _ensure(pkg: str, import_name: str | None = None) -> None:
    try:
        __import__(import_name or pkg)
    except ImportError:
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


_ensure("gradio")
_ensure("anthropic")
_ensure("python-dotenv", "dotenv")
_ensure("yt-dlp", "yt_dlp")
_ensure("youtube-transcript-api", "youtube_transcript_api")

import gradio as gr
import yt_dlp
from anthropic import Anthropic
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

ROOT = Path.home() / "claude-projects" / "Transcripts"
ENV_PATH = ROOT / ".env"
load_dotenv(ENV_PATH)

MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are a research assistant answering questions based on YouTube video "
    "transcripts. Ground every claim in the provided transcripts and cite the "
    "specific videos you draw from. If the transcripts don't contain the answer, "
    "say so plainly. Be concise and factual."
)


def load_transcripts() -> list[dict]:
    docs = []
    for txt in sorted(ROOT.rglob("*.txt")):
        if not txt.is_file():
            continue
        meta_path = txt.with_suffix(".json")
        meta: dict = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
            except json.JSONDecodeError:
                pass
        docs.append({
            "path": txt,
            "mtime": txt.stat().st_mtime,
            "video_id": meta.get("video_id") or "",
            "title": meta.get("title") or txt.stem,
            "channel": meta.get("channel") or "Unknown",
            "publish_date": meta.get("publish_date") or "",
            "view_count": meta.get("view_count"),
            "url": meta.get("url") or "",
            "transcript": txt.read_text(),
        })
    return docs


MAX_DOCS_PER_QUERY = 5

RECENT_PATTERNS = (
    "last added", "latest", "most recent", "newest",
    "just added", "recently added", "last transcript", "newest transcript",
)

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "this", "that", "these", "those", "i", "you", "he", "she", "we", "they",
    "what", "which", "who", "whom", "when", "where", "why", "how", "do",
    "does", "did", "can", "could", "should", "would", "will", "say", "said",
    "tell", "told", "about", "from", "as", "at", "by", "if", "so", "not",
    "have", "has", "had", "any", "all", "some", "me", "my", "your", "our",
    "transcript", "transcripts", "video", "videos",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def select_relevant_docs(question: str, docs: list[dict]) -> list[dict]:
    if not docs:
        return []

    q_lower = question.lower()
    if any(p in q_lower for p in RECENT_PATTERNS):
        return [max(docs, key=lambda d: d["mtime"])]

    keywords = [t for t in _tokenize(question) if t not in STOPWORDS and len(t) > 2]
    if not keywords:
        return sorted(docs, key=lambda d: d["mtime"], reverse=True)[:MAX_DOCS_PER_QUERY]

    scored: list[tuple[int, float, dict]] = []
    for d in docs:
        body = d["transcript"].lower()
        meta_blob = f"{d['title']}\n{d['channel']}".lower()
        score = 0
        for k in keywords:
            in_meta = k in meta_blob
            body_hits = body.count(k)
            if in_meta:
                score += 50
            if body_hits > 0:
                score += 5 + min(body_hits, 20)
        if score > 0:
            scored.append((score, d["mtime"], d))

    if not scored:
        return sorted(docs, key=lambda d: d["mtime"], reverse=True)[:MAX_DOCS_PER_QUERY]

    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [d for _, _, d in scored[:MAX_DOCS_PER_QUERY]]


DOCS = load_transcripts()
client = Anthropic()


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


def fetch_clean_transcript(video_id: str) -> str:
    segments = YouTubeTranscriptApi().fetch(video_id)
    parts = [s.text.strip() for s in segments if s.text and s.text.strip()]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def find_orphans() -> list[Path]:
    return [
        txt for txt in sorted(ROOT.rglob("*.txt"))
        if txt.is_file() and not txt.with_suffix(".json").exists()
    ]


def orphan_choices() -> list[str]:
    return [str(o.relative_to(ROOT)) for o in find_orphans()]


def orphan_list_md() -> str:
    orphans = find_orphans()
    if not orphans:
        return "_All transcripts have metadata._"
    lines = [f"**{len(orphans)} transcript(s) missing metadata:**"]
    for o in orphans:
        lines.append(f"- `{o.relative_to(ROOT)}`")
    return "\n".join(lines)


def doc_count_md() -> str:
    return f"Loaded **{len(DOCS)}** transcripts from `{ROOT}`"


def _no_change():
    return gr.update()


def ingest_url(url: str):
    url = (url or "").strip()
    if not url:
        return "Please enter a YouTube URL.", doc_count_md(), orphan_list_md(), _no_change(), url

    try:
        meta = fetch_metadata(url)
    except Exception as e:
        return f"Error fetching metadata: {e}", doc_count_md(), orphan_list_md(), _no_change(), url

    video_id = meta.get("video_id")
    if not video_id:
        return "Could not resolve video ID from URL.", doc_count_md(), orphan_list_md(), _no_change(), url

    existing = next((d for d in DOCS if d.get("video_id") == video_id), None)
    if existing:
        rel = existing["path"].relative_to(ROOT)
        return (
            f"Already saved as `{rel}` — skipped re-download.",
            doc_count_md(),
            orphan_list_md(),
            _no_change(),
            "",
        )

    try:
        transcript = fetch_clean_transcript(video_id)
    except Exception as e:
        return f"Error fetching transcript: {e}", doc_count_md(), orphan_list_md(), _no_change(), url

    ROOT.mkdir(parents=True, exist_ok=True)
    basename = f"{meta['publish_date']}_{slugify(meta['title'])}"
    txt_path = ROOT / f"{basename}.txt"
    json_path = ROOT / f"{basename}.json"
    txt_path.write_text(transcript)
    json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    DOCS[:] = load_transcripts()
    rel = txt_path.relative_to(ROOT)
    return (
        f"Saved `{rel}` ({len(transcript):,} chars).",
        doc_count_md(),
        orphan_list_md(),
        gr.update(choices=orphan_choices(), value=None),
        "",
    )


def generate_metadata(orphan_rel: str, url: str):
    if not orphan_rel:
        return "Pick a transcript first.", orphan_list_md(), _no_change(), url, doc_count_md()
    url = (url or "").strip()
    if not url:
        return "Enter the YouTube URL for the selected transcript.", orphan_list_md(), _no_change(), url, doc_count_md()

    txt_path = ROOT / orphan_rel
    if not txt_path.exists():
        return (
            f"Not found: `{orphan_rel}`",
            orphan_list_md(),
            gr.update(choices=orphan_choices(), value=None),
            url,
            doc_count_md(),
        )

    try:
        meta = fetch_metadata(url)
    except Exception as e:
        return f"Error fetching metadata: {e}", orphan_list_md(), _no_change(), url, doc_count_md()
    if not meta.get("video_id"):
        return "Could not resolve video ID.", orphan_list_md(), _no_change(), url, doc_count_md()

    json_path = txt_path.with_suffix(".json")
    json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    DOCS[:] = load_transcripts()
    return (
        f"Generated metadata for `{orphan_rel}`.",
        orphan_list_md(),
        gr.update(choices=orphan_choices(), value=None),
        "",
        doc_count_md(),
    )


def refresh_orphans():
    return orphan_list_md(), gr.update(choices=orphan_choices(), value=None)


def build_user_content(question: str, docs: list[dict]) -> list[dict]:
    content: list[dict] = []
    for d in docs:
        content.append({
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": d["transcript"],
            },
            "title": d["title"],
            "context": (
                f"Channel: {d['channel']} | Published: {d['publish_date']} | "
                f"URL: {d['url']}"
            ),
            "citations": {"enabled": True},
        })
    if content:
        content[-1]["cache_control"] = {"type": "ephemeral"}
    content.append({"type": "text", "text": question})
    return content


def format_sources(docs_cited: list[dict], docs_searched: list[dict]) -> str:
    parts: list[str] = []
    if docs_cited:
        parts.append("")
        parts.append("**Sources cited:**")
        for d in docs_cited:
            url = d["url"] or ""
            title = d["title"]
            link = f"[{title}]({url})" if url else title
            parts.append(f"- {link} — {d['channel']}, {d['publish_date']}")
    if docs_searched:
        parts.append("")
        parts.append(
            f"_Searched {len(docs_searched)} transcript(s): "
            + ", ".join(f"`{d['title']}`" for d in docs_searched)
            + "_"
        )
    return "\n".join(parts)


def answer(question: str) -> str:
    if not question.strip():
        return "Please enter a question."
    if not DOCS:
        return f"No transcripts found in `{ROOT}`."
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return (
            f"ANTHROPIC_API_KEY not found. Add it to `{ENV_PATH}` as "
            "`ANTHROPIC_API_KEY=sk-ant-...` and relaunch."
        )

    selected = select_relevant_docs(question, DOCS)

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_content(question, selected)}],
        )
    except Exception as e:
        return f"API error: {e}"

    answer_parts: list[str] = []
    cited_indices: set[int] = set()
    for block in resp.content:
        if getattr(block, "type", None) != "text":
            continue
        answer_parts.append(block.text)
        for c in (getattr(block, "citations", None) or []):
            idx = getattr(c, "document_index", None)
            if idx is not None:
                cited_indices.add(idx)

    answer_text = "".join(answer_parts).strip()
    docs_cited = [selected[i] for i in sorted(cited_indices) if i < len(selected)]
    return answer_text + format_sources(docs_cited, selected)


def chat_fn(message: str, history) -> str:
    return answer(message)


CUSTOM_CSS = """
.gradio-container {
    max-width: 860px !important;
    margin: 0 auto !important;
    padding: 12px !important;
}
#header h1 { margin: 0 0 4px 0; font-size: 1.6rem; }
#subhead { color: var(--body-text-color-subdued); margin-bottom: 8px; }
footer { display: none !important; }
@media (max-width: 640px) {
    .gradio-container { padding: 8px !important; }
    #header h1 { font-size: 1.35rem; }
    .tabitem { padding: 8px !important; }
}
"""

THEME = gr.themes.Soft(
    primary_hue="indigo",
    secondary_hue="slate",
    radius_size=gr.themes.sizes.radius_lg,
)

with gr.Blocks(title="Transcript Chat", theme=THEME, css=CUSTOM_CSS, fill_height=True) as demo:
    with gr.Column(elem_id="header"):
        gr.Markdown("# Transcript Chat")
        count_md = gr.Markdown(doc_count_md(), elem_id="subhead")

    with gr.Tabs():
        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=chat_fn,
                type="messages",
                chatbot=gr.Chatbot(
                    type="messages",
                    height=520,
                    show_copy_button=True,
                    avatar_images=(None, None),
                    placeholder="Ask anything about your saved transcripts.",
                ),
                textbox=gr.Textbox(
                    placeholder="Type your question...",
                    container=False,
                    scale=7,
                ),
                examples=[
                    "Summarize the key themes across all transcripts.",
                    "What did Tom Lee say about the market crash?",
                    "Which stocks does Dan Niles like for AI exposure?",
                ],
                cache_examples=False,
            )

        with gr.Tab("Add transcript"):
            gr.Markdown("Paste a YouTube URL. The transcript and metadata save to your library.")
            url_input = gr.Textbox(
                label="YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                autofocus=True,
            )
            ingest_btn = gr.Button("Fetch and save", variant="primary", size="lg")
            ingest_status = gr.Markdown()

        with gr.Tab("Fix metadata"):
            gr.Markdown(
                "Generate metadata for transcripts that don't have a `.json` companion file."
            )
            orphan_md = gr.Markdown(orphan_list_md())
            with gr.Row(equal_height=True):
                orphan_picker = gr.Dropdown(
                    orphan_choices(),
                    label="Transcript",
                    value=None,
                    scale=3,
                )
                refresh_btn = gr.Button("Refresh", scale=1)
            orphan_url = gr.Textbox(
                label="YouTube URL for selected transcript",
                placeholder="https://www.youtube.com/watch?v=...",
            )
            fix_btn = gr.Button("Generate metadata", variant="primary", size="lg")
            fix_status = gr.Markdown()

    ingest_btn.click(
        fn=ingest_url,
        inputs=[url_input],
        outputs=[ingest_status, count_md, orphan_md, orphan_picker, url_input],
    )
    url_input.submit(
        fn=ingest_url,
        inputs=[url_input],
        outputs=[ingest_status, count_md, orphan_md, orphan_picker, url_input],
    )
    fix_btn.click(
        fn=generate_metadata,
        inputs=[orphan_picker, orphan_url],
        outputs=[fix_status, orphan_md, orphan_picker, orphan_url, count_md],
    )
    refresh_btn.click(fn=refresh_orphans, outputs=[orphan_md, orphan_picker])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
