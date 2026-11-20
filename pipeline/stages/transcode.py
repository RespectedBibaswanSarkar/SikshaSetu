"""Stage: transcode — ffmpeg: 360p H264/AAC faststart, audio-only Opus, poster."""
import subprocess
from pathlib import Path

from pipeline import state


def ff(args):
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg {' '.join(args[:4])} failed: {r.stderr[:400]}")


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        v = u["assets"].get("video_360p")
        if not v or not Path(v["path"]).exists():
            continue
        inp = v["path"]
        d = Path(inp).parent
        # 360p H.264/AAC faststart
        out = d / f"{u['id']}_video_360p.mp4"
        ff(["-i", inp, "-vf", "scale=min(640,iw):min(360,ih)" , "-c:v", "libx264",
            "-preset", "veryfast", "-crf", "28", "-c:a", "aac", "-b:a", "96k",
            "-movflags", "+faststart", str(out)])
        u["assets"]["video_360p"] = {**v, "path": str(out), "tier": "video_360p"}
        # audio-only Opus
        aout = d / f"{u['id']}_audio_only.opus"
        ff(["-i", inp, "-vn", "-c:a", "libopus", "-b:a", "128k", str(aout)])
        u["assets"]["audio_only"] = {"path": str(aout), "sha256": __import__("pipeline.stages.fetch", fromlist=["sha256_of"]).sha256_of(aout),
                                     "size": aout.stat().st_size, "tier": "audio_only",
                                     "machine_generated": v.get("machine_generated", True), "reviewed": False}
        # poster from first frame
        pout = d / f"{u['id']}_poster.jpg"
        ff(["-ss", "0.5", "-i", inp, "-vframes", "1", "-q:v", "3", str(pout)])
        u["assets"]["poster"] = {"path": str(pout), "sha256": __import__("pipeline.stages.fetch", fromlist=["sha256_of"]).sha256_of(pout),
                                 "size": pout.stat().st_size, "tier": "poster",
                                 "machine_generated": True, "reviewed": False}
    state.mark(slug, "transcode", units=len(st["units"]))
    return True
