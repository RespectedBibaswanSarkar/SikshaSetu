"""SikshaSetu Hub (FastAPI): serves content objects with Range+ETag, catalog/manifests,
admin API (import course from OCW URL, review, publish, library, heatmap, logs), serves admin panel."""
import json, os, re, subprocess, sys, time, uuid
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / "pipeline" / "store"
ADMIN = Path(__file__).parent / "admin"

app = FastAPI(title="SikshaSetu Hub")

# ---------------- content serving ----------------

def read_store(p: Path):
    return json.loads(p.read_text()) if p.exists() else None

def file_etag(p: Path, size=None):
    if not p.exists():
        return None
    if size is None:
        size = p.stat().st_size
    return f'"{int(p.stat().st_mtime_ns)}-{size}"'

def serve_file(p: Path, request: Request):
    if not p.exists():
        return Response(status_code=404)
    etag = file_etag(p)
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304)
    size = p.stat().st_size
    range_h = request.headers.get("range")
    if range_h:
        m = re.match(r"bytes=(\d*)-(\d*)", range_h)
        if m:
            start = int(m.group(1) or 0)
            end = int(m.group(2)) if m.group(2) else size - 1
            end = min(end, size - 1)
            if start >= size:
                return Response(status_code=416)
            data = p.read_bytes()[start:end + 1]
            return Response(content=data, status_code=206,
                            headers={"Content-Range": f"bytes {start}-{end}/{size}",
                                     "Accept-Ranges": "bytes", "ETag": etag,
                                     "Content-Length": str(len(data))})
    return FileResponse(p, headers={"Accept-Ranges": "bytes", "ETag": etag})

@app.get("/catalog.json")
def catalog(): return read_store(STORE / "catalog.json")

@app.get("/concepts.json")
def concepts(): return read_store(STORE / "concepts.json")

@app.get("/questions.json")
def questions(): return read_store(STORE / "questions.json")

@app.get("/version.json")
def version(): return read_store(STORE / "version.json")

@app.get("/{slug}.manifest.json")
def manifest(slug: str):
    p = STORE / f"{slug}.manifest.json"
    if not p.exists():
        return Response(status_code=404)
    return read_store(p)

@app.get("/objects/{sha256}")
def object_sha(sha256: str, request: Request):
    p = STORE / "objects" / sha256
    if not p.exists():
        return Response(status_code=404)
    return serve_file(p, request)

# ---------------- admin API ----------------

from hub.db import connect, log_line

def all_manifests():
    out = []
    if STORE.exists():
        for p in sorted(STORE.glob("*.manifest.json")):
            m = json.loads(p.read_text())
            for u in m["units"]:
                for tier, a in u["assets"].items():
                    a["unit"] = u["id"]
            out.append(m)
    return out

@app.get("/api/admin/stats")
def admin_stats():
    mans = all_manifests()
    students_db = connect()
    nstud = students_db.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    insts = [m["meta"]["institution"] for m in mans]
    return {"courses": len(mans), "students": nstud, "institutions": sorted(set(insts)),
            "storage_bytes": sum(a["size"] for m in mans for u in m["units"] for a in u["assets"].values())}

@app.get("/api/admin/courses")
def admin_courses():
    mans = all_manifests()
    return [{"slug": m["slug"], "title": m["meta"]["title"], "term": m["meta"]["term"],
             "units": len(m["units"]), "attribution": m["meta"]["attribution"]} for m in mans]

@app.get("/api/admin/concepts")
def admin_concepts():
    return read_store(STORE / "concepts.json") or []

@app.get("/api/admin/questions")
def admin_questions():
    return read_store(STORE / "questions.json") or []

@app.post("/api/admin/concepts/{cid}")
async def admin_edit_concept(cid: str, request: Request):
    body = await request.json()
    p = STORE / "concepts.json"
    cs = read_store(p) or []
    c = next((c for c in cs if c["id"] == cid), None)
    if not c:
        return JSONResponse({"error": "not found"}, 404)
    c.update({k: v for k, v in body.items() if k in ("name", "prerequisites", "description")})
    p.write_text(json.dumps(cs, indent=1))
    log_line(connect(), f"concept edited: {cid} by admin", "INFO")
    return {"ok": True, "concept": c}

@app.post("/api/admin/questions/{qid}/review")
async def admin_approve_question(qid: str, request: Request):
    body = await request.json()
    p = STORE / "questions.json"
    qs = read_store(p) or []
    q = next((q for q in qs if q["id"] == qid), None)
    if not q:
        return JSONResponse({"error": "not found"}, 404)
    q["reviewed"] = True
    q.update({k: v for k, v in body.items() if k in ("question", "options", "answer_index")})
    p.write_text(json.dumps(qs, indent=1))
    return {"ok": True, "question": q}

@app.get("/api/admin/imports")
def admin_imports():
    db = connect()
    return [dict(r) for r in db.execute("SELECT id, ocw_url, status, stage, ts FROM imports ORDER BY id DESC")]

@app.get("/api/admin/import/{iid}/status")
def admin_import_status(iid: str):
    db = connect()
    r = db.execute("SELECT * FROM imports WHERE id=?", (iid,)).fetchone()
    return dict(r) if r else {"error": "not found"}

def run_pipeline(ocw_url: str, iid: str):
    db = connect()
    def update(stage, log=""):
        db.execute("UPDATE imports SET stage=?, log=? WHERE id=?", (stage, log, iid))
        db.commit()
    for st in ["resolve", "fetch", "parse", "transcode", "transcripts", "segment", "map", "questions", "package", "install"]:
        update(st, f"running {st}")
        r = subprocess.run([sys.executable, "-m", "pipeline.run", "--stage", st],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            update("failed", f"stage {st}: {r.stderr[-800:]}")
            log_line(db, f"import {iid} failed at {st}: {r.stderr[-500:]}", "ERROR")
            return
    # find slug and set status
    for p in STORE.glob("*.manifest.json"):
        pass
    update("done", "course mapped & published")
    log_line(db, f"import {iid} done", "INFO")

@app.post("/api/admin/import")
async def admin_import(request: Request):
    body = await request.json()
    url = body.get("ocw_url", "")
    iid = uuid.uuid4().hex[:12]
    db = connect()
    db.execute("INSERT INTO imports(id, ocw_url, status, stage, ts) VALUES(?,?,?,?,?)",
               (iid, url, "importing", "resolve", time.time()))
    db.commit()
    import threading
    threading.Thread(target=run_pipeline, args=(url, iid), daemon=True).start()
    return {"id": iid}

@app.get("/api/admin/library")
def admin_library():
    mans = all_manifests()
    out = []
    for m in mans:
        for u in m["units"]:
            out.append({"unit": u["id"], "course": m["slug"], "segments": len(u["segments"]),
                        "concepts": len(u["concepts"]),
                        "tiers": {t: a["size"] for t, a in u["assets"].items()},
                        "attribution": m["meta"]["attribution"]})
    return out

@app.get("/api/admin/analytics/heatmap")
def admin_heatmap():
    db = connect()
    rows = [dict(r) for r in db.execute("SELECT ts FROM activity ORDER BY ts")]
    if not rows:
        return {"days": []}
    by_day = {}
    for r in rows:
        by_day.setdefault(time.strftime("%Y-%m-%d", time.localtime(r["ts"])), 0)
        by_day[time.strftime("%Y-%m-%d", time.localtime(r["ts"]))] += 1
    return {"days": [{"day": d, "count": by_day[d]} for d in sorted(by_day)][-30:]}

@app.get("/api/admin/logs")
def admin_logs():
    db = connect()
    return [dict(r) for r in db.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 200")]

# ---------------- static admin panel ----------------

if ADMIN.exists():
    app.mount("/admin", StaticFiles(directory=ADMIN, html=True), name="admin")

@app.get("/")
def root():
    return FileResponse(ADMIN / "index.html") if (ADMIN / "index.html").exists() else JSONResponse({"hub": "sikshasetu", "store": str(STORE)})

@app.get("/api/admin/sync/export")
def admin_sync_export():
    """Students export roster + activity: list of {id,name,cohort,masteries,progress_code}"""
    db = connect()
    return [dict(r) for r in db.execute("SELECT * FROM students")]

@app.post("/api/admin/sync/import")
async def admin_sync_import(request: Request):
    """Roster import: list of {name, cohort, masteries:[], progress_code}"""
    body = await request.json()
    db = connect()
    for s in body.get("students", []):
        db.execute("INSERT OR REPLACE INTO students(id,name,cohort,masteries,progress_code,ts) VALUES(?,?,?,?,?,?)",
                   (s.get("id") or uuid.uuid4().hex[:10], s.get("name"), s.get("cohort"),
                    json.dumps(s.get("masteries", {})), s.get("progress_code"), time.time()))
    db.commit()
    log_line(db, f"roster imported: {len(body.get('students', []))} students", "INFO")
    return {"ok": True, "count": len(body.get("students", []))}

if __name__ == "__main__":
    lan = "--lan" in sys.argv
    if lan:
        import socket
        ip = socket.gethostbyname(socket.gethostname())
        print(f"SikshaSetu Hub listening on http://{ip}:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
