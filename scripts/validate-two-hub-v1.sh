#!/usr/bin/env bash
# validate-two-hub-v1.sh — H1 Super Fast + H2 Machine Hub health + sync
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-two-hub-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up at ${BASE}"

echo "== dual heal =="
python3 "${ROOT}/scripts/hub_dual_heal_v1.py" --json >/dev/null || fail "hub_dual_heal_v1"

echo "== H1 Super Fast =="
bash "${ROOT}/scripts/validate-super-fast-hub-v1.sh" || fail "validate-super-fast-hub-v1"

echo "== H2 Machine =="
bash "${ROOT}/scripts/validate-machine-hub-v1.sh" || fail "validate-machine-hub-v1"

python3 - <<'PY' "$BASE"
import json, os, urllib.request
base = os.environ.get("SINA_COMMAND_URL", "http://127.0.0.1:13020")
with urllib.request.urlopen(base + "/api/machine-hub/v1", timeout=8) as r:
    h2 = json.loads(r.read().decode())
health = h2.get("health") or {}
if health.get("schema") != "machine-hub-staleness-v1":
    raise SystemExit("H2 missing health block")
if health.get("status") not in ("fresh", "aging", "unknown"):
    raise SystemExit(f"H2 health bad: {health.get('status')} issues={health.get('issues')}")
print(f"OK: H2 health={health.get('status')} age={health.get('age_sec')} pending={h2.get('pending_total')}")
PY

echo "OK: validate-two-hub-v1 · H1 + H2 fresh"
