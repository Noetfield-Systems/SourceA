#!/usr/bin/env bash
# validate-super-fast-hub-e2e-v1.sh — full H1+H2 E2E (founder daily path)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-super-fast-hub-e2e-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up — run serve-sina-command.sh"

echo "== dual hub validators =="
bash "${ROOT}/scripts/validate-two-hub-v1.sh" || fail "validate-two-hub-v1"

echo "== H1 fast safety (L2 tier) =="
bash "${ROOT}/scripts/validate-ecosystem-safety-h1-fast-v1.sh" || fail "validate-ecosystem-safety-h1-fast-v1"

echo "== API smoke =="
python3 - <<'PY' "$BASE"
import json, os, sys, urllib.request
base = sys.argv[1]

def post(path, body, timeout=45):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

heal = post("/api/worker-hub/heal", {"reason": "e2e"})
assert heal.get("schema") in ("worker-anti-staleness-heal-v1", "worker-hub-heal-v1"), heal.get("schema")
print("OK: heal", (heal.get("health_after") or {}).get("status"))

rooms = post("/api/worker-hub/rooms/run", {"room": "strip"}, timeout=120)
assert rooms.get("ok") is not None
print("OK: rooms strip", len(rooms.get("steps") or []))

with urllib.request.urlopen(base + "/api/hub-sync", timeout=15) as r:
    sync = json.loads(r.read().decode())
assert sync.get("ok") and sync.get("built_at")
print("OK: hub-sync", sync.get("built_at", "")[:19])
PY

echo "OK: validate-super-fast-hub-e2e-v1 · H1+H2+safety+API smoke PASS"
