#!/usr/bin/env bash
# validate-n8n-commercial-launch-v1.sh — full revenue kit on disk
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

for f in \
  n8n-commercial-sow-v1.json \
  n8n-commercial-sow-v1.html \
  n8n-commercial-email-templates-v1.json \
  n8n-commercial-outreach-v1.json \
  n8n-commercial-payments-v1.json; do
  [[ -f "$SINA/$f" ]] && check true "$f" || check false "$f"
done

[[ -f "$ROOT/archive/attachments/2026-06-15/N8N_COMMERCIAL_LAUNCH_BRIEF_LOCKED_v1.md" ]] \
  && check true "archive brief" || check false "archive brief"

python3 - <<'PY' || { echo "FAIL: outreach targets"; fail=1; }
import json
from pathlib import Path
o = json.loads((Path.home()/".sina/n8n-commercial-outreach-v1.json").read_text())
assert len(o.get("targets") or []) >= 10, len(o.get("targets") or [])
assert o.get("batch_size") == 10
print("PASS: outreach 10 targets")
PY

python3 - <<'PY' || { echo "FAIL: email templates"; fail=1; }
import json
from pathlib import Path
e = json.loads((Path.home()/".sina/n8n-commercial-email-templates-v1.json").read_text())
t = e.get("templates") or {}
for k in ("cold_agency", "audit_upsell", "followup_with_proof", "investor_diligence"):
    assert k in t and t[k].get("subject") and t[k].get("body"), k
print("PASS: email templates x4")
PY

python3 - <<'PY' || { echo "FAIL: stripe metadata"; fail=1; }
import json
from pathlib import Path
p = json.loads((Path.home()/".sina/n8n-commercial-payments-v1.json").read_text())
assert len(p.get("products") or []) >= 3
assert p.get("checkout_urls", {}).get("SKU-OPS-001_setup")
print("PASS: stripe payment metadata")
PY

python3 - <<'PY' || { echo "FAIL: sales pack launch_assets"; fail=1; }
import json
from pathlib import Path
sp = json.loads((Path.home()/".sina/n8n-commercial-sales-pack-v1.json").read_text())
assert sp.get("payment_links")
assert sp.get("launch_assets", {}).get("client_weekly")
print("PASS: sales pack wired")
PY

for f in n8n-commercial-client-sow-v1.html n8n-commercial-client-weekly-v1.html n8n-commercial-client-one-pager-v1.html n8n-commercial-client-readiness-v1.json; do
  [[ -f "$SINA/$f" ]] && check true "$f" || check false "$f"
done

python3 - <<'PY' || { echo "FAIL: client buy ready"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home()/".sina/n8n-commercial-client-readiness-v1.json").read_text())
assert r.get("client_buy_ready"), r.get("issues")
for p in (r.get("client_assets") or {}).values():
    t = Path(p).read_text()
    for bad in ("SKU-OPS", "WF1", "PLACEHOLDER", "LOCKED_v1"):
        assert bad not in t, (p, bad)
print("PASS: client_buy_ready")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-n8n-commercial-launch-v1"
  exit 0
fi
echo "FAIL: validate-n8n-commercial-launch-v1"
exit 1
