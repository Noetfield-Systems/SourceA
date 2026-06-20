#!/usr/bin/env bash
# validate-n8n-commercial-grade-v1.sh — sellable SKU gate (outcomes + receipts)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/N8N_COMMERCIAL_GRADE_LOCKED_v1.md" ]] && check true "commercial law doc" || check false "N8N_COMMERCIAL_GRADE_LOCKED_v1.md"
[[ -f "$ROOT/scripts/n8n_commercial_grade_v1.py" ]] && check true "commercial grade script" || check false "script missing"

python3 "$ROOT/scripts/n8n_commercial_grade_v1.py" --upgrade --json >/dev/null
python3 "$ROOT/scripts/n8n_commercial_grade_v1.py" --pack --json >/dev/null

[[ -f "$SINA/n8n-commercial-grade-v1.json" ]] && check true "commercial grade receipt" || check false "receipt missing"
[[ -f "$SINA/n8n-commercial-sales-pack-v1.json" ]] && check true "sales pack" || check false "sales pack missing"

python3 - <<'PY' || { echo "FAIL: sales pack launch_assets"; fail=1; }
import json
from pathlib import Path
sp = json.loads((Path.home()/".sina/n8n-commercial-sales-pack-v1.json").read_text())
assert sp.get("payment_links")
assert sp.get("launch_assets", {}).get("sow_html")
print("PASS: sales pack launch_assets")
PY

python3 - <<'PY' || { echo "FAIL: commercial meta on WF8"; fail=1; }
import json
from pathlib import Path
p = Path("/Users/sinakazemnezhad/Desktop/SourceA/n8n/workflows/wf-mac-health-cooldown-v1.json")
d = json.loads(p.read_text())
c = (d.get("meta") or {}).get("commercial") or {}
assert c.get("sku_id") == "SKU-SOLO-001", c
assert c.get("setup_usd") == 0
assert c.get("monthly_usd") == 99
print("PASS: WF8 commercial meta")
PY

[[ -f "$SINA/n8n-receipts/health/tier0-pass.json" ]] && check true "tier0 pass" || check false "tier0"
[[ -f "$SINA/n8n-receipts/health/tier1-pass.json" ]] && check true "tier1 pass" || check false "tier1"

ready=$(python3 -c "import json; print('true' if json.load(open('$SINA/n8n-commercial-grade-v1.json')).get('commercial_ready') else 'false')")
check "$ready" "commercial_ready flag"

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-n8n-commercial-grade-v1"
  exit 0
fi
echo "FAIL: validate-n8n-commercial-grade-v1"
exit 1
