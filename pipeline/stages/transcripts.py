"""Stage: transcripts — YouTube auto-captions via yt-dlp (official captions, machine:true);
else faster-whisper transcription of the decoded audio (marked machine:true).
"""
import time
from pathlib import Path

from pipeline import state
from pipeline.stages.fetch import sha256_of

VOICE_MODEL = "base"


def _get(url, timeout=30):
    import time
    import requests
    for i in range(5):
        try:
            r = requests.get(url, timeout=timeout, headers={"User-Agent": "SikshaSetu-Transcript/1.0"})
            if r.status_code == 429:
                time.sleep(2 * i + 1)
                continue
            r.raise_for_status()
            return r.text
        except Exception:
            time.sleep(2 * i + 1)
    return None


def _fetch_sub(url, ext):
    """Fetch a caption file and return a VTT string (or None if not usable)."""
    import re
    import xml.etree.ElementTree as ET
    if ext == "m3u8":
        txt = _get(url)
        if not txt:
            return None
        vtts = [l.strip() for l in txt.splitlines() if l.strip().endswith(".vtt") or l.strip().endswith(".vtt?cdn=translate")]
        if not vtts:
            return None
        chunks = []
        for u in vtts[:30]:
            part = _fetch_sub(u, "vtt")
            if part:
                chunks.append(part)
        return "\n".join(chunks) if chunks else None
    txt = _get(url)
    if txt is None:
        return None
    if ext == "vtt":
        return txt if "-->" in txt else None
    if ext == "srv1":
        cues = []
        try:
            root = ET.fromstring(txt)
            for p in root.iter():
                t = (p.text or "").strip()
                if t:
                    cues.append((float(p.get("t", 0) or 0), float(p.get("d", 0) or 0), t))
        except Exception:
            return None
        return cues
    if ext == "json3":
        import json
        try:
            doc = json.loads(txt)
            cues = []
            for ev in doc.get("events", []):
                start_ms = ev.get("tStartMs", 0) / 1000
                dur = ev.get("dDurationMs", 0) / 1000
                text = " ".join(s.get("tText", "") for s in ev.get("segs", []))
                if text.strip():
                    cues.append((start_ms, dur, text))
            return cues
        except Exception:
            return None
    return None


def _cues_to_vtt(cues):
    def fmt(s):
        h, rem = divmod(s, 3600); m, sec = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}".replace(".", ",")
    parts, i = ["WEBVTT\n"], 1
    for s, d, t in cues:
        parts.append(f"{i}\n{fmt(s)} --> {fmt(s + d)}\n{t}\n")
        i += 1
    return "\n".join(parts)


def grab_sub(v, out):
    """Official auto-captions via yt-dlp extract_info + direct fetch (m3u8 playlists handled)."""
    import yt_dlp
    vid = v.get("yt_id")
    if not vid:
        return False
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    except Exception:
        info = None
    cues = []
    if info:
        for key in ("automatic_captions", "subtitles"):
            for entry in (info.get(key) or {}).values():
                for x in entry:
                    r = _fetch_sub(x.get("url", ""), x.get("ext", ""))
                    if isinstance(r, list):
                        cues.extend(r)
                    elif isinstance(r, str) and cues is not None:
                        if cues and not isinstance(cues, str):
                            pass
                        cues = ["__vtt__"] + ([r] if isinstance(r, str) else cues)
                if cues:
                    break
            if cues:
                break
    if cues:
        if cues[0] == "__vtt__":
            out.write_text(cues[1], encoding="utf-8")
        else:
            out.write_text(_cues_to_vtt(cues), encoding="utf-8")
        return True
    return False


def whisper_vtt(video_path, out_vtt):
    from faster_whisper import WhisperModel
    model = WhisperModel(VOICE_MODEL, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(video_path), vad_filter=True)
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(f"{i}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{seg.text.strip()}\n")
    out_vtt.write_text("WEBVTT\n\n" + "\n".join(lines), encoding="utf-8")
    return True


def fmt_ts(t):
    t = max(0.0, float(t))
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        p = u["assets"].get("transcript_vtt")
        if p and Path(p["path"]).exists():
            continue
        v = u["assets"].get("video_360p")
        if not v:
            continue
        out = Path(v["path"]).parent / f"{Path(v['path']).stem}_transcript.vtt"
        used_machine = grab_sub(v, out)
        if not used_machine:
            whisper_vtt(Path(v["path"]), out)
        u["assets"]["transcript_vtt"] = {"path": str(out), "tier": "transcript_vtt",
                                         "machine_generated": True, "reviewed": False,
                                         "sha256": sha256_of(out), "size": out.stat().st_size}
        print(f"[transcripts] {u['id']} ({'yt-auto-captions' if used_machine else 'whisper'})")
    state.save(slug, st)
    state.mark(slug, "transcripts", units=len(st["units"]))
    return True
