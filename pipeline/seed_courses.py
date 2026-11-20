"""Pinned seed courses (pipeline/seed_courses.yaml → importable list)."""
from pathlib import Path
import yaml

def load():
    p = Path(__file__).parent / "seed_courses.yaml"
    out = []
    for c in yaml.safe_load(p.read_text())["courses"]:
        c["slug"] = str(c["slug"])
        c["fallback_slug"] = str(c["fallback_slug"])
        out.append(c)
    return out

def slugs(course=None):
    cs = load()
    if course:
        return [c for c in cs if str(c["slug"]) == str(course) or str(c["fallback_slug"]) == str(course)]
    return cs
