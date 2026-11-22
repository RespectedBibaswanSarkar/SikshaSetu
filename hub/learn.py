"""SikshaSetu learning backend.

Event-sourced: every answer / test is stored as an event in hub.db; ALL dashboard
numbers are derived by replaying those events through the engine below
(BKT mastery + forgetting + Elo ability + LinUCB bandit).  Nothing is hardcoded.

Endpoints (all under /api/learn):
  POST /students                       register a student
  GET  /courses                        courses + concept/question counts
  GET  /students/{sid}/dashboard       everything the dashboard shows
  GET  /students/{sid}/next            next adaptive question (practice | diagnostic)
  POST /students/{sid}/answer          grade + update engine, returns live deltas
  POST /students/{sid}/tests           build a 15-question mock test
  POST /students/{sid}/tests/{tid}/submit
  GET  /students/{sid}/tests           history
  GET  /students/{sid}/analytics       mastery table, trends, bandit internals
  POST /students/{sid}/reset
  GET  /concepts/{cid}                 concept page: notes chunks + exercises
  GET  /search?q=                      full-text search over notes/exercises
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import random
import sqlite3
import time
import uuid
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from hub import db as hubdb

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DB = ROOT / "content" / "sikshasetu_content.sqlite"
router = APIRouter(prefix="/api/learn", tags=["learn"])

P_INIT, P_LEARN, P_SLIP, P_GUESS = 0.25, 0.15, 0.10, 0.20
WEAK_P, CLEAR_P, WEAK_MIN_ATTEMPTS = 0.5, 0.8, 3
D = 6  # LinUCB context dimension
ALPHA = 0.6
PRIOR_W = np.array([1.0, 0.4, 0.3, 0.2, 0.3, 0.0])


# ----------------------------------------------------------------- content
@lru_cache(maxsize=1)
def content() -> dict:
    con = sqlite3.connect(CONTENT_DB)
    con.row_factory = sqlite3.Row
    courses = {r["slug"]: dict(r) for r in con.execute("SELECT * FROM courses")}
    modules = {r["id"]: dict(r) for r in con.execute("SELECT * FROM modules")}
    concepts = {}
    for r in con.execute("SELECT * FROM concepts"):
        d = dict(r)
        d["prerequisites"] = json.loads(d.get("prerequisites") or "[]")
        concepts[d["id"]] = d
    for d in concepts.values():
        d["prerequisites"] = [p for p in d["prerequisites"] if p in concepts]
    dependents = defaultdict(list)
    for d in concepts.values():
        for p in d["prerequisites"]:
            dependents[p].append(d["id"])
    questions = {}
    by_concept = defaultdict(list)
    for r in con.execute("SELECT * FROM questions"):
        d = dict(r)
        d["options"] = json.loads(d["options"]) if isinstance(d["options"], str) else d["options"]
        if d["concept_id"] in concepts and d["options"]:
            questions[d["id"]] = d
            by_concept[d["concept_id"]].append(d["id"])
    con.close()
    return dict(courses=courses, modules=modules, concepts=concepts,
                dependents=dependents, questions=questions, by_concept=by_concept)


def reload_content():
    content.cache_clear()


# ----------------------------------------------------------------- storage
def _db():
    db = hubdb.connect()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS learn_students (id TEXT PRIMARY KEY, name TEXT, roll_no TEXT,
        courses TEXT, created REAL);
    CREATE TABLE IF NOT EXISTS learn_events (seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT UNIQUE,
        sid TEXT, ts REAL, type TEXT, payload TEXT);
    CREATE INDEX IF NOT EXISTS ix_learn_events_sid ON learn_events(sid, seq);
    CREATE TABLE IF NOT EXISTS learn_tests (id TEXT PRIMARY KEY, sid TEXT, ts REAL, qids TEXT,
        status TEXT, result TEXT);
    """)
    return db


def _student(db, sid):
    r = db.execute("SELECT * FROM learn_students WHERE id=?", (sid,)).fetchone()
    if not r:
        raise HTTPException(404, "Unknown student")
    return r


def _add_event(db, sid, typ, payload, ts=None, eid=None):
    ts = ts or time.time()
    eid = eid or uuid.uuid4().hex
    cur = db.execute("INSERT OR IGNORE INTO learn_events(id,sid,ts,type,payload) VALUES(?,?,?,?,?)",
                     (eid, sid, ts, typ, json.dumps(payload)))
    if cur.rowcount:  # also feed the admin "activity" stream
        db.execute("INSERT INTO activity(ts,student,event) VALUES(?,?,?)",
                   (ts, sid, json.dumps({"type": typ, **payload})))
    db.commit()
    return cur.rowcount == 1


# ----------------------------------------------------------------- engine
def _day(ts):
    return dt.date.fromtimestamp(ts)


class Engine:
    """Replays events -> full learner state."""

    def __init__(self, sid, courses, events):
        C = content()
        self.sid = sid
        self.courses = [c for c in courses if c in C["courses"]] or list(C["courses"])
        self.cids = [c for c, d in C["concepts"].items() if d["course_slug"] in self.courses]
        self.pl = {c: P_INIT for c in self.cids}
        self.att, self.cor = Counter(), Counter()
        self.streak_c = Counter()          # consecutive correct per concept
        self.last = {}                     # concept -> ts
        self.recent_err = defaultdict(list)
        self.theta = 1000.0
        self.qb = {}                       # item difficulty (Elo)
        self.qcount = Counter()
        self.recent_q = []
        self.A = {c: np.eye(D) for c in self.cids}
        self.b = {c: np.zeros(D) for c in self.cids}
        self.answers = []                  # dicts
        self.test_ends = []
        self.theta_hist, self.reward_hist = [], []
        self.diag = defaultdict(list)      # course -> [(cid, correct)]
        for e in events:
            self._apply(e)

    # --- features / LinUCB
    def retention(self, cid, now):
        if cid not in self.last:
            return self.pl[cid]
        gap = max(0.0, (now - self.last[cid]) / 86400)
        S = 2 + 3 * self.streak_c[cid]
        return self.pl[cid] * math.exp(-gap / S)

    def prereq_ready(self, cid):
        pre = content()["concepts"][cid]["prerequisites"]
        pre = [p for p in pre if p in self.pl]
        if not pre:
            return 1.0
        return sum(min(1.0, self.pl[p] / CLEAR_P) for p in pre) / len(pre)

    def features(self, cid, now, minutes=30):
        d = content()["concepts"][cid]
        b_c = 1000 + (d["difficulty"] - 3) * 150
        er = self.recent_err[cid][-5:]
        return np.array([
            1 - self.pl[cid],
            1 - self.retention(cid, now),
            self.prereq_ready(cid),
            1 - min(1.0, abs(self.theta - b_c) / 500),
            (sum(er) / len(er)) if er else 0.0,
            min(1.0, minutes / 60),
        ])

    def arm_score(self, cid, now, minutes=30):
        x = self.features(cid, now, minutes)
        Ainv = np.linalg.inv(self.A[cid])
        th = Ainv @ self.b[cid]
        exploit = float(PRIOR_W @ x + th @ x)
        bonus = float(ALPHA * math.sqrt(x @ Ainv @ x))
        return dict(concept=cid, score=exploit + bonus, exploit=exploit, bonus=bonus, x=x.tolist())

    # --- update from an answer
    def _bkt(self, p, ok, diff):
        s = 0.8 + 0.1 * diff
        slip, guess = P_SLIP * s, P_GUESS / s
        if ok:
            post = p * (1 - slip) / (p * (1 - slip) + (1 - p) * guess)
        else:
            post = p * slip / (p * slip + (1 - p) * (1 - guess))
        return min(0.98, max(0.02, post + (1 - post) * P_LEARN))

    def _apply(self, e):
        t, p = e["type"], e["payload"]
        if t == "test_end":
            self.test_ends.append(e["ts"])
            return
        if t != "answer":
            return
        cid = p["concept_id"]
        if cid not in self.pl:
            return
        C = content()
        q = C["questions"].get(p["question_id"])
        diff = q["difficulty"] if q else 3
        ok = bool(p["correct"])
        x = self.features(cid, e["ts"])
        before = self.pl[cid]
        self.pl[cid] = self._bkt(before, ok, diff)
        reward = (self.pl[cid] - before) + 0.2 * (1 if ok else 0)
        self.A[cid] += np.outer(x, x)
        self.b[cid] += reward * x
        self.reward_hist.append(dict(ts=e["ts"], concept=cid, reward=round(reward, 4)))
        qid = p["question_id"]
        b0 = self.qb.get(qid, 1000 + (diff - 3) * 150)
        exp = 1 / (1 + 10 ** ((b0 - self.theta) / 400))
        self.theta += 24 * ((1 if ok else 0) - exp)
        self.qb[qid] = b0 - 16 * ((1 if ok else 0) - exp)
        self.theta_hist.append(dict(ts=e["ts"], theta=round(self.theta, 1)))
        self.att[cid] += 1
        self.cor[cid] += 1 if ok else 0
        self.streak_c[cid] = self.streak_c[cid] + 1 if ok else 0
        self.recent_err[cid].append(0 if ok else 1)
        self.last[cid] = e["ts"]
        self.qcount[qid] += 1
        self.recent_q = (self.recent_q + [qid])[-8:]
        self.answers.append(dict(ts=e["ts"], correct=ok, seconds=float(p.get("seconds", 0)),
                                 concept=cid, course=C["concepts"][cid]["course_slug"],
                                 test_id=p.get("test_id"), ctx=p.get("ctx")))
        if p.get("ctx") == "diagnostic":
            self.diag[C["concepts"][cid]["course_slug"]].append((cid, ok))

    # --- derived views
    def norm(self, cid):  # 0 at start, 1 at full mastery
        return max(0.0, (self.pl[cid] - P_INIT) / (1 - P_INIT))

    def progress(self, course=None):
        ids = [c for c in self.cids if course is None or content()["concepts"][c]["course_slug"] == course]
        return round(100 * sum(self.norm(c) for c in ids) / len(ids), 1) if ids else 0.0

    def weak_areas(self, now=None):
        now = now or time.time()
        C = content()
        out = []
        for c in self.cids:
            if self.pl[c] < WEAK_P and self.att[c] >= WEAK_MIN_ATTEMPTS:
                gap = (now - self.last[c]) / 86400 if c in self.last else 0
                score = (1 - self.pl[c]) * (1 + min(1.5, gap / 30)) * (1 + len(C["dependents"][c]) / 6)
                weaker = [p for p in C["concepts"][c]["prerequisites"]
                          if p in self.pl and self.att[p] >= 1 and self.pl[p] < self.pl[c]]
                root = min(weaker, key=lambda p: self.pl[p]) if weaker else None
                out.append(dict(concept_id=c, name=C["concepts"][c]["name"], course=C["concepts"][c]["course_slug"],
                                mastery=round(self.pl[c], 3), attempts=self.att[c], score=round(score, 3),
                                root_cause=(dict(concept_id=root, name=C["concepts"][root]["name"]) if root else None)))
        return sorted(out, key=lambda d: -d["score"])

    def cleared(self):
        return [c for c in self.cids if self.pl[c] >= CLEAR_P and self.att[c] >= WEAK_MIN_ATTEMPTS]

    def recommend(self, now=None, course=None, k=3, minutes=30, only=None):
        now = now or time.time()
        ids = [c for c in self.cids if (course is None or content()["concepts"][c]["course_slug"] == course)]
        if only is not None:
            ids = [c for c in ids if c in only]
        scored = [self.arm_score(c, now, minutes) for c in ids]
        ready = [s for s in scored if self.prereq_ready(s["concept"]) >= 0.5]
        pool = ready or scored
        return sorted(pool, key=lambda s: -s["score"])[:k]

    def next_question(self, course=None, concept=None, mode="practice", now=None):
        now = now or time.time()
        C = content()
        if concept is None:
            only = None
            if mode == "diagnostic":
                hist = self.diag.get(course, [])
                if hist and not hist[-1][1]:  # failed -> probe an unseen prerequisite
                    pre = [p for p in C["concepts"][hist[-1][0]]["prerequisites"]
                           if p in self.pl and self.att[p] == 0]
                    if pre:
                        only = set(pre)
                if only is None:
                    unseen = {c for c in self.cids if self.att[c] == 0
                              and (course is None or C["concepts"][c]["course_slug"] == course)}
                    only = unseen or None
            rec = self.recommend(now, course, 1, only=only)
            if not rec:
                return None, None
            concept = rec[0]["concept"]
        pool = C["by_concept"].get(concept, [])
        fresh = [q for q in pool if q not in self.recent_q] or pool
        unseen = [q for q in fresh if self.qcount[q] == 0] or fresh
        rng = random.Random(f"{self.sid}:{concept}:{self.att[concept]}")
        qid = min(unseen, key=lambda q: (abs(self.theta - self.qb.get(q, 1000 + (C["questions"][q]["difficulty"] - 3) * 150)), rng.random()))
        return qid, concept

    def next_mock_date(self):
        if not self.test_ends:
            return dt.date.today()
        return _day(max(self.test_ends)) + dt.timedelta(days=7)

    def metrics(self, now=None):
        now = now or time.time()
        A = self.answers
        d30 = [a for a in A if now - a["ts"] <= 30 * 86400]
        w1 = [a for a in A if now - a["ts"] <= 7 * 86400]
        w0 = [a for a in A if 7 * 86400 < now - a["ts"] <= 14 * 86400]
        acc = lambda L: (sum(a["correct"] for a in L) / len(L)) if L else None
        mins = lambda L: sum(min(a["seconds"], 300) for a in L) / 60
        acc30, acc7, acc_prev = acc(d30), acc(w1), acc(w0)
        t1 = sum(1 for t in self.test_ends if now - t <= 7 * 86400)
        t0 = sum(1 for t in self.test_ends if 7 * 86400 < now - t <= 14 * 86400)
        per_day = defaultdict(lambda: [0, 0.0])
        for a in A:
            per_day[_day(a["ts"])][0] += 1
            per_day[_day(a["ts"])][1] += min(a["seconds"], 300)
        active = {d for d, (n, s) in per_day.items() if n >= 5 or s >= 600}
        today = dt.date.today()
        cur = today if today in active else today - dt.timedelta(days=1)
        streak = 0
        while cur in active:
            streak += 1
            cur -= dt.timedelta(days=1)
        study7, study_prev = mins(w1), mins(w0)
        days7 = {_day(a["ts"]) for a in w1}
        attempted = [c for c in self.cids if self.att[c] > 0]
        weak = self.weak_areas(now)
        focus = None
        if A:
            a7 = acc7 if acc7 is not None else acc30
            share = len(weak) / max(1, len(attempted))
            focus = round(100 * (0.4 * a7 + 0.3 * len(days7) / 7 + 0.3 * (1 - share)))
        return dict(
            tests_taken=len(self.test_ends), tests_delta=t1 - t0 if (t1 or t0) else None,
            accuracy=None if acc30 is None else round(100 * acc30),
            accuracy_delta=None if (acc7 is None or acc_prev is None) else round(100 * (acc7 - acc_prev), 1),
            study_hours=round(study7 / 60, 1),
            study_delta=None if study_prev == 0 else round((study7 - study_prev) / 60, 1),
            streak=streak, streak_at_risk=bool(streak and today not in active),
            focus_score=focus, answered=len(A))


def _engine(db, sid):
    s = _student(db, sid)
    ev = [dict(ts=r["ts"], type=r["type"], payload=json.loads(r["payload"]))
          for r in db.execute("SELECT ts,type,payload FROM learn_events WHERE sid=? ORDER BY seq", (sid,))]
    return Engine(sid, json.loads(s["courses"]), ev), s


def _qview(sid, qid, eng):
    q = content()["questions"][qid]
    opts = list(q["options"])
    random.Random(f"{sid}:{qid}:{eng.qcount[qid]}").shuffle(opts)  # answer position never leaks
    c = content()["concepts"][q["concept_id"]]
    return dict(question_id=qid, concept_id=q["concept_id"], concept=c["name"], course=c["course_slug"],
                qtype=q.get("qtype"), stem=q["question"], options=opts, difficulty=q["difficulty"],
                time_limit_sec=q.get("time_limit_sec"))


# ----------------------------------------------------------------- dashboard
def dashboard_dict(db, sid):
    eng, s = _engine(db, sid)
    C = content()
    now = time.time()
    m = eng.metrics(now)
    weak = eng.weak_areas(now)
    labels = ["Today", "Next", "Later"]
    if m["answered"] == 0:
        path = [dict(label="Today", title="Take the diagnostic", action="diagnostic", minutes=10,
                     course=eng.courses[0], concept_id=None)]
    else:
        path = []
        for lab, r in zip(labels, eng.recommend(now, None, 3)):
            c = r["concept"]
            action = "review_notes" if (eng.pl[c] < 0.35 and eng.att[c] >= WEAK_MIN_ATTEMPTS) else "practice"
            verb = "Review notes" if action == "review_notes" else "Practice"
            path.append(dict(label=lab, title=f"{verb}: {C['concepts'][c]['name']}", action=action,
                             minutes=8 if action == "review_notes" else 12, concept_id=c,
                             course=C["concepts"][c]["course_slug"], arm_score=round(r["score"], 3)))
    today = dt.date.today()
    due = eng.next_mock_date()
    topic = weak[0]["name"] if weak else ("Mixed baseline" if m["answered"] == 0 else
                                          C["concepts"][eng.recommend(now, None, 1)[0]["concept"]]["name"])
    notes = []
    if due <= today:
        notes.append(dict(kind="test_due", text="Your weekly mock test is ready."))
    stale = [c for c in eng.cids if eng.att[c] and eng.retention(c, now) < 0.7]
    if stale:
        notes.append(dict(kind="revision", text=f"{len(stale)} concept(s) are due for revision."))
    if m["streak_at_risk"]:
        notes.append(dict(kind="streak", text=f"Practise today to keep your {m['streak']}-day streak."))
    courses = []
    for slug in eng.courses:
        ids = [c for c in eng.cids if C["concepts"][c]["course_slug"] == slug]
        courses.append(dict(slug=slug, title=C["courses"][slug]["title"], term=C["courses"][slug]["term"],
                            progress=eng.progress(slug), concepts=len(ids),
                            attempted=sum(1 for c in ids if eng.att[c]),
                            questions=sum(len(C["by_concept"].get(c, [])) for c in ids)))
    return dict(
        student=dict(id=sid, name=s["name"], initials="".join(w[0] for w in s["name"].split()[:2]).upper() or "S",
                     courses=eng.courses),
        stats=dict(overall_progress=eng.progress(), **m),
        weak_areas=weak[:5], cleared=[C["concepts"][c]["name"] for c in eng.cleared()],
        learning_path=path,
        next_mock_test=dict(date=due.isoformat(), due=due <= today, topic=topic),
        courses=courses, notifications=notes, theta=round(eng.theta, 1),
        generated_at=now,
    )


# ----------------------------------------------------------------- models
class NewStudent(BaseModel):
    name: str
    roll_no: str | None = None
    courses: list[str] | None = None


class AnswerIn(BaseModel):
    question_id: str
    choice: str
    seconds: float = 0
    event_id: str | None = None
    ctx: str | None = "practice"
    test_id: str | None = None


class SubmitIn(BaseModel):
    answers: list[AnswerIn]


# ----------------------------------------------------------------- routes
@router.get("/courses")
def courses():
    C = content()
    return [dict(slug=s, title=c["title"], term=c["term"], ocw_url=c["ocw_url"], description=c["description"],
                 concepts=sum(1 for x in C["concepts"].values() if x["course_slug"] == s),
                 questions=sum(len(C["by_concept"].get(x, [])) for x, d in C["concepts"].items() if d["course_slug"] == s))
            for s, c in C["courses"].items()]


@router.post("/students")
def create_student(body: NewStudent):
    db = _db()
    sid = "s-" + uuid.uuid4().hex[:8]
    courses_ = body.courses or list(content()["courses"])
    db.execute("INSERT INTO learn_students(id,name,roll_no,courses,created) VALUES(?,?,?,?,?)",
               (sid, body.name.strip() or "Student", body.roll_no, json.dumps(courses_), time.time()))
    db.execute("INSERT OR REPLACE INTO students(id,name,cohort,masteries,progress_code,ts) VALUES(?,?,?,?,?,?)",
               (sid, body.name, "IIIT Senapati", "{}", "LIVE", time.time()))
    db.commit()
    hubdb.log_line(db, f"Student registered: {sid} ({body.name})")
    return dict(student_id=sid, courses=courses_)


@router.get("/students/{sid}/dashboard")
def dashboard(sid: str):
    return dashboard_dict(_db(), sid)


@router.get("/students/{sid}/next")
def next_q(sid: str, course: str | None = None, concept: str | None = None, mode: str = "practice"):
    db = _db()
    eng, _ = _engine(db, sid)
    if mode == "diagnostic":
        done = len(eng.diag.get(course, [])) if course else sum(len(v) for v in eng.diag.values())
        if done >= 12:
            return dict(done=True, answered=done, weak_areas=eng.weak_areas()
                        or [dict(concept_id=c, name=content()["concepts"][c]["name"], mastery=round(eng.pl[c], 3))
                            for c in sorted([c for c in eng.cids if eng.att[c]], key=lambda c: eng.pl[c])[:5]])
    qid, cid = eng.next_question(course, concept, mode)
    if not qid:
        raise HTTPException(404, "No questions available")
    rec = eng.arm_score(cid, time.time())
    out = _qview(sid, qid, eng)
    out["why"] = dict(concept=content()["concepts"][cid]["name"], mastery=round(eng.pl[cid], 3),
                      exploit=round(rec["exploit"], 3), exploration_bonus=round(rec["bonus"], 3),
                      ability_theta=round(eng.theta, 1), mode=mode)
    out["diagnostic_progress"] = len(eng.diag.get(course, [])) if mode == "diagnostic" else None
    return out


def _grade(db, sid, a: AnswerIn):
    C = content()
    q = C["questions"].get(a.question_id)
    if not q:
        raise HTTPException(404, "Unknown question")
    eng, _ = _engine(db, sid)
    cid = q["concept_id"]
    before = eng.pl.get(cid, P_INIT)
    correct_text = q["options"][q["answer_index"]]
    ok = a.choice.strip() == str(correct_text).strip()
    fresh = _add_event(db, sid, "answer", dict(question_id=a.question_id, concept_id=cid, correct=ok,
                       seconds=a.seconds, ctx=a.ctx, test_id=a.test_id, choice=a.choice), eid=a.event_id)
    eng2, _ = _engine(db, sid)
    return dict(correct=ok, correct_answer=correct_text, explanation=q.get("explanation"),
                source_ref=q.get("source_ref"), duplicate=not fresh,
                concept=dict(id=cid, name=C["concepts"][cid]["name"], mastery_before=round(before, 3),
                             mastery_after=round(eng2.pl[cid], 3), delta=round(eng2.pl[cid] - before, 3),
                             weak=eng2.pl[cid] < WEAK_P and eng2.att[cid] >= WEAK_MIN_ATTEMPTS),
                ability_theta=round(eng2.theta, 1))


@router.post("/students/{sid}/answer")
def answer(sid: str, a: AnswerIn):
    db = _db()
    _student(db, sid)
    res = _grade(db, sid, a)
    d = dashboard_dict(db, sid)
    res["live"] = dict(stats=d["stats"], weak_areas=d["weak_areas"], learning_path=d["learning_path"])
    return res


@router.post("/students/{sid}/tests")
def make_test(sid: str, course: str | None = None, n: int = 15):
    db = _db()
    eng, _ = _engine(db, sid)
    C = content()
    now = time.time()
    ids = [c for c in eng.cids if course is None or C["concepts"][c]["course_slug"] == course]
    rng = random.Random(f"{sid}:{len(eng.test_ends)}:{eng.att.total()}")
    weak_pool = [c for c in ids if eng.att[c] and (eng.pl[c] < 0.6 or eng.retention(c, now) < 0.7)]
    cur_mod = None
    if eng.answers:
        cur_mod = C["concepts"][eng.answers[-1]["concept"]]["module_ref"]
    mod_pool = [c for c in ids if C["concepts"][c]["module_ref"] == cur_mod] if cur_mod else []
    picked, seen = [], set()

    def take(pool, k):
        qs = [q for c in pool for q in C["by_concept"].get(c, []) if q not in seen]
        rng.shuffle(qs)
        for q in qs[:k]:
            picked.append(q); seen.add(q)
    take(weak_pool, round(n * 0.5)); take(mod_pool, round(n * 0.3))
    take(ids, n - len(picked))
    take(ids, n - len(picked))
    tid = "t-" + uuid.uuid4().hex[:8]
    db.execute("INSERT INTO learn_tests(id,sid,ts,qids,status) VALUES(?,?,?,?,'open')",
               (tid, sid, now, json.dumps(picked)))
    _add_event(db, sid, "test_start", dict(test_id=tid, n=len(picked)))
    qs = [_qview(sid, q, eng) for q in picked]
    return dict(test_id=tid, questions=qs,
                time_limit_sec=sum((C["questions"][q].get("time_limit_sec") or 90) for q in picked))


@router.post("/students/{sid}/tests/{tid}/submit")
def submit_test(sid: str, tid: str, body: SubmitIn):
    db = _db()
    t = db.execute("SELECT * FROM learn_tests WHERE id=? AND sid=?", (tid, sid)).fetchone()
    if not t:
        raise HTTPException(404, "Unknown test")
    if t["status"] == "submitted":
        return json.loads(t["result"])
    C = content()
    qids = json.loads(t["qids"])
    given = {a.question_id: a for a in body.answers if a.question_id in qids}
    review, per = [], defaultdict(lambda: dict(correct=0, total=0, before=None, after=None))
    for qid in qids:
        cid = C["questions"][qid]["concept_id"]
        a = given.get(qid)
        if a is None:
            review.append(dict(question_id=qid, stem=C["questions"][qid]["question"], skipped=True,
                               correct_answer=C["questions"][qid]["options"][C["questions"][qid]["answer_index"]]))
            continue
        a.ctx, a.test_id = "test", tid
        a.event_id = a.event_id or f"{tid}:{qid}"
        r = _grade(db, sid, a)
        p = per[cid]
        p["total"] += 1; p["correct"] += 1 if r["correct"] else 0
        p["before"] = r["concept"]["mastery_before"] if p["before"] is None else p["before"]
        p["after"] = r["concept"]["mastery_after"]
        review.append(dict(question_id=qid, stem=C["questions"][qid]["question"], your_answer=a.choice,
                           correct=r["correct"], correct_answer=r["correct_answer"],
                           explanation=r["explanation"], source_ref=r["source_ref"], seconds=a.seconds))
    _add_event(db, sid, "test_end", dict(test_id=tid))
    answered = sum(p["total"] for p in per.values())
    right = sum(p["correct"] for p in per.values())
    result = dict(test_id=tid, total=len(qids), answered=answered, correct=right,
                  score_pct=round(100 * right / len(qids)) if qids else 0,
                  by_concept=[dict(concept_id=c, name=C["concepts"][c]["name"], **p) for c, p in per.items()],
                  weak_points=[dict(concept_id=c, name=C["concepts"][c]["name"])
                               for c, p in per.items() if p["correct"] < p["total"]],
                  review=review, dashboard=dashboard_dict(db, sid))
    db.execute("UPDATE learn_tests SET status='submitted', result=? WHERE id=?", (json.dumps(result), tid))
    db.commit()
    return result


@router.get("/students/{sid}/tests")
def tests(sid: str):
    db = _db()
    _student(db, sid)
    out = []
    for r in db.execute("SELECT id,ts,status,result FROM learn_tests WHERE sid=? ORDER BY ts DESC", (sid,)):
        res = json.loads(r["result"]) if r["result"] else None
        out.append(dict(test_id=r["id"], ts=r["ts"], status=r["status"],
                        score_pct=res["score_pct"] if res else None, total=res["total"] if res else None))
    return out


@router.get("/students/{sid}/analytics")
def analytics(sid: str):
    db = _db()
    eng, _ = _engine(db, sid)
    C = content()
    now = time.time()
    mastery = [dict(concept_id=c, name=C["concepts"][c]["name"], course=C["concepts"][c]["course_slug"],
                    mastery=round(eng.pl[c], 3), attempts=eng.att[c], correct=eng.cor[c],
                    retention=round(eng.retention(c, now), 3),
                    weak=eng.pl[c] < WEAK_P and eng.att[c] >= WEAK_MIN_ATTEMPTS) for c in eng.cids]
    byday = defaultdict(lambda: dict(answered=0, correct=0, minutes=0.0))
    for a in eng.answers:
        d = byday[_day(a["ts"]).isoformat()]
        d["answered"] += 1; d["correct"] += a["correct"]; d["minutes"] += min(a["seconds"], 300) / 60
    arms = sorted((eng.arm_score(c, now) for c in eng.cids), key=lambda s: -s["score"])[:8]
    return dict(mastery=mastery,
                by_day=[dict(date=k, accuracy=round(100 * v["correct"] / v["answered"]), **{**v, "minutes": round(v["minutes"], 1)})
                        for k, v in sorted(byday.items())],
                theta_history=eng.theta_hist[-100:], reward_history=eng.reward_hist[-100:],
                bandit_arms=[dict(concept=C["concepts"][a["concept"]]["name"], score=round(a["score"], 3),
                                  exploit=round(a["exploit"], 3), exploration_bonus=round(a["bonus"], 3)) for a in arms],
                weak_areas=eng.weak_areas(now), strong=[C["concepts"][c]["name"] for c in eng.cleared()])


@router.post("/students/{sid}/reset")
def reset(sid: str):
    db = _db()
    _student(db, sid)
    db.execute("DELETE FROM learn_events WHERE sid=?", (sid,))
    db.execute("DELETE FROM learn_tests WHERE sid=?", (sid,))
    db.execute("DELETE FROM activity WHERE student=?", (sid,))
    db.commit()
    return dict(ok=True)


@router.get("/concepts/{cid}")
def concept_page(cid: str):
    C = content()
    c = C["concepts"].get(cid)
    if not c:
        raise HTTPException(404, "Unknown concept")
    con = sqlite3.connect(CONTENT_DB)
    con.row_factory = sqlite3.Row
    chunks = [dict(r) for r in con.execute(
        "SELECT id,title,page_number,content,source_ref FROM chunks WHERE module_id=?", (c["module_ref"],))]
    ex = [dict(r) for r in con.execute(
        "SELECT id,title,problem_text,solution_text,source_ref FROM exercises WHERE concept_id=?", (cid,))]
    con.close()
    return dict(concept=c, prerequisites=[dict(id=p, name=C["concepts"][p]["name"]) for p in c["prerequisites"]],
                chunks=chunks, exercises=ex, question_count=len(C["by_concept"].get(cid, [])))


@router.get("/search")
def search(q: str = Query(min_length=2)):
    con = sqlite3.connect(CONTENT_DB)
    con.row_factory = sqlite3.Row
    term = " ".join(w + "*" for w in "".join(ch if ch.isalnum() else " " for ch in q).split())
    try:
        rows = con.execute("""SELECT c.id, c.title, c.course_slug, c.page_number, c.source_ref,
                 snippet(chunks_fts, 2, '[', ']', '…', 24) AS excerpt
                 FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.chunk_id
                 WHERE chunks_fts MATCH ? LIMIT 20""", (term,)).fetchall()
    except sqlite3.OperationalError:
        rows = []
    con.close()
    return [dict(r) for r in rows]


@router.get("/live-test", include_in_schema=False)
def live_test():
    return FileResponse(Path(__file__).parent / "live_test.html")
