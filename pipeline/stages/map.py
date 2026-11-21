"""Stage: map — build concepts.json (id, name, prerequisites, unit_refs, segment_refs).
Deterministic TF-IDF-free approach: top noun phrases per unit segment; prereqs link
to earlier units (DAG). Machine output: reviewed:false.
"""
import re
from collections import Counter

import yaml
from pathlib import Path
from pipeline import state
ROOT = Path(__file__).resolve().parent.parent.parent


def terms_of(text):
    words = re.findall(r"[a-z][a-z0-9]{2,}", text.lower())
    return words


def stopwords():
    return set("the of and a an to in on for is are was were be been this that these those it its its we you they he she the a by as with from or not no so if then when where why how what who whom whose which will would can could should may might must do does did have has had being able to of and the is it this in that for on with as by from at".split())


def _notes_for(unit, slug):
    """Generate a notes PDF from the unit's transcript segments (user's YouTube path)."""
    from pathlib import Path
    from pipeline.pdfwrite import write_notes_pdf
    lines, seen = [], set()
    for s in unit.get("segments", []):
        for sent in re.split(r"[.!?] +", s["text"]):
            t = sent.strip()[:100]
            if len(t) > 25 and t not in seen:
                seen.add(t)
                lines.append(t)
                if len(lines) >= 120:
                    break
        if len(lines) >= 120:
            break
    p = Path(state.load(slug)["units"][0].get("_notes_dir", "") ) / "" if False else None
    from pipeline.stages.fetch import CACHE
    p = CACHE / slug / f"{unit['id']}_notes.pdf"
    write_notes_pdf(p, f"{slug}: {unit['title']}", lines or ["Lecture notes (auto-generated from transcript)."])
    return p


def run(slug, resume=False):
    st = state.load(slug)
    for u in st["units"]:
        if not u["assets"].get("notes_pdf"):
            p = _notes_for(u, slug)
            from pipeline.stages.fetch import sha256_of
            u["assets"]["notes_pdf"] = {"path": str(p), "tier": "notes_pdf",
                                        "sha256": sha256_of(p), "size": p.stat().st_size,
                                        "machine_generated": True, "reviewed": False,
                                        "url": u.get("ocw_url"),
                                        "attribution": {"course": slug, "url": u.get("ocw_url"), "license": st.get("meta", {}).get("license", "CC BY-NC-SA")}}
    concepts = []
    for ui, u in enumerate(st["units"]):
        for s in u.get("segments", []):
            words = terms_of(s["text"])
            c = Counter(w for w in words if w not in stopwords())
            for name, _ in c.most_common(8):
                cid = f"{slug}/c-{name}"
                entry = next((c for c in concepts if c["id"] == cid), None)
                if not entry:
                    concepts.append({"id": cid, "name": name.replace("_", " ").title(),
                                     "prerequisites": [c["id"] for c in concepts[-8:]] or [],
                                     "unit_refs": [], "segment_refs": []})
                    entry = concepts[-1]
                entry["segment_refs"].append(s["id"])
                entry["unit_refs"].append(u["id"])
                if u["id"] not in entry["unit_refs"][:-1]:
                    pass
    # ensure acyclicity: prereqs always reference earlier-created concepts
    for c in concepts:
        c["prerequisites"] = [p for p in c["prerequisites"] if p != c["id"]][:3]
    cpath = ROOT.parent / "content" / slug / "concepts.yaml"
    if cpath.exists():
        concepts = yaml.safe_load(cpath.read_text())["concepts"]
    st["concepts"] = concepts
    state.save(slug, st)
    state.mark(slug, "map", concepts=len(concepts))
    st.setdefault("concepts", []).extend(concepts)
    state.save(slug, st)
    print(f"[map] {slug}: {len(concepts)} concepts")
    return True
