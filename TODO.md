# SikshaSetu TODO — All Green Checklist

## Phase 1: Scripts & Infrastructure
- [ ] Create `scripts/verify_all.sh`
- [ ] Create `scripts/no_static.sh`
- [ ] Create `client/e2e/app.spec.ts`
- [ ] Create `tests/test_learn_extra.py`
- [ ] Add `tsconfig.json` to client
- [ ] Update `client/package.json` build script = `tsc --noEmit && vite build`
- [ ] Create/fix `.gitignore`
- [ ] Create `run.sh`
- [ ] Create `Makefile`
- [ ] Fix `scripts/install-ubuntu.sh`

## Phase 2: Clean Up Legacy Code
- [x] `client/src/App.tsx` imports `./Offline` → remove (Offline component never existed as file)
- [ ] Delete: `client/src/{engine.ts,bandit.ts,storage.ts}` (old offline logic)
- [ ] Delete: old `Diagnostic.tsx/MockTest.tsx/Misc.tsx` (replace with real API versions)
- [ ] Remove manifest/segment/asset code from `api.ts`
- [ ] Remove `client/public/offline-pack/*`
- [ ] Remove `pipeline/stages/*` video stages, `pipeline/state/*`, legacy dirs
- [ ] `git rm --cached hub/hub.db`

## Phase 3: Content Quality (B)
- [ ] Fix answer_index distribution (344/456 = 75% with index 0 — must vary)
- [ ] Fix fake URLs in source_ref (invented `/resources/6.006-m01/`)
- [ ] Fix boilerplate explanations — must say WHY
- [ ] Need ≥ 25-35 concepts per course (currently: 25/26/25 — OK but need to verify)
- [ ] Need ≥ 8 questions per concept (currently some have 6)
- [ ] Verify answers with sympy/numpy where possible
- [ ] Real OCW source attribution
- [ ] Regenerate DB via `python -m pipeline.build_db`

## Phase 4: Backend Gaps (C)
- [ ] `GET /api/learn/courses/{slug}/tree?sid=`
- [ ] `GET /students/{sid}/planner`, `POST .../planner/{item}/done`, `POST .../planner/regenerate`
- [ ] `GET /api/learn/notes?course=&type=`
- [ ] `PATCH /students/{sid}` (name, roll_no, courses, weekly_hours)
- [ ] `GET /students/{sid}/export`, `POST .../import`
- [ ] `GET /students/{sid}/tests/{tid}` (stored result)
- [ ] Admin: `/api/admin/map-course` with job progress at `GET /api/admin/import/{job}`
- [ ] `GET /api/admin/users` (real rows)
- [ ] `GET/PUT /api/admin/institution`
- [ ] Admin PIN log at start

## Phase 5: Student App Rewrite (D)
- [ ] Create `client/src/live.ts` — single typed API client
- [ ] Create shared store (useSyncExternalStore)
- [ ] Onboarding: name, roll_no, courses → POST /students; sid in localStorage
- [ ] Dashboard: bind to /students/{sid}/dashboard
- [ ] Practice page: GET /next → answer → POST /answer
- [ ] Diagnostic: mode=diagnostic
- [ ] Mock Tests: full flow
- [ ] My Courses: tree view
- [ ] AI Analytics: mastery/heatmap/etc
- [ ] Study Planner
- [ ] Notes: chunk viewer + search
- [ ] Settings: profile, export/import, reset, theme
- [ ] Error state: hub unreachable → show error-state + retry button
- [ ] All required data-testid attributes
- [ ] `<main>` element
- [ ] Responsive design (1280+, 768-1279, <768)
- [ ] Accessibility (aria, focus rings, contrast, motion)
- [ ] No dead controls

## Phase 6: Admin App (E)
- [ ] Separate admin app at `/admin/` (hash-routed)
- [ ] Hub serves admin at /admin/ (not student app)
- [ ] Fix known bugs (click recursion, wrong tab, polling nonexistent selectors)
- [ ] Dashboard: real stats from /api/admin/stats
- [ ] Course Mapper: select (6.006/6.100L/18.06) + Map Course → progress → success
- [ ] Analytics, Users, Logs tables from API
- [ ] Admin PIN required except localhost

## Phase 7: Run & Tests
- [ ] `pytest tests/` — ALL PASS (including test_learn.py + test_learn_extra.py)
- [ ] `python scripts/validate_content.py` — ALL PASS
- [ ] `python scripts/no_static.sh` — ALL PASS
- [ ] `tsc --noEmit && vite build` — SUCCESS
- [ ] `python scripts/smoke_backend.py` — ALL PASS
- [ ] `npx playwright test` — ALL PASS
- [ ] `bash scripts/verify_all.sh` → ALL GREEN

## Phase 8: Final
- [ ] Screenshots of every page at 3 viewports into docs/screens/
- [ ] Update README.md and PROGRESS.md
- [ ] Final verify_all.sh run → ALL GREEN
- [ ] Print final report
