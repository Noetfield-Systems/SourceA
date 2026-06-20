#!/usr/bin/env bash
# validate-machine-hub-v1.sh — H2 /machines/ route + API
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-machine-hub-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"

code="$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/machines/")"
[[ "$code" == "200" ]] || fail "/machines/ HTTP $code (expected 200)"

html="$(curl -sf "${BASE}/machines/")"
echo "$html" | grep -q "Machine Hub" || fail "/machines/ missing Machine Hub title"
echo "$html" | grep -q "machine-hub/v1" || fail "/machines/ must fetch /api/machine-hub/v1"
echo "$html" | grep -q "health-pill" || fail "/machines/ missing health pill (H2 parity)"
echo "$html" | grep -q "sibling hub" || fail "/machines/ must declare sibling hub (not sub-page)"

python3 - <<'PY' || fail "machine-hub API schema"
import json, os, urllib.request
base = os.environ.get("SINA_COMMAND_URL", "http://127.0.0.1:13020")
with urllib.request.urlopen(base + "/api/machine-hub/v1", timeout=8) as r:
    d = json.loads(r.read().decode())
assert d.get("ok") is True
assert d.get("schema") == "machine-hub-v1"
assert d.get("hub") == "H2"
assert "health" in d
assert (d.get("health") or {}).get("schema") == "machine-hub-staleness-v1"
assert "buckets" in d
assert "next_phase" in (d.get("buckets") or {})
h = d.get("health") or {}
print(f"OK: machine-hub-v1 pending={d.get('pending_total')} form={d.get('form_live', {}).get('open_questions_count')} health={h.get('status')}")
PY

legacy_js="$(curl -s -o /dev/null -w '%{http_code}' --max-redirs 0 "${BASE}/legacy/assets/app.js")"
[[ "$legacy_js" == "301" || "$legacy_js" == "410" ]] || fail "/legacy/assets/app.js HTTP $legacy_js (legacy must redirect/410)"

echo "OK: validate-machine-hub-v1 · H2 route · API · legacy retired"
