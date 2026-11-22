#!/usr/bin/env python3
"""Live smoke test: proves the dashboard is driven by the backend.
Usage:  python3 scripts/smoke_backend.py [http://localhost:8000]
Registers a fresh student, prints the ZERO-STATE dashboard, answers 16 questions
(10 right in concept A, 6 wrong in concept B), prints the dashboard again, then
takes a mock test. Exit code 1 if any check fails."""
import itertools, sys
import requests

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
API = BASE + "/api/learn"
ok = True


def check(name, cond, extra=""):
    global ok
    ok &= bool(cond)
    print(("PASS " if cond else "FAIL ") + name, extra)


def show(tag, d):
    s = d["stats"]
    print(f"\n[{tag}] progress={s['overall_progress']}% tests={s['tests_taken']} accuracy={s['accuracy']} "
          f"study={s['study_hours']}h streak={s['streak']} focus={s['focus_score']} answered={s['answered']}")
    print("   weak:", [w["name"] for w in d["weak_areas"]] or "none")
    print("   path:", [f"{p['label']}: {p['title']}" for p in d["learning_path"]])
    print("   next mock test:", d["next_mock_test"])
    print("   courses:", [(c["slug"], c["progress"]) for c in d["courses"]])


r = requests.get(BASE + "/api/health"); check("backend up", r.ok)
sid = requests.post(API + "/students", json={"name": "Smoke Test"}).json()["student_id"]
d0 = requests.get(f"{API}/students/{sid}/dashboard").json(); show("ZERO STATE", d0)
check("zero progress", d0["stats"]["overall_progress"] == 0 and d0["stats"]["answered"] == 0)
check("no fake accuracy/focus", d0["stats"]["accuracy"] is None and d0["stats"]["focus_score"] is None)

import sqlite3, json, pathlib
db = sqlite3.connect(pathlib.Path(__file__).resolve().parent.parent / "content" / "sikshasetu_content.sqlite")
rows = db.execute("select id, concept_id, options, answer_index from questions where course_slug='6.006'").fetchall()
by = {}
for qid, cid, opts, ai in rows:
    by.setdefault(cid, []).append((qid, json.loads(opts), ai))
cids = [c for c, q in by.items() if len(q) >= 4]
A, B = cids[0], cids[1]


def ans(cid, right, n):
    last = None
    for (qid, opts, ai), _ in zip(itertools.cycle(by[cid]), range(n)):
        good = opts[ai]
        bad = next((o for o in opts if o != good), "x")
        last = requests.post(f"{API}/students/{sid}/answer",
                             json={"question_id": qid, "choice": good if right else bad, "seconds": 25}).json()
    return last


a = ans(A, True, 10); b = ans(B, False, 6)
d1 = requests.get(f"{API}/students/{sid}/dashboard").json(); show("AFTER 16 ANSWERS", d1)
check("accuracy = 10/16 = 62", d1["stats"]["accuracy"] == 62, d1["stats"]["accuracy"])
check("progress rose", d1["stats"]["overall_progress"] > 0)
check("failed concept is a weak area", B in [w["concept_id"] for w in d1["weak_areas"]])
check("mastered concept is not weak", A not in [w["concept_id"] for w in d1["weak_areas"]])
check("path no longer says diagnostic", d1["learning_path"][0]["action"] != "diagnostic")
ans(B, True, 8)
d2 = requests.get(f"{API}/students/{sid}/dashboard").json(); show("AFTER REMEDIATION", d2)
check("weak area cleared after correct answers", B not in [w["concept_id"] for w in d2["weak_areas"]])

t = requests.post(f"{API}/students/{sid}/tests?course=6.006").json()
res = requests.post(f"{API}/students/{sid}/tests/{t['test_id']}/submit",
                    json={"answers": [{"question_id": q["question_id"], "choice": q["options"][0], "seconds": 12} for q in t["questions"]]}).json()
check("mock test graded", res["total"] == 15, f"score {res['score_pct']}%")
check("tests_taken incremented", res["dashboard"]["stats"]["tests_taken"] == 1)
print("\nANALYTICS bandit arms:", [(x["concept"], x["score"]) for x in requests.get(f"{API}/students/{sid}/analytics").json()["bandit_arms"][:3]])
print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED"); sys.exit(0 if ok else 1)
