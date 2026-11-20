"""make verify — pipeline checks: every unit has video + notes + transcript + >=1 concept;
hashes match; no dangling refs; concept graph acyclic; prints per-tier sizes."""
import json
from pathlib import Path

from pipeline import state
from pipeline.seed_courses import load

STORE = Path(__file__).resolve().parent / "store"


def check(slug, problems):
    man = json.loads((STORE / f"{slug}.manifest.json").read_text())
    concepts = json.loads((STORE / "concepts.json").read_text())
    for u in man["units"]:
        for tier in ("video_360p", "notes_pdf", "transcript_vtt"):
            if tier not in u["assets"]:
                problems.append(f"{slug} {u['id']}: missing {tier}")
        import hashlib
        for tier, a in u["assets"].items():
            if not (STORE / a["path"]).exists():
                problems.append(f"{slug} {u['id']}: dangling {tier}")
                continue
            if hashlib.sha256((STORE / a["path"]).read_bytes()).hexdigest() != a["sha256"]:
                problems.append(f"{slug} {u['id']}: sha mismatch {tier}")
    # acyclic concept graph
    by_id = {c["id"]: c for c in concepts}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {}
    def dfs(nid):
        color[nid] = GRAY
        for p in by_id.get(nid, {}).get("prerequisites", []):
            if color.get(p, WHITE) == GRAY:
                problems.append(f"cycle involving {p}")
            elif color.get(p, WHITE) == WHITE:
                dfs(p)
        color[nid] = BLACK
    for c in concepts:
        if color.get(c["id"], WHITE) == WHITE:
            dfs(c["id"])
    return man


def main():
    problems = []
    sizes = {}
    for entry in load():
        slug = entry["slug"]
        st = state.load(slug)
        if "package" not in st.get("stages", {}):
            problems.append(f"{slug}: not packaged (run make seed)")
            continue
        man = check(slug, problems)
        for u in man["units"]:
            for tier, a in u["assets"].items():
                sizes[tier] = sizes.get(tier, 0) + a["size"]
    if problems:
        print("VERIFY FAILED:")
        for p in problems[:30]:
            print("  -", p)
        return 1
    print("VERIFY OK")
    for t, sz in sorted(sizes.items()):
        print(f"  {t:16s} {sz/2**20:8.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
