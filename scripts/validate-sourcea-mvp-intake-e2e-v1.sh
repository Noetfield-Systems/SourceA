#!/usr/bin/env bash
# Business A — 48h MVP intake E2E (commercial plane). Light — no Playwright marathon.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
GREEN="$ROOT/SourceA-landing/green-unified"
PORT="${MVP_INTAKE_PORT:-8192}"
API="http://127.0.0.1:${PORT}/api/commercial/mvp-intake/v1"

echo "=== validate-sourcea-mvp-intake-e2e-v1 ==="

# 1) Static files present
for f in start.html commercial-start.js commercial-start.css data/mvp-intake-config.json; do
  [[ -f "$GREEN/$f" ]] || { echo "FAIL: missing $GREEN/$f"; exit 1; }
done
echo "OK: commercial landing files"

# 2) Pages function present
[[ -f "$ROOT/cloud/pages-functions/_middleware.js" ]] || {
  echo "FAIL: missing pages middleware"
  exit 1
}
echo "OK: pages middleware"

# 3) Python intake self-test (disk receipt)
python3 scripts/sourcea_mvp_intake_submit_v1.py --self-test --json | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
r = row['receipt']
assert r.get('intake_id','').startswith('mvp-'), r
print('OK: self-test intake', r['intake_id'])
"

# 4) HTTP round-trip (dev server)
python3 scripts/sourcea_mvp_intake_submit_v1.py --serve --port "$PORT" &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 1

curl -sf -X POST "$API" \
  -H 'Content-Type: application/json' \
  -d '{"building":"Test SaaS dashboard","building_type":"mvp","competitor":"linear.app","deadline":"two_weeks","budget":"1k_3k","email":"e2e@example.com"}' \
  | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
assert row.get('end_screen'), row
print('OK: HTTP intake', row['intake_id'])
"

# 5) start.html content checks
python3 - <<'PY'
from pathlib import Path
html = Path("SourceA-landing/green-unified/start.html").read_text()
for needle in (
    "We build your startup's MVP in 48 hours",
    "What are you building?",
    "What's your deadline?",
    "What's your budget?",
    "Your email",
    "hello@sourcea.app",
    "sa-mvp-intake-form",
):
    assert needle in html, f"missing: {needle}"
print("OK: start.html copy")
PY

# 6) Build dist includes start page
python3 scripts/build_sourcea_vercel_output_v1.py --json >/dev/null
[[ -f "$GREEN/dist/sourcea/start.html" ]] || { echo "FAIL: dist missing start.html"; exit 1; }
echo "OK: build dist"

echo "validate-sourcea-mvp-intake-e2e-v1.sh: ALL PASS"
