#!/usr/bin/env python3
"""Knowledge base engine — no Gradio imports. Handles storage, embedding, and retrieval."""
from __future__ import annotations

import hashlib
import json
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


_ensure("chromadb")
_ensure("sentence-transformers", "sentence_transformers")
_ensure("trafilatura")
_ensure("pdfplumber")
_ensure("yt-dlp", "yt_dlp")
_ensure("youtube-transcript-api", "youtube_transcript_api")
_ensure("python-dotenv", "dotenv")
_ensure("anthropic")

import chromadb
import pdfplumber
import trafilatura
import yt_dlp
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

ROOT = Path.home() / "claude-projects" / "Transcripts"
DB_PATH = ROOT / ".chromadb"

load_dotenv(ROOT / ".env")


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:120] or "untitled"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


class KnowledgeBase:
    def __init__(self) -> None:
        # Create subdirectories
        for subdir in ("articles", "notes", "pdfs"):
            (ROOT / subdir).mkdir(parents=True, exist_ok=True)

        # Init ChromaDB
        ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self._client = chromadb.PersistentClient(path=str(DB_PATH))
        self._col = self._client.get_or_create_collection(
            name="kb",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        # Import any existing files not yet in the index
        self._import_existing()

    # ------------------------------------------------------------------
    # Public ingestion methods
    # ------------------------------------------------------------------

    def add_youtube(self, url: str) -> dict:
        """Fetch a YouTube video's transcript and add it to the KB."""
        meta = self._fetch_yt_metadata(url)
        video_id = meta.get("video_id")
        if not video_id:
            raise ValueError("Could not resolve video ID from URL.")

        doc_id = f"yt_{video_id}"

        # Duplicate check
        existing = self._col.get(ids=[doc_id])
        if existing["ids"]:
            file_path = existing["metadatas"][0].get("file_path", "")
            return {"status": "duplicate", "title": meta.get("title", ""), "file_path": file_path}

        transcript = self._fetch_yt_transcript(video_id)

        basename = f"{meta['publish_date']}_{slugify(meta['title'])}"
        txt_path = ROOT / f"{basename}.txt"
        json_path = ROOT / f"{basename}.json"
        txt_path.write_text(transcript)
        json_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

        chroma_meta = {
            "type": "youtube",
            "title": meta.get("title") or "",
            "source": meta.get("url") or url,
            "channel": meta.get("channel") or "",
            "publish_date": meta.get("publish_date") or "",
            "file_path": str(txt_path),
            "created_at": _today(),
        }
        self._upsert(doc_id, transcript, chroma_meta, transcript, str(txt_path))

        return {"status": "saved", "title": meta.get("title", ""), "file_path": str(txt_path)}

    def add_article(self, url: str) -> dict:
        """Scrape a web article and add it to the KB."""
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            raise ValueError(f"Could not fetch URL: {url}")

        raw = trafilatura.extract(
            downloaded,
            include_metadata=True,
            output_format="json",
            with_metadata=True,
        )
        if not raw:
            raise ValueError("Could not extract content from the page.")

        data = json.loads(raw)
        title = data.get("title") or url
        text = data.get("text") or data.get("raw_text") or ""
        if not text.strip():
            raise ValueError("Extracted article text is empty.")

        author = data.get("author") or ""
        publish_date = data.get("date") or _today()
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        doc_id = f"art_{_url_hash(url)[:16]}"

        date_slug = publish_date[:10] if publish_date else _today()
        basename = f"{date_slug}_{slugify(title)}"
        art_dir = ROOT / "articles"
        txt_path = art_dir / f"{basename}.txt"
        json_path = art_dir / f"{basename}.json"

        file_meta = {
            "type": "article",
            "title": title,
            "source": url,
            "author": author,
            "publish_date": date_slug,
            "domain": domain,
        }
        txt_path.write_text(text)
        json_path.write_text(json.dumps(file_meta, indent=2, ensure_ascii=False))

        chroma_meta = {
            **file_meta,
            "file_path": str(txt_path),
            "created_at": _today(),
        }
        self._upsert(doc_id, text, chroma_meta, text, str(txt_path))

        # Check if it was a duplicate
        status = "saved"
        existing = self._col.get(ids=[doc_id])
        if len(existing["ids"]) > 0:
            status = "saved"

        return {"status": status, "title": title, "file_path": str(txt_path)}

    def add_pdf(self, file_path: str | Path) -> dict:
        """Extract text from a PDF and add it to the KB."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        try:
            with pdfplumber.open(file_path) as pdf:
                pages_text = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages_text.append(t)
                text = "\n\n".join(pages_text)
        except Exception as e:
            raise ValueError(f"Could not read PDF (may be encrypted): {e}")

        if not text.strip():
            raise ValueError("PDF appears to be empty or image-only.")

        title = file_path.stem.replace("-", " ").replace("_", " ").title()
        slug = slugify(file_path.stem)
        doc_id = f"pdf_{slug}"

        pdf_dir = ROOT / "pdfs"
        txt_path = pdf_dir / f"{slug}.txt"
        json_path = pdf_dir / f"{slug}.json"

        file_meta = {
            "type": "pdf",
            "title": title,
            "source": file_path.name,
        }
        txt_path.write_text(text)
        json_path.write_text(json.dumps(file_meta, indent=2, ensure_ascii=False))

        chroma_meta = {
            **file_meta,
            "file_path": str(txt_path),
            "created_at": _today(),
            "publish_date": "",
            "channel": "",
        }
        self._upsert(doc_id, text, chroma_meta, text, str(txt_path))

        return {"status": "saved", "title": title, "file_path": str(txt_path)}

    def add_note(self, title: str, content: str, tags: list[str]) -> dict:
        """Save a personal note to the KB."""
        if not title.strip():
            raise ValueError("Note title cannot be empty.")
        if not content.strip():
            raise ValueError("Note content cannot be empty.")

        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        date_str = now.strftime("%Y-%m-%d")
        doc_id = f"note_{timestamp}"

        basename = f"{date_str}_{slugify(title)}"
        notes_dir = ROOT / "notes"
        txt_path = notes_dir / f"{basename}.txt"
        json_path = notes_dir / f"{basename}.json"

        tags_str = ", ".join(t.strip() for t in tags if t.strip())
        file_meta = {
            "type": "note",
            "title": title,
            "tags": tags_str,
            "created_at": now.isoformat(),
        }
        txt_path.write_text(content)
        json_path.write_text(json.dumps(file_meta, indent=2, ensure_ascii=False))

        chroma_meta = {
            "type": "note",
            "title": title,
            "source": "",
            "tags": tags_str,
            "publish_date": date_str,
            "channel": "",
            "file_path": str(txt_path),
            "created_at": now.isoformat(),
        }
        self._upsert(doc_id, content, chroma_meta, content, str(txt_path))

        return {"status": "saved", "title": title, "file_path": str(txt_path)}

    # ------------------------------------------------------------------
    # Search and retrieval
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        n_results: int = 6,
        content_type: str | None = None,
    ) -> list[dict]:
        """Semantic search over the KB. Optionally filter by content_type."""
        total = self._col.count()
        if total == 0:
            return []

        n = min(n_results, total)
        kwargs: dict = {"query_texts": [query], "n_results": n}
        if content_type:
            kwargs["where"] = {"type": {"$eq": content_type}}

        results = self._col.query(**kwargs)
        if not results["ids"] or not results["ids"][0]:
            return []

        output = []
        for i, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            distance = results["distances"][0][i] if results.get("distances") else None
            content = self._load_content(meta.get("file_path", ""))
            output.append({
                "id": doc_id,
                "type": meta.get("type", ""),
                "title": meta.get("title", ""),
                "source": meta.get("source", ""),
                "file_path": meta.get("file_path", ""),
                "content": content,
                "metadata": meta,
                "distance": distance,
            })
        return output

    def get_all(self, content_type: str | None = None) -> list[dict]:
        """Return all documents, optionally filtered by type, newest first."""
        total = self._col.count()
        if total == 0:
            return []

        kwargs: dict = {}
        if content_type:
            kwargs["where"] = {"type": {"$eq": content_type}}

        results = self._col.get(include=["metadatas"], **kwargs)
        if not results["ids"]:
            return []

        output = []
        for i, doc_id in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            output.append({
                "id": doc_id,
                "type": meta.get("type", ""),
                "title": meta.get("title", ""),
                "source": meta.get("source", ""),
                "file_path": meta.get("file_path", ""),
                "content": "",
                "metadata": meta,
                "distance": None,
            })

        # Sort by created_at descending
        def _sort_key(d: dict) -> str:
            return d["metadata"].get("created_at") or d["metadata"].get("publish_date") or ""

        output.sort(key=_sort_key, reverse=True)
        return output

    def rebuild_index(self) -> int:
        """Clear ChromaDB and re-import everything from disk."""
        self._client.delete_collection("kb")
        ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self._col = self._client.get_or_create_collection(
            name="kb",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        self._import_existing()
        return self._col.count()

    def count_by_type(self) -> dict:
        """Return counts per content type."""
        counts: dict[str, int] = {"youtube": 0, "article": 0, "pdf": 0, "note": 0, "total": 0}
        total = self._col.count()
        if total == 0:
            counts["total"] = 0
            return counts

        results = self._col.get(include=["metadatas"])
        for meta in results["metadatas"]:
            t = meta.get("type", "")
            if t in counts:
                counts[t] += 1
        counts["total"] = total
        return counts

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _upsert(
        self,
        doc_id: str,
        content_preview: str,
        metadata: dict,
        full_content: str,
        file_path: str,
    ) -> None:
        preview = content_preview[:1500]
        # Ensure all metadata values are strings (ChromaDB requirement)
        safe_meta = {k: str(v) if v is not None else "" for k, v in metadata.items()}
        safe_meta["file_path"] = file_path
        self._col.upsert(
            ids=[doc_id],
            documents=[preview],
            metadatas=[safe_meta],
        )

    def _import_existing(self) -> None:
        """Scan ROOT recursively for .json files and import any not yet indexed."""
        existing_ids = set(self._col.get()["ids"])

        for json_path in sorted(ROOT.rglob("*.json")):
            # Skip ChromaDB internal files
            if ".chromadb" in json_path.parts:
                continue
            txt_path = json_path.with_suffix(".txt")
            if not txt_path.exists():
                continue

            try:
                meta = json.loads(json_path.read_text())
            except (json.JSONDecodeError, OSError):
                continue

            content_type = meta.get("type", "youtube")

            # Determine doc_id
            if content_type == "youtube" or "video_id" in meta:
                video_id = meta.get("video_id")
                if not video_id:
                    video_id = json_path.stem
                doc_id = f"yt_{video_id}"
                content_type = "youtube"
            elif content_type == "article":
                source = meta.get("source", "")
                doc_id = f"art_{_url_hash(source)[:16]}" if source else f"art_{json_path.stem}"
            elif content_type == "pdf":
                doc_id = f"pdf_{slugify(json_path.stem)}"
            elif content_type == "note":
                # Use stem as timestamp proxy
                doc_id = f"note_{json_path.stem}"
            else:
                doc_id = f"yt_{json_path.stem}"
                content_type = "youtube"

            if doc_id in existing_ids:
                continue

            try:
                content = txt_path.read_text()
            except OSError:
                continue

            chroma_meta = {
                "type": content_type,
                "title": meta.get("title") or json_path.stem,
                "source": meta.get("url") or meta.get("source") or "",
                "channel": meta.get("channel") or "",
                "publish_date": meta.get("publish_date") or "",
                "tags": meta.get("tags") or "",
                "file_path": str(txt_path),
                "created_at": meta.get("created_at") or meta.get("publish_date") or "",
            }
            self._upsert(doc_id, content, chroma_meta, content, str(txt_path))

    def _load_content(self, file_path: str) -> str:
        if not file_path:
            return ""
        p = Path(file_path)
        if p.exists():
            try:
                return p.read_text()
            except OSError:
                return ""
        return ""

    @staticmethod
    def _fetch_yt_metadata(url: str) -> dict:
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        upload_date = info.get("upload_date")
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

    @staticmethod
    def _fetch_yt_transcript(video_id: str) -> str:
        segments = YouTubeTranscriptApi().fetch(video_id)
        parts = [s.text.strip() for s in segments if s.text and s.text.strip()]
        return re.sub(r"\s+", " ", " ".join(parts)).strip()
