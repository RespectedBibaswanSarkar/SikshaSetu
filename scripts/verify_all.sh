#!/usr/bin/env bash
# verify_all.sh — SikshaSetu full acceptance suite.
# NEVER edit or weaken this file. Exit 0 = ALL GREEN.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PASS=0; FAIL=0
ok()  { echo "✅  $*"; ((PASS++)) || true; }
fail(){ echo "❌  $*"; ((FAIL++)) || true; }

# ── 1. pytest (backend unit + extra) ───────────────────────────────────────
echo ""; echo "═══ 1 / 7  pytest ═══"
if python3 -m pytest tests/ -q --tb=short 2>&1; then
  ok "pytest"
else
  fail "pytest (see output above)"
fi

# ── 2. content validation ──────────────────────────────────────────────────
echo ""; echo "═══ 2 / 7  content validation ═══"
if python3 scripts/validate_content.py 2>&1; then
  ok "validate_content"
else
  fail "validate_content"
fi

# ── 3. no-static check ────────────────────────────────────────────────────
echo ""; echo "═══ 3 / 7  no-static check ═══"
if bash scripts/no_static.sh 2>&1; then
  ok "no_static"
else
  fail "no_static"
fi

# ── 4. TypeScript + Vite build ────────────────────────────────────────────
echo ""; echo "═══ 4 / 7  tsc + vite build ═══"
(cd client && npm run build) 2>&1
if [ $? -eq 0 ]; then
  ok "tsc+vite build"
else
  fail "tsc+vite build"
fi

# ── 5. smoke backend (needs hub running) ─────────────────────────────────
echo ""; echo "═══ 5 / 7  smoke backend ═══"
# Start hub if not running
if ! curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
  echo "Starting hub for smoke test..."
  python3 -m uvicorn hub.main:app --host 127.0.0.1 --port 8000 --log-level error &
  HUB_PID=$!
  sleep 3
  STARTED=1
else
  STARTED=0
fi

if python3 scripts/smoke_backend.py http://localhost:8000 2>&1; then
  ok "smoke_backend"
else
  fail "smoke_backend"
fi

if [ "${STARTED:-0}" = "1" ]; then kill $HUB_PID 2>/dev/null || true; fi

# ── 6. Playwright e2e ─────────────────────────────────────────────────────
echo ""; echo "═══ 6 / 7  Playwright e2e ═══"
# Start hub for e2e
if ! curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
  python3 -m uvicorn hub.main:app --host 127.0.0.1 --port 8000 --log-level error &
  HUB_PID2=$!
  sleep 3
  STARTED2=1
else
  STARTED2=0
fi

(cd client && npx playwright test --reporter=line 2>&1)
if [ $? -eq 0 ]; then
  ok "playwright"
else
  fail "playwright (see output above)"
fi

if [ "${STARTED2:-0}" = "1" ]; then kill $HUB_PID2 2>/dev/null || true; fi

# ── 7. admin smoke ────────────────────────────────────────────────────────
echo ""; echo "═══ 7 / 7  admin routes ═══"
if ! curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
  python3 -m uvicorn hub.main:app --host 127.0.0.1 --port 8000 --log-level error &
  HUB_PID3=$!
  sleep 3
  STARTED3=1
else
  STARTED3=0
fi

ADMIN_OK=1
for ROUTE in "/api/admin/stats" "/api/admin/users" "/api/admin/logs"; do
  STATUS=$(curl -sf -o /dev/null -w "%{http_code}" -H "X-Admin-PIN: 1234" "http://localhost:8000$ROUTE" 2>/dev/null || echo "000")
  if [ "$STATUS" = "200" ]; then
    echo "   $ROUTE → $STATUS"
  else
    echo "   FAIL $ROUTE → $STATUS"
    ADMIN_OK=0
  fi
done
# Admin UI
ADMIN_UI=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:8000/admin/" 2>/dev/null || echo "000")
echo "   /admin/ → $ADMIN_UI"
if [ "$ADMIN_UI" != "200" ]; then ADMIN_OK=0; fi

if [ "${STARTED3:-0}" = "1" ]; then kill $HUB_PID3 2>/dev/null || true; fi

if [ "$ADMIN_OK" = "1" ]; then
  ok "admin routes"
else
  fail "admin routes"
fi

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════"
echo "PASS: $PASS   FAIL: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "🎉  ALL GREEN"
  exit 0
else
  echo "⛔  SOME CHECKS FAILED"
  exit 1
fi
