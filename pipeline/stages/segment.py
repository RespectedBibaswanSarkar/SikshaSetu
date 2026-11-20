"""Stage: segment — parse transcript VTT into topic segments with timestamps."""
import re
from pathlib import Path

from pipeline import state


CUE_RE = re.compile(r"(\d{2}:\d{2}:\d{2}[.,]\d{3}) --> (\d{2}:\d{2}:\d{2}[.,]\d{3})")
TAG_RE = re.compile(r"<[^>]*>")


def to_sec(ts):
    ts = ts.replace(",", ".")
    h, m, rest = ts.split(":")
    s, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + float(s) + float(ms) / 1000


def parse_vtt(text):
    """Parse VTT with YouTube-style inline tags/timestamps."""
    cues = []
    for m in CUE_RE.finditer(text):
        start, end = to_sec(m.group(1)), to_sec(m.group(2))
        block = text[m.end():]
        nxt = CUE_RE.search(block)
        chunk = block[:nxt.start()] if nxt else block
        t = " ".join(TAG_RE.sub("", line).strip() for line in chunk.splitlines() if line.strip())
        t = " ".join(t.split())
        if t:
            cues.append({"start": start, "end": end, "text": t})
    return cues


def segment_unit(unit, cues):
    segs, cur = [], []
    for c in cues:
        if cur and c["start"] - cur[-1]["end"] > 2.0:
            segs.append(cur)
            cur = []
        if len(cur) > 40:
            segs.append(cur)
            cur = []
        cur.append(c)
    if cur:
        segs.append(cur)
    out = []
    for i, s in enumerate(segs, 1):
        out.append({"id": f"{unit['id']}/s{i:02d}", "unit_id": unit["id"],
                    "start": s[0]["start"], "end": s[-1]["end"],
                    "title": f"{unit['title']} · seg {i}",
                    "text": " ".join(x["text"] for x in s)})
    return out


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        tp = u["assets"].get("transcript_vtt", {}).get("path")
        if not tp or not Path(tp).exists():
            continue
        cues = parse_vtt(Path(tp).read_text(encoding="utf-8", errors="replace"))
        segs = segment_unit(u, cues)
        u.setdefault("segments", []).extend(segs)
    state.save(slug, st)
    state.mark(slug, "segment", units=len(st["units"]))
    return True
