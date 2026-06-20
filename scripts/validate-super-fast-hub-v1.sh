#!/usr/bin/env bash
# validate-super-fast-hub-v1.sh — default hub must stay light (no monolith on daily path)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-super-fast-hub-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up at ${BASE}"

# Default route serves worker hub HTML (not legacy index)
HUB_HTML="$(mktemp)"
trap 'rm -f "$HUB_HTML"' EXIT
curl -sf "${BASE}/" >"$HUB_HTML" || fail "default / unreachable"
grep -qE "Source A|Worker Hub|Super Fast Hub" "$HUB_HTML" || fail "default / is not Worker Hub"
grep -q 'function shortAlarm' "$HUB_HTML" || fail "worker-hub JS missing shortAlarm (syntax guard)"
grep -q 'fetchPayload' "$HUB_HTML" || fail "worker-hub JS missing fetchPayload (stability guard)"
test -f "$ROOT/agent-control-panel/worker-hub/boot.json" || fail "worker-hub/boot.json missing — run worker_hub_v1.py"
grep -q "command-data.json" "$HUB_HTML" && fail "default HTML must not prefetch command-data.json"

# API payload size cap (~2 KB typical, hard cap 16 KB)
bytes="$(curl -sf "${BASE}/api/worker-hub/v1" | wc -c | tr -d ' ')"
if [[ "$bytes" -gt 16384 ]]; then
  fail "worker-hub payload too large: ${bytes} bytes"
fi

python3 - <<'PY' || fail "worker-hub schema"
import json, os, urllib.request
base = os.environ.get("SINA_COMMAND_URL", "http://127.0.0.1:13020")
with urllib.request.urlopen(base + "/api/worker-hub/v1", timeout=5) as r:
    d = json.loads(r.read().decode())
assert d.get("ok") is True
assert d.get("schema") == "worker-hub-v1"
assert d.get("hub_mode") == "worker-only"
assert "h2_machines" in (d.get("actions") or {}) or (d.get("upgrade") or {}).get("h2_machines_url")
h = d.get("health") or {}
assert h.get("schema") == "worker-hub-staleness-v1"
assert h.get("status") in ("fresh", "aging", "stale", "critical", "unknown")
assert "auto_heal_recommended" in h
assert "dual_proof_ok" in (h.get("latches") or {}), "health latches missing dual_proof_ok"
dr = d.get("daily_rooms") or {}
assert dr.get("schema") == "worker-hub-daily-rooms-v1"
assert (dr.get("judge_center") or {}).get("id") == "judge-center"
assert (dr.get("thread_room") or {}).get("id") == "thread-room"
print(f"OK: worker-hub-v1 task={d.get('task_id')} bytes_ok freeze={d.get('freeze_status')} health={h.get('status')} judge={((dr.get('judge_center') or {}).get('headline') or '')[:30]}")
PY

# Light refresh must not return full command-data blob
refresh="$(curl -sf -X POST "${BASE}/refresh" -H "Content-Type: application/json" -d '{"mode":"light"}')"
echo "$refresh" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('mode')=='light' and d.get('ok'); print('OK: light refresh', d.get('built_at','')[:19])"

echo "OK: validate-super-fast-hub-v1 · default=Worker Hub · payload<16KB · light refresh"

# H2 sibling must resolve (SHIP — not daily load on H1)
h2_code="$(curl -s -o /dev/null -w '%{http_code}' "${BASE}/machines/")"
if [[ "$h2_code" != "200" ]]; then
  fail "H2 /machines/ HTTP $h2_code (expected 200)"
fi
echo "OK: H2 /machines/ reachable"
