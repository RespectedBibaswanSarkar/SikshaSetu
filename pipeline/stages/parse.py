"""Stage: parse — turn fetched files into units with asset metadata (already done in fetch)."""
from pipeline import state


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        for tier, a in u["assets"].items():
            if isinstance(a, dict) and "tier" not in a:
                a["tier"] = tier
        u["id"] = u["id"]
        u.setdefault("segments", [])
        u.setdefault("concepts", [])
        u.setdefault("problems", [])
    state.mark(slug, "parse", units=len(st["units"]))
    return True
