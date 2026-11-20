"""Stage: package — content-addressed store + catalog.json / concepts.json /
questions.json / version.json / per-course manifest. Attribution kept per-asset.
"""
import json
import shutil
from pathlib import Path

from pipeline import state

STORE = Path(__file__).resolve().parent.parent.parent / "pipeline" / "store"


def package_course(st):
    slug = st["slug"]
    objs = STORE / "objects"
    objs.mkdir(parents=True, exist_ok=True)
    manifest = {"slug": slug, "meta": st["meta"], "units": []}
    for u in st["units"]:
        mu = {"id": u["id"], "title": u["title"], "ocw_url": u.get("ocw_url"),
              "assets": {}, "segments": u.get("segments", []),
              "concepts": u.get("concepts", [])}
        for tier, a in u["assets"].items():
            if isinstance(a, dict) and a.get("sha256") and a.get("path"):
                dst = objs / a["sha256"]
                if not dst.exists():
                    shutil.copy(a["path"], dst)
                mu["assets"][tier] = {k: a[k] for k in ("sha256", "size", "tier", "machine_generated", "reviewed")}
                mu["assets"][tier]["path"] = str(dst)
                mu["assets"][tier]["attribution"] = {"course": slug, "url": u.get("ocw_url") or a.get("url"),
                                                     "license": st["meta"]["license"]}
        manifest["units"].append(mu)
    (STORE / f"{slug}.manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def run(slug, resume=False):
    st = state.load(slug)
    m = package_course(st)
    allc = state.load(slug).get("concepts", [])
    allq = state.load(slug).get("questions", [])
    catalog = [state.load(s)["meta"] for s in {x["slug"] for x in [st]}]
    import yaml
    from pipeline.seed_courses import load
    (STORE / "catalog.json").write_text(json.dumps({"courses": load()}, indent=1), encoding="utf-8")
    (STORE / "concepts.json").write_text(json.dumps(allc, indent=1), encoding="utf-8")
    (STORE / "questions.json").write_text(json.dumps(allq, indent=1), encoding="utf-8")
    (STORE / "version.json").write_text(json.dumps({"content_version": "1", "seed_report": "pipeline/seed_report.md",
                                                    "courses": [x["slug"] for x in load()]}, indent=1), encoding="utf-8")
    state.mark(slug, "package", units=len(m["units"]), concepts=len(allc), questions=len(allq))
    return True
