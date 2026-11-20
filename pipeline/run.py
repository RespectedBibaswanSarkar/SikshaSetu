#!/usr/bin/env python3
"""SikshaSetu pipeline runner: python -m pipeline.run [--course X|--all] [--stage S] [--resume]"""
import argparse
import importlib
import sys

from pipeline.seed_courses import slugs

STAGES = ["resolve", "fetch", "parse", "transcode", "transcripts", "segment",
          "map", "questions", "package", "install"]


def main():
    ap = argparse.ArgumentParser(description="SikshaSetu pipeline")
    ap.add_argument("--course", default=None, help="course slug")
    ap.add_argument("--all", action="store_true", help="run all seed courses (default)")
    ap.add_argument("--stage", default=None, help=f"only run this stage: {', '.join(STAGES)}")
    ap.add_argument("--resume", action="store_true", help="skip stages already done")
    a = ap.parse_args()
    ok = True
    for entry in slugs(a.course if not a.all else None):
        slug = entry["slug"]
        for s in STAGES:
            if a.stage and a.stage != s:
                continue
            mod = importlib.import_module(f"pipeline.stages.{s}")
            if not mod.run(slug, resume=a.resume):
                print(f"[FAIL] {slug}::{s}")
                ok = False
                break
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
