"""Stage: install-to-app — copy catalog/concepts/questions + a short sample lecture
into client/public/offline-pack so the PWA launches offline out of the box.
"""
import shutil
from pathlib import Path

from pipeline import state

STORE = Path(__file__).resolve().parent.parent.parent / "pipeline" / "store"
PACK = Path(__file__).resolve().parent.parent.parent / "client" / "public" / "offline-pack"


def run(slug, resume=False):
    for f in ("catalog.json", "concepts.json", "questions.json", "version.json"):
        src = STORE / f
        if src.exists():
            shutil.copy(src, PACK / f)
    # copy one small 360p sample lecture + transcript
    sample_dir = PACK / "sample"
    sample_dir.mkdir(exist_ok=True)
    import json
    man = json.loads((STORE / f"{slug}.manifest.json").read_text())
    done = 0
    for u in man["units"][:1]:
        for tier in ("video_360p", "transcript_vtt", "notes_pdf", "audio_only"):
            a = u["assets"].get(tier)
            if a and a.get("path") and Path(a["path"]).exists() and a.get("size", 0) < 25 * 1024 * 1024:
                shutil.copy(a["path"], sample_dir / Path(a["path"]).name)
                done += 1
                if done >= 2:
                    break
        if done >= 2:
            break
    state.mark(slug, "install", sample_files=done)
    return True
