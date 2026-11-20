"""Stage: resolve — MIT OCW course page meta + units; lecture videos from YouTube (yt-dlp).

Notes/problem sets come from OCW-hosted PDFs where exposed; MIT OCW pages are
Angular apps, so units with OCW assets are gathered from linked resource pages
(best effort), and missing notes are generated from the YouTube video
descriptions/transcripts (see parse/transcripts stages).
"""
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from pipeline import state
from pipeline.seed_courses import slugs

UA = {"User-Agent": "SikshaSetu-Pipeline/1.0 (mit-ocw-resolver)"}


def get(url, timeout=30):
    r = requests.get(url, timeout=timeout, headers=UA)
    r.raise_for_status()
    return r.text


def course_meta(soup, url, slug):
    title = soup.title.text.strip() if soup.title else "Untitled"
    term = urlparse(url).path.strip("/").split("/")[-1].replace("-", " ")
    return {"slug": slug, "title": title, "term": term, "ocw_url": url,
            "license": "CC BY-NC-SA 4.0",
            "attribution": {"course_page": url, "license": "CC BY-NC-SA",
                            "date_accessed": __import__("datetime").date.today().isoformat()}}


def asset_kind(url):
    u = url.lower()
    if any(u.endswith(x) for x in (".vtt", ".vtt.txt")):
        return "transcript_vtt"
    if "problem" in u and u.endswith(".pdf"):
        return "problem_set"
    if u.endswith(".pdf") and any(k in u for k in ("note", "syllabus", "reading")):
        return "notes_pdf"
    if u.endswith(".pdf"):
        return "solutions"
    return None


def ocw_units(meta):
    """Units with OCW-hosted assets (notes/problem sets) from the course page."""
    units = []
    try:
        soup = BeautifulSoup(get(meta["ocw_url"]), "html.parser")
    except Exception:
        soup = BeautifulSoup("", "html.parser")
    for a in soup.find_all("a", href=True):
        href = urljoin(meta["ocw_url"], a["href"])
        kind = asset_kind(href)
        if kind and urlparse(href).netloc.endswith("mit.edu"):
            units.append({"id": f"{meta['slug']}/oc{len(units)+1:02d}",
                          "title": (a.get_text() or "OCW asset")[:60],
                          "ocw_url": meta["ocw_url"],
                          "assets": {kind: href}})
    return units


def yt_units(meta, limit=30):
    """Lecture units from the MIT OCW YouTube channel via yt-dlp search (top hits)."""
    import yt_dlp
    ydl = yt_dlp.YoutubeDL({"quiet": True, "flat_playlist": True, "extract_flat": True})
    entries = []
    for q in (f"mitocw {meta['slug']}", f"mitocw {meta['slug']} lecture"):
        info = ydl.extract_info(f"ytsearch:{q}", download=False) or {}
        entries += [e for e in info.get("entries") or [] if e.get("id")]
    out = []
    seen = set()
    for e in entries:
        if not e.get("id") or e["id"] in seen:
            continue
        seen.add(e["id"])
        out.append({"id": f"{meta['slug']}/u{len(out)+1:02d}",
                    "title": (e.get("title") or f"Unit {len(out)+1}").strip(),
                    "ocw_url": e.get("webpage_url"), "yt_id": e.get("id"),
                    "assets": {"video_360p": e["id"]},
                    "desc": (e.get("description") or "")[:600]})
        if len(out) >= limit:
            break
    return out


def run(slug, resume=False):
    if resume and state.stage_done(slug, "resolve"):
        return True
    entry = slugs(slug)[0]
    soup = BeautifulSoup(get(entry["ocw_url"]), "html.parser")
    meta = course_meta(soup, entry["ocw_url"], entry["slug"])
    units = yt_units(meta)
    ocw = ocw_units(meta)
    for u, o in zip(units, ocw):
        u["assets"].update(o["assets"])
    missing = [u["id"] for u in units if not any(k in u["assets"] for k in ("video_360p", "notes_pdf", "problem_set"))]
    if not units:
        raise RuntimeError(f"course {slug}: no lecture videos found (YouTube search for '{meta['title']} {meta['term']}' empty)")
    if missing:
        print(f"[resolve] warning: {slug}: units without video yet: {missing[:5]}")
    state.mark(slug, "resolve", meta=meta, units=units)
    print(f"[resolve] {slug}: {len(units)} units from YouTube search; ocw notes/problems: {sum(bool(o['assets']) for o in ocw)}")
    return True
