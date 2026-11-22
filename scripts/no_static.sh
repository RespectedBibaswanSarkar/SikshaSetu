#!/usr/bin/env bash
# no_static.sh — Reject any hardcoded learning data/mock stats in client source.
# Every stat must come from /api/learn/*, never from embedded constants.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/client/src"
FAIL=0

check_pattern() {
  local desc="$1"; local pattern="$2"; local flag="${3:--rn}"
  local hits
  hits=$(grep $flag --include="*.ts" --include="*.tsx" -l "$pattern" "$SRC" 2>/dev/null | grep -v "\.d\.ts" || true)
  if [ -n "$hits" ]; then
    echo "❌  $desc — found in:"
    echo "$hits" | sed 's/^/     /'
    ((FAIL++)) || true
  fi
}

# No local engine/BKT/bandit logic in client
check_pattern "No local BKT engine in client"   "P_LEARN\|P_SLIP\|P_GUESS\|P_INIT"
check_pattern "No offline Engine class in client" "class Engine"
check_pattern "No local Bandit in client"         "class Bandit\|LinUCB"

# No hardcoded stats
check_pattern "No hardcoded mastery percent"      '"mastery":\s*[0-9]'    "-rn"
check_pattern "No hardcoded streak value"         'streak.*=.*[0-9]'      "-rn"

# No offline-pack fallback URLs
check_pattern "No offline-pack URLs"              "offline-pack"

# No getManifest / getCatalog offline API
check_pattern "No old offline catalog API"        "getCatalog\|getManifest\|getConcepts\|getQuestions"

# No imported engine/storage/bandit
check_pattern "No engine.ts import"               "from.*['\"].*engine['\"]"
check_pattern "No storage.ts import"              "from.*['\"].*storage['\"]"
check_pattern "No bandit.ts import"               "from.*['\"].*bandit['\"]"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "✅  no_static: client contains no hardcoded learning data"
  exit 0
else
  echo "⛔  no_static: $FAIL pattern(s) violated"
  exit 1
fi
