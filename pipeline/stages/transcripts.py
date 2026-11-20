"""Stage: transcripts — YouTube auto-captions (official, machine:true) via yt-dlp;
else faster-whisper transcription of the decoded audio (marked machine:true).
"""
import json
from pathlib import Path

import requests

from pipeline import state
from pipeline.stages.fetch import sha256_of

VOICE_MODEL = "base"  # change to "small" for better accuracy (slower)


def yt_subs(vid_or_url):
    """Return first English auto-caption VTT URL from the video."""
    import yt_dlp
    ydl = yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True})
    try:
        info = ydl.extract_info(vid_or_url, download=False) or {}
    except Exception:
        return None
    for lst in (info.get("automatic_captions") or {}).values():
        if lst and any(x.get("ext") == "vtt" for x in lst):
            for x in lst:
                if x.get("ext") == "vtt":
                    return x["url"]
    for lst in (info.get("subtitles") or {}).values():
        for x in lst:
            if x.get("ext") == "vtt":
                return x["url"]
    return None


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
        if u["assets"].get("transcript_vtt", {}).get("path"):
            continue
        v = u["assets"].get("video_360p")
        if not v:
            continue
        out = Path(v["path"]).parent / f"{u['id']}_transcript.vtt"
        used_machine = False
        url = v.get("yt_id") or v.get("url")
        sub_url = yt_subs(url) if url else None
        if sub_url:
            r = requests.get(sub_url, timeout=60)
            r.raise_for_status()
            out.write_text(r.text if r.text.startswith("WEBVTT") else "WEBVTT\n\n" + r.text, encoding="utf-8")
            used_machine = True
        else:
            whisper_vtt(Path(v["path"]), out)
        u["assets"]["transcript_vtt"] = {"path": str(out), "tier": "transcript_vtt",
                                         "machine_generated": used_machine, "reviewed": False,
                                         "sha256": sha256_of(out), "size": out.stat().st_size}
        print(f"[transcripts] {u['id']} ({'yt-auto-captions' if used_machine else 'whisper'})")
    state.mark(slug, "transcripts", units=len(st["units"]))
    return True
