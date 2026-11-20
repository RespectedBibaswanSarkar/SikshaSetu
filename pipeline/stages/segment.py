"""Stage: segment — parse transcript VTT into topic segments with timestamps."""
import re
from pathlib import Path

from pipeline import state


def parse_vtt(text):
    cues, cur = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            if cur:
                cues.append(cur)
                cur = []
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2},\d{3} --> ", line):
            ts = line.split(" --> ")
            cur = [to_sec(ts[0]), to_sec(ts[1]), []]
        elif cur and not re.match(r"^\d+$", line):
            cur[2].append(line)
    if cur:
        cues.append(cur)
    out = []
    for s, e, txt in cues:
        if txt:
            out.append({"start": s, "end": e, "text": " ".join(txt)})
    return out


def to_sec(ts):
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + float(s) + float(ms) / 1000


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
    state.mark(slug, "segment", units=len(st["units"]))
    return True
