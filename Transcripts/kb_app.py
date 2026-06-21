#!/usr/bin/env python3
"""Personal knowledge base Gradio app — chat, ingest, browse, and develop ideas."""
from __future__ import annotations

import os
import subprocess
import sys
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
_ensure("chromadb")
_ensure("sentence-transformers", "sentence_transformers")
_ensure("trafilatura")
_ensure("pdfplumber")
_ensure("yt-dlp", "yt_dlp")
_ensure("youtube-transcript-api", "youtube_transcript_api")

import gradio as gr
from anthropic import Anthropic
from dotenv import load_dotenv

ROOT = Path.home() / "claude-projects" / "Transcripts"
load_dotenv(ROOT / ".env")

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = (
    "You are a personal research assistant with access to the user's knowledge base, "
    "which contains YouTube video transcripts, web articles, PDF documents, and personal notes. "
    "Ground every answer in the provided sources and cite them. "
    "When the user asks about their ideas or notes, help them develop and connect those ideas "
    "to other content in their knowledge base. Be thoughtful, specific, and direct."
)

print("Loading knowledge base (first run downloads ~90MB embedding model)...")
from kb_core import KnowledgeBase
kb = KnowledgeBase()
print(f"Knowledge base ready. {kb.count_by_type()['total']} items indexed.")

client = Anthropic()

TYPE_BADGE = {
    "youtube": "[YouTube]",
    "article": "[Article]",
    "pdf": "[PDF]",
    "note": "[Note]",
}


# ------------------------------------------------------------------
# Chat helpers
# ------------------------------------------------------------------

def _build_doc_context(results: list[dict]) -> list[dict]:
    content: list[dict] = []
    for r in results:
        badge = TYPE_BADGE.get(r["type"], "[Doc]")
        content.append({
            "type": "document",
            "source": {"type": "text", "media_type": "text/plain", "data": r["content"] or r["metadata"].get("title", "")},
            "title": f"{badge} {r['title']}",
            "context": f"Source: {r['source']} | Type: {r['type']}",
            "citations": {"enabled": True},
        })
    if content:
        content[-1]["cache_control"] = {"type": "ephemeral"}
    return content


def _format_sources(results: list[dict]) -> str:
    if not results:
        return ""
    parts = ["\n\n**Sources searched:**"]
    for r in results:
        badge = TYPE_BADGE.get(r["type"], "[Doc]")
        title = r["title"] or "Untitled"
        source = r["source"]
        if source and source.startswith("http"):
            line = f"- {badge} [{title}]({source})"
        else:
            line = f"- {badge} {title}"
        parts.append(line)
    return "\n".join(parts)


def chat_fn(message: str, history) -> str:
    if not message.strip():
        return "Please enter a question."
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return f"ANTHROPIC_API_KEY not set. Add it to `{ROOT / '.env'}` and relaunch."

    counts = kb.count_by_type()
    total = counts["total"]
    if total == 0:
        return "Your knowledge base is empty. Add some content in the **Add Content** tab first."

    results = kb.search(message, n_results=6)
    if not results:
        return "No relevant content found in your knowledge base for that question."

    doc_content = _build_doc_context(results)
    doc_content.append({"type": "text", "text": message})

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": doc_content}],
        )
    except Exception as e:
        return f"API error: {e}"

    answer_parts: list[str] = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            answer_parts.append(block.text)

    answer_text = "".join(answer_parts).strip()
    status_line = f"\n\n_Searching {total} items in your knowledge base..._"
    return answer_text + status_line + _format_sources(results)


# ------------------------------------------------------------------
# Add content helpers
# ------------------------------------------------------------------

def _kb_count_md() -> str:
    c = kb.count_by_type()
    return (
        f"**{c['total']} items** in your knowledge base — "
        f"{c['youtube']} YouTube · {c['article']} Articles · "
        f"{c['pdf']} PDFs · {c['note']} Notes"
    )


def add_youtube(url: str):
    url = (url or "").strip()
    if not url:
        return "Please enter a YouTube URL.", _kb_count_md()
    try:
        result = kb.add_youtube(url)
    except Exception as e:
        return f"Error: {e}", _kb_count_md()
    if result["status"] == "duplicate":
        return f"Already in your knowledge base: **{result['title']}**", _kb_count_md()
    return f"Saved: **{result['title']}**", _kb_count_md()


def add_article(url: str):
    url = (url or "").strip()
    if not url:
        return "Please enter a URL.", _kb_count_md()
    try:
        result = kb.add_article(url)
    except Exception as e:
        return f"Error: {e}", _kb_count_md()
    return f"Saved: **{result['title']}**", _kb_count_md()


def add_pdf(file_obj):
    if file_obj is None:
        return "Please upload a PDF file.", _kb_count_md()
    try:
        result = kb.add_pdf(file_obj.name)
    except Exception as e:
        return f"Error: {e}", _kb_count_md()
    return f"Saved: **{result['title']}**", _kb_count_md()


def add_note(title: str, content: str, tags_str: str):
    title = (title or "").strip()
    content = (content or "").strip()
    if not title:
        return "Please enter a note title.", _kb_count_md()
    if not content:
        return "Please enter note content.", _kb_count_md()
    tags = [t.strip() for t in (tags_str or "").split(",") if t.strip()]
    try:
        result = kb.add_note(title, content, tags)
    except Exception as e:
        return f"Error: {e}", _kb_count_md()
    return f"Saved note: **{result['title']}**", _kb_count_md()


def show_youtube_inputs():
    return (
        gr.update(visible=True),   # yt_url
        gr.update(visible=True),   # yt_btn
        gr.update(visible=False),  # art_url
        gr.update(visible=False),  # art_btn
        gr.update(visible=False),  # pdf_file
        gr.update(visible=False),  # pdf_btn
        gr.update(visible=False),  # note_title
        gr.update(visible=False),  # note_content
        gr.update(visible=False),  # note_tags
        gr.update(visible=False),  # note_btn
    )


def show_article_inputs():
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def show_pdf_inputs():
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def show_note_inputs():
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
    )


TYPE_SHOW_FNS = {
    "YouTube": show_youtube_inputs,
    "Article": show_article_inputs,
    "PDF": show_pdf_inputs,
    "Note": show_note_inputs,
}


def on_type_change(choice: str):
    fn = TYPE_SHOW_FNS.get(choice, show_youtube_inputs)
    return fn()


# ------------------------------------------------------------------
# Library helpers
# ------------------------------------------------------------------

def load_library(filter_type: str):
    type_map = {
        "All": None,
        "YouTube": "youtube",
        "Articles": "article",
        "PDFs": "pdf",
        "Notes": "note",
    }
    ct = type_map.get(filter_type)
    items = kb.get_all(content_type=ct)

    rows = []
    for item in items:
        meta = item["metadata"]
        title = item["title"] or "Untitled"
        item_type = TYPE_BADGE.get(item["type"], item["type"])
        date = meta.get("publish_date") or meta.get("created_at", "")[:10]
        source = item["source"] or meta.get("file_path", "")
        if len(source) > 60:
            source = "..." + source[-57:]
        rows.append([title, item_type, date, source])

    count_str = f"**{len(rows)} items**"
    return rows, count_str


# ------------------------------------------------------------------
# Ideas helpers
# ------------------------------------------------------------------

def save_idea(title: str, content: str, tags_str: str):
    title = (title or "").strip()
    content = (content or "").strip()
    if not title:
        return "Please enter an idea title.", _kb_count_md()
    if not content:
        return "Please enter your idea.", _kb_count_md()
    tags = [t.strip() for t in (tags_str or "").split(",") if t.strip()]
    try:
        result = kb.add_note(title, content, tags)
    except Exception as e:
        return f"Error saving idea: {e}", _kb_count_md()
    return f"Idea saved: **{result['title']}**", _kb_count_md()


def find_connections(title: str, content: str):
    title = (title or "").strip()
    content = (content or "").strip()
    if not content:
        return "Please enter your idea first."
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return "ANTHROPIC_API_KEY not set."

    query = f"{title} {content}".strip()
    related = kb.search(query, n_results=5)
    if not related:
        return "No related content found in your knowledge base yet. Try adding more content first."

    doc_content = _build_doc_context(related)
    prompt = (
        f"Here is an idea I'm developing:\n\n"
        f"**Title:** {title or '(untitled)'}\n\n"
        f"{content}\n\n"
        f"What does this idea connect to in my knowledge base? "
        f"What related content have I already saved? What patterns do you see?"
    )
    doc_content.append({"type": "text", "text": prompt})

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": doc_content}],
        )
    except Exception as e:
        return f"API error: {e}"

    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "".join(parts).strip() + _format_sources(related)


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------

CUSTOM_CSS = """
.gradio-container {
    max-width: 960px !important;
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

with gr.Blocks(title="Knowledge Base", theme=THEME, css=CUSTOM_CSS, fill_height=True) as demo:
    with gr.Column(elem_id="header"):
        gr.Markdown("# Personal Knowledge Base")
        kb_count_md = gr.Markdown(_kb_count_md(), elem_id="subhead")

    with gr.Tabs():

        # ---- Tab 1: Chat ----
        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=chat_fn,
                type="messages",
                chatbot=gr.Chatbot(
                    type="messages",
                    height=520,
                    show_copy_button=True,
                    avatar_images=(None, None),
                    placeholder="Ask anything about your knowledge base.",
                ),
                textbox=gr.Textbox(
                    placeholder="Type your question...",
                    container=False,
                    scale=7,
                ),
                examples=[
                    "What are the key themes across everything I've saved?",
                    "Summarize what I know about AI businesses",
                    "Find connections between my notes and saved articles",
                    "What have I saved about investing and stocks?",
                ],
                cache_examples=False,
            )

        # ---- Tab 2: Add Content ----
        with gr.Tab("Add Content"):
            gr.Markdown("Add YouTube videos, web articles, PDFs, or personal notes to your knowledge base.")

            content_type = gr.Radio(
                choices=["YouTube", "Article", "PDF", "Note"],
                value="YouTube",
                label="Content type",
            )

            # YouTube inputs
            yt_url = gr.Textbox(
                label="YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                visible=True,
            )
            yt_btn = gr.Button("Fetch and save", variant="primary", visible=True)

            # Article inputs
            art_url = gr.Textbox(
                label="Article URL",
                placeholder="https://example.com/article",
                visible=False,
            )
            art_btn = gr.Button("Fetch and save", variant="primary", visible=False)

            # PDF inputs
            pdf_file = gr.File(
                label="PDF file",
                file_types=[".pdf"],
                visible=False,
            )
            pdf_btn = gr.Button("Add PDF", variant="primary", visible=False)

            # Note inputs
            note_title = gr.Textbox(label="Note title", visible=False)
            note_content = gr.Textbox(label="Your thought / idea", lines=6, visible=False)
            note_tags = gr.Textbox(
                label="Tags (comma-separated)",
                placeholder="startup, AI, marketing",
                visible=False,
            )
            note_btn = gr.Button("Save note", variant="primary", visible=False)

            add_status = gr.Markdown()
            add_count = gr.Markdown(_kb_count_md())

            all_inputs = [yt_url, yt_btn, art_url, art_btn, pdf_file, pdf_btn,
                          note_title, note_content, note_tags, note_btn]

            content_type.change(fn=on_type_change, inputs=[content_type], outputs=all_inputs)

            yt_btn.click(fn=add_youtube, inputs=[yt_url], outputs=[add_status, add_count])
            yt_url.submit(fn=add_youtube, inputs=[yt_url], outputs=[add_status, add_count])

            art_btn.click(fn=add_article, inputs=[art_url], outputs=[add_status, add_count])
            art_url.submit(fn=add_article, inputs=[art_url], outputs=[add_status, add_count])

            pdf_btn.click(fn=add_pdf, inputs=[pdf_file], outputs=[add_status, add_count])

            note_btn.click(
                fn=add_note,
                inputs=[note_title, note_content, note_tags],
                outputs=[add_status, add_count],
            )

        # ---- Tab 3: Library ----
        with gr.Tab("Library"):
            gr.Markdown("Browse everything in your knowledge base.")

            with gr.Row():
                lib_filter = gr.Radio(
                    choices=["All", "YouTube", "Articles", "PDFs", "Notes"],
                    value="All",
                    label="Filter by type",
                    scale=4,
                )
                lib_refresh = gr.Button("Refresh", scale=1)

            lib_count = gr.Markdown()
            lib_table = gr.Dataframe(
                headers=["Title", "Type", "Date", "Source"],
                datatype=["str", "str", "str", "str"],
                interactive=False,
                wrap=True,
            )

            def refresh_library(filter_type: str):
                rows, count = load_library(filter_type)
                return rows, count

            lib_filter.change(fn=refresh_library, inputs=[lib_filter], outputs=[lib_table, lib_count])
            lib_refresh.click(fn=refresh_library, inputs=[lib_filter], outputs=[lib_table, lib_count])

            # Load on startup
            demo.load(fn=refresh_library, inputs=[lib_filter], outputs=[lib_table, lib_count])

        # ---- Tab 4: Ideas ----
        with gr.Tab("Ideas"):
            gr.Markdown(
                "Capture ideas and let your knowledge base help you develop them. "
                "Save an idea as a note, or find what you've already saved that connects to it."
            )

            idea_title = gr.Textbox(label="Idea title", placeholder="e.g. Build a micro-SaaS for...")
            idea_content = gr.Textbox(
                label="Your thought / idea",
                lines=8,
                placeholder="Describe your idea in detail...",
            )
            idea_tags = gr.Textbox(
                label="Tags (comma-separated)",
                placeholder="startup, AI, marketing",
            )

            with gr.Row():
                idea_save_btn = gr.Button("Save idea as note", variant="secondary")
                idea_connect_btn = gr.Button("Find connections", variant="primary")

            idea_status = gr.Markdown()
            idea_count = gr.Markdown()
            idea_connections = gr.Markdown()

            idea_save_btn.click(
                fn=save_idea,
                inputs=[idea_title, idea_content, idea_tags],
                outputs=[idea_status, idea_count],
            )
            idea_connect_btn.click(
                fn=find_connections,
                inputs=[idea_title, idea_content],
                outputs=[idea_connections],
            )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
