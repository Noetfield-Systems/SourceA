#!/usr/bin/env bash
# validate-worker-hub-live-v1.sh — fast API + heal endpoint + staleness wiring
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-worker-hub-live-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"

# Local payload build must stay fast (<400ms typical)
python3 - <<'PY' || fail "worker_hub_v1 slow or missing health"
import time, json, sys
sys.path.insert(0, "scripts")
from worker_hub_v1 import worker_hub_payload
t0 = time.perf_counter()
d = worker_hub_payload(skip_cache=True)
ms = (time.perf_counter() - t0) * 1000
assert d.get("ok") and d.get("health", {}).get("schema") == "worker-hub-staleness-v1"
if ms > 900:
    raise SystemExit(f"worker_hub_payload too slow: {ms:.0f}ms")
print(f"OK: worker_hub_payload {ms:.0f}ms health={d['health'].get('status')}")
PY

# Heal endpoint (may return 207 partial — must be JSON)
heal="$(curl -sf -X POST "${BASE}/api/worker-hub/heal" -H "Content-Type: application/json" -d '{"reason":"validator"}' || true)"
echo "$heal" | python3 -c "
import json, sys
d = json.load(sys.stdin)
schema = d.get('schema') or ''
assert schema in ('worker-anti-staleness-heal-v1', 'worker-hub-heal-v1'), schema
after = (d.get('health_after') or {}).get('status') or '?'
print('OK: heal endpoint', after, 'schema=' + schema)
" || fail "heal endpoint missing — restart hub (serve-sina-command)"

python3 - <<'PY' || fail "cloud_glance_line missing when Railway ok"
import json, sys, urllib.request
sys.path.insert(0, "scripts")
from worker_hub_v1 import worker_hub_payload
from mac_health_cloud_glance_v1 import probe as cloud_glance_probe

glance = cloud_glance_probe(write_receipt=False)
payload = worker_hub_payload(skip_cache=True)
line = payload.get("cloud_glance_line") or ""
if glance.get("railway_ok"):
    assert line.strip(), f"cloud_glance_line empty while railway_ok glance={glance.get('founder_line')!r}"
    assert "Cloud" in line or "Railway" in line or "comprehension" in line.lower(), line
    print("OK: worker hub cloud_glance_line when Railway ok:", line[:100])
else:
    print("WARN: Railway not ok — cloud_glance_line check skipped")
PY

echo "OK: validate-worker-hub-live-v1"
