"""Stage: fetch — download unit assets (OCW PDFs via requests; YouTube videos via yt-dlp).
Max 2 concurrent (rate limit per spec). Resume-friendly.
"""
import hashlib
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

from pipeline import state

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / "pipeline" / "cache"


def dl_http(url, dest, timeout=900):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    for _ in range(3):
        try:
            with requests.get(url, stream=True, timeout=timeout,
                              headers={"User-Agent": "SikshaSetu-Fetch/1.0"}) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        if chunk:
                            f.write(chunk)
            shutil.move(str(tmp), str(dest))
            return dest
        except Exception as e:
            print(f"[fetch] retry {url[:80]}: {e}")
    raise RuntimeError(f"failed {url}")


def dl_yt(vid, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    import glob
    import os
    import time
    import yt_dlp
    tmp = dest.parent / (dest.stem + ".part.mp4")
    before = {p for p in glob.glob(str(dest.parent / "*.mp4"))}
    opts = {"quiet": True, "noprogress": True, "no_warnings": True,
            "outtmpl": str(tmp), "merge_output_format": "mp4",
            "format": "bestvideo[height<=360]+bestaudio/worst",
            "concurrent_fragments": 1}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([vid])
    now = time.time()
    cands = [Path(p) for p in glob.glob(str(dest.parent / "*.mp4"))
             if now - os.path.getmtime(p) < 120 and os.path.getsize(p) > 1000]
    cands = [p for p in cands if p != dest]
    if cands:
        best = max(cands, key=lambda p: p.stat().st_size)
        shutil.move(str(best), str(dest))
        for c in cands:
            if c.exists() and c != dest:
                c.unlink()
    if not dest.exists() or dest.stat().st_size == 0:
        raise RuntimeError(f"yt download produced no file for {vid}")
    return dest


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        for tier, a in list(u["assets"].items()):
            if isinstance(a, dict) and a.get("path"):
                continue
            if isinstance(a, dict):  # url + maybe yt id
                url, vid = a.get("url"), a.get("path") or a.get("yt_id")
            else:
                url, vid = a, None
            if not isinstance(url, str) or not url.startswith("http"):
                continue
            dest = CACHE / slug / f"{u['id']}_{tier}{Path(urlparse(url).path).suffix}"
            dl_http(url, dest)
            u["assets"][tier] = {"path": str(dest), "url": url, "sha256": sha256_of(dest),
                                 "size": dest.stat().st_size, "tier": tier,
                                 "machine_generated": False, "reviewed": False}
        # YouTube videos: resolve id → download
        for tier in ("video_360p",):
            a = u["assets"].get(tier)
            if isinstance(a, str) and not a.startswith("http"):
                dest = CACHE / slug / f"{u['id']}_video_360p.mp4"
                dl_yt(a, dest)
                u["assets"][tier] = {"path": str(dest), "yt_id": a, "sha256": sha256_of(dest),
                                     "size": dest.stat().st_size, "tier": tier,
                                     "machine_generated": True, "reviewed": False}
    state.save(slug, st)
    state.mark(slug, "fetch", units=len(st["units"]))
    return True
