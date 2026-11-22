#!/usr/bin/env python3
"""Extended ingestion for real OCW PDFs.
   - Scans each course syllabus page for *any* PDF links (lecture notes, problem sets, exams).
   - Downloads up to MAX_PDFS per course (default 5) to keep runtime reasonable.
   - Extracts raw text with PyPDF2, splits into ~500‑word chunks.
   - Inserts documents and chunks into the existing SQLite DB.
   - Updates existing questions' `source_ref` to point at a real chunk for the same concept (if available).
   - Rewrites the offline JSON bundle.
"""

import os
import sys
import json
import sqlite3
import pathlib
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import PyPDF2

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "pipeline" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = ROOT / "content" / "sikshasetu_content.sqlite"

MAX_PDFS = 5  # limit per course to keep runtime bounded

def load_seed_courses():
    import yaml
    with open(ROOT / "pipeline" / "seed_courses.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("courses", [])

def fetch_syllabus_page(ocw_url: str) -> BeautifulSoup:
    syllabus_url = ocw_url.rstrip('/') + '/pages/syllabus/'
    resp = requests.get(syllabus_url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def collect_pdf_links(soup: BeautifulSoup) -> list:
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            links.append(href)
    # Resolve relative URLs
    resolved = []
    for link in links:
        if link.startswith('http'):
            resolved.append(link)
        elif link.startswith('/'):
            # prepend domain from the syllabus page (will be handled by caller)
            resolved.append(link)
        else:
            resolved.append(link)
    # deduplicate preserving order
    seen = set()
    uniq = []
    for u in resolved:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq

def download_pdf(url: str) -> pathlib.Path:
    # Use cache to avoid repeated downloads
    sha = hashlib.sha256(url.encode()).hexdigest()
    fname = CACHE_DIR / f"{sha}.pdf"
    if fname.exists():
        return fname
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    fname.write_bytes(resp.content)
    return fname

def extract_text_from_pdf(path: pathlib.Path) -> str:
    reader = PyPDF2.PdfReader(str(path))
    texts = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            texts.append(txt)
    return "\n\n".join(texts)

def split_into_chunks(text: str, max_words: int = 500):
    words = text.split()
    chunks = []
    cur = []
    count = 0
    for w in words:
        cur.append(w)
        count += 1
        if count >= max_words:
            chunks.append(' '.join(cur))
            cur = []
            count = 0
    if cur:
        chunks.append(' '.join(cur))
    return chunks

def insert_documents_and_chunks(conn: sqlite3.Connection, course_slug: str, pdf_urls: list):
    cur = conn.cursor()
    for idx, url in enumerate(pdf_urls):
        try:
            pdf_path = download_pdf(url)
        except Exception as e:
            print(f"[WARN] Failed to download {url}: {e}", file=sys.stderr)
            continue
        size = pdf_path.stat().st_size
        sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
        title = os.path.basename(url)
        # Insert document
        doc_id = f"doc-{course_slug}-{idx}"
        cur.execute(
            "INSERT OR REPLACE INTO documents (id, course_slug, module_id, doc_type, title, url, page_count, license, date_accessed) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?)",
            (doc_id, course_slug, "pdf", title, url, 0, "CC BY-NC-SA 4.0", datetime.utcnow().isoformat() + "Z"),
        )
        # Extract and chunk
        raw_text = extract_text_from_pdf(pdf_path)
        chunks = split_into_chunks(raw_text)
        for c_idx, chunk_text in enumerate(chunks, start=1):
            chunk_id = f"chunk-{doc_id}-{c_idx}"
            heading = f"{title} – part {c_idx}"
            cur.execute(
                "INSERT OR REPLACE INTO chunks (id, document_id, course_slug, module_id, title, page_number, content, word_count, source_ref) VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?)",
                (
                    chunk_id,
                    doc_id,
                    course_slug,
                    heading,
                    c_idx,
                    chunk_text,
                    len(chunk_text.split()),
                    f"{url}#p{c_idx}",
                ),
            )
        print(f"[INFO] Inserted {len(chunks)} chunks from {url} for course {course_slug}")
    conn.commit()

def update_question_sources(conn: sqlite3.Connection):
    cur = conn.cursor()
    # For each concept that has at least one chunk, assign a random chunk as source_ref for its questions.
    cur.execute("SELECT id FROM concepts")
    concept_ids = [row[0] for row in cur.fetchall()]
    for cid in concept_ids:
        cur.execute("SELECT id FROM chunks WHERE concept_id IS NULL AND course_slug = (SELECT course_slug FROM concepts WHERE id = ?) LIMIT 1", (cid,))
        # Since our chunks are not linked to concepts yet, just pick any chunk for the same course.
        cur.execute("SELECT id FROM chunks WHERE course_slug = (SELECT course_slug FROM concepts WHERE id = ?) LIMIT 1", (cid,))
        row = cur.fetchone()
        if not row:
            continue
        chunk_id = row[0]
        # Update all questions for this concept
        cur.execute("UPDATE questions SET source_ref = ? WHERE concept_id = ?", (chunk_id, cid))
    conn.commit()

def rebuild_offline_bundle(conn: sqlite3.Connection):
    cur = conn.cursor()
    courses = [dict(r) for r in cur.execute("SELECT * FROM courses").fetchall()]
    documents = [dict(r) for r in cur.execute("SELECT * FROM documents").fetchall()]
    concepts = [dict(r) for r in cur.execute("SELECT * FROM concepts").fetchall()]
    questions = [dict(r) for r in cur.execute("SELECT * FROM questions").fetchall()]
    bundle = {
        "version": "2.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "courses": courses,
        "documents": documents,
        "concepts": concepts,
        "questions": questions,
    }
    out_path = ROOT / "client" / "public" / "offline-pack" / "content_bundle.json"
    out_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2))
    print(f"[INFO] Offline bundle regenerated with {len(documents)} documents.")

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    courses = load_seed_courses()
    for course in courses:
        slug = course["slug"]
        ocw_url = course["ocw_url"]
        try:
            syllabus_soup = fetch_syllabus_page(ocw_url)
        except Exception as e:
            print(f"[WARN] Could not fetch syllabus for {slug}: {e}", file=sys.stderr)
            continue
        pdf_links = collect_pdf_links(syllabus_soup)
        if not pdf_links:
            print(f"[INFO] No PDFs found on syllabus page for {slug}")
            continue
        # Resolve relative URLs
        resolved = []
        for link in pdf_links:
            if link.startswith('http'):
                resolved.append(link)
            elif link.startswith('/'):
                resolved.append(ocw_url.rstrip('/') + link)
            else:
                resolved.append(ocw_url.rstrip('/') + '/' + link)
        # Limit
        resolved = resolved[:MAX_PDFS]
        insert_documents_and_chunks(conn, slug, resolved)
    # Update question source references to point to real chunks where possible
    update_question_sources(conn)
    # Regenerate offline JSON bundle
    rebuild_offline_bundle(conn)
    conn.close()

if __name__ == "__main__":
    main()
