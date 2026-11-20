"""Pipeline state manager: pipeline/state/<slug>.json — idempotent stage tracking."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def state_file(slug: str) -> Path:
    d = ROOT / "pipeline" / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{slug}.json"


def load(slug: str) -> dict:
    f = state_file(slug)
    st = json.loads(f.read_text()) if f.exists() else {"slug": slug, "stages": {}}
    r = st["stages"].get("resolve") or {}
    if "units" not in st and r.get("units"):
        st["units"] = r["units"]
    if "meta" not in st and r.get("meta"):
        st["meta"] = r["meta"]
    return st


def save(slug: str, data: dict) -> None:
    state_file(slug).write_text(json.dumps(data, indent=1, default=str))


def stage_done(slug: str, stage: str) -> bool:
    return stage in load(slug).get("stages", {})


def mark(slug: str, stage: str, **res) -> None:
    st = load(slug)
    st.setdefault("stages", {})[stage] = res
    save(slug, st)
