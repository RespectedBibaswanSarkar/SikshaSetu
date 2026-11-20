# SikshaSetu — College Edition (offline-first adaptive learning on MIT OCW)

An installable PWA + Ubuntu desktop (Tauri) + Android APK (Capacitor) system: students get
personalised study plans from MIT OCW lecture videos/notes, diagnostic assessments, weekly mock
tests, on-device analytics, and an RL-driven study recommender — **fully offline-first** after one sync.

## Architecture
```
/client   React+Vite PWA (dashboard, player, diagnostic, mock test, analytics, planner, OPFS storage, bandit recommender)
/hub      FastAPI+SQLite: serves content objects (Range+ETag), catalog, manifests, admin API, admin panel
/pipeline Python CLI: resolve → fetch → transcode → transcripts → segment → map → questions → package → install → verify
/sim      200-student simulation: recommender vs fixed syllabus vs random (docs/evidence.md)
/docs     schema.md, seed_report.md, DEMO.md, evidence.md
```

## Install
```
# 1. Python deps (venv recommended)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # fastapi uvicorn httpx pytest numpy scipy yt-dlp faster-whisper

# 2. Seed (downloads lecture videos/notes from MIT OCW, transcodes, packages content store)
make seed                            # all 3 courses; or: make seed-course COURSE=6.006
make verify                          # verify hashes, acyclicity, per-tier sizes

# 3. Hub + Admin panel (serves content, admin UI)
make serve-lan                       # prints LAN URL + QR

# 4. Student app
cd client && npm ci && npm run build     # PWA dist → client/dist
# Ubuntu desktop: cargo install --path .  (Tauri); Android: npx @capacitor/cli build android
```

## Demos
- `docs/DEMO.md` — 5-minute LAN demo script (student airplane mode, diagnostic, plan, mock test, weak-point report).
- `/sim` — `make sim`: bandit vs fixed syllabus vs random (200 students) → `docs/evidence.md`.
- `/admin` — import OCW course URLs, live stage progress, concept/question review, publish.
- Playwright offline test: `cd client && npx playwright test` (HUB_URL=http://127.0.0.1:8000).

## Licensing
OCW material: CC BY-NC-SA (LICENSES.md). MIT OCW condition: attribution for every asset (course page, URL, license).
Machine-generated transcripts (whisper) flagged; review in admin panel.

## Limitations
- Transcripts depend on YouTube auto-captions; whisper (`faster-whisper`) is the fallback for videos without captions.
- 6.006 (Spring 2020) official OCW videos are YouTube-hosted; see docs/seed_report.md.
- Token-limited build (offline-first, no runtime LLM calls).

## 🎬 Animations (ManimX — `animations/`)

Two ManimX videos (rendered with `python3 -m manim -ql animations/pipeline.py PipelineAnim` etc.):

| Diagram | What it shows |
|---|---|
| **[Pipeline](animations/media/pipeline.mp4)** | MIT OCW resolve → fetch (2-concurrent, checksums) → parse → transcode → transcripts → segment → map → questions → package → install → verify — with per-stage color changes. |
| **[Adaptive learning loop](animations/media/learning_loop.mp4)** | Diagnostic → mastery update → bandit pick → mock test → weak-point report; loop arrow with pacing/decay. |

Sources: [`animations/pipeline.py`](animations/pipeline.py), [`animations/learning_loop.py`](animations/learning_loop.py).

### Interactive pipeline SVG

[`assets/pipeline.svg`](assets/pipeline.svg) — click any stage node to see details; animated edges; course badge pulse:

- **resolve** — course page + units (mitocw search for lecture videos)
- **fetch** — downloads with checksums, rate-limited (2 concurrent)
- **transcode** — 360p H.264/AAC faststart, audio-only Opus, poster
- **transcripts** — official captions (machine) or whisper fallback
- **map** — concept graph (~100–200 concepts per course), reviewed:false
- **package** — content-addressed store (objects/<sha256>), catalog/concepts/questions/manifests
- **verify** — video+notes+transcript+concepts per unit, hashes, acyclic graph
