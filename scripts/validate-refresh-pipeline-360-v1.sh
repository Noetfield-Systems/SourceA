#!/usr/bin/env bash
# validate-refresh-pipeline-360-v1.sh — sa-0853 refresh E2E budget ≤360s
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
e2e = (ROOT / "scripts" / "audit_backend_e2e.py").read_text(encoding="utf-8")
light = (ROOT / "scripts" / "audit_backend_e2e_light_v1.py").read_text(encoding="utf-8")

assert "REFRESH_E2E_BUDGET_SEC = 360" in e2e, "audit_backend_e2e missing 360s budget (sa-0853)"
assert "sa-0853" in e2e, "sa-0853 marker missing in audit_backend_e2e"
assert '"mode": "light"' in e2e or "'mode': 'light'" in e2e, "audit_backend_e2e must use light refresh"
assert "REFRESH_E2E_BUDGET_SEC = 360" in light, "audit_backend_e2e_light missing 360s budget"
assert "refresh-light" in light and "expect=200" in light, "light E2E must expect HTTP 200"

t0 = time.time()
req = urllib.request.Request(
    "http://127.0.0.1:13020/refresh",
    data=json.dumps({"mode": "light"}).encode(),
    method="POST",
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=30) as resp:
    body = json.loads(resp.read().decode())
    elapsed = time.time() - t0
assert resp.status == 200, f"light refresh HTTP {resp.status}"
assert body.get("ok"), body
assert elapsed <= 360, f"live light refresh {elapsed:.1f}s > 360s"

print(
    f"OK: validate-refresh-pipeline-360-v1 · light refresh {elapsed:.2f}s ≤ 360s "
    f"· mode={body.get('mode')} (sa-0853)"
)
PY
