#!/usr/bin/env bash
# HUB_PROOF_UX_P0_LOCKED_v1.md — proof_counter, export API, overnight verify (HUB-P0-1/2/3)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-hub-proof-ux-p0-v1 — $*"; exit 1; }

grep -q "proof_counter" "$ROOT/scripts/hub_home_founder_view_v1.py" || fail "hub_home_founder_view missing proof_counter"
grep -q "program-1000-honest-status-v1" "$ROOT/scripts/hub_home_founder_view_v1.py" || fail "proof_counter must use program-1000-honest-status-v1"
grep -q "def export_chain" "$ROOT/scripts/event_chain_export_v1.py" || fail "event_chain_export_v1.py missing export_chain"
grep -q "/api/event-chain-export-v1" "$ROOT/scripts/sina-command-server.py" || fail "event-chain-export API missing"
grep -q "MAX_TURNS = 5" "$ROOT/scripts/overnight_verify_readonly_v1.py" || fail "overnight_verify_readonly_v1.py missing"
grep -q "founder-overnight-verify-readonly" "$ROOT/scripts/sina_command_lib.py" || fail "overnight action missing in sina_command_lib"
grep -q "founder-export-event-chain" "$ROOT/scripts/sina_command_lib.py" || fail "export action missing in sina_command_lib"
grep -q "sc-home-founder-proof" "$ROOT/agent-control-panel/assets/app.js" || fail "app.js proof UI missing"
grep -q "sc-proof-kill" "$ROOT/agent-control-panel/assets/app.css" || fail "app.css proof kill chip missing"

python3 - <<PY
import json
import sys
from pathlib import Path

ROOT = Path("${ROOT}")

sys.path.insert(0, str(ROOT / "scripts"))
from hub_home_founder_view_v1 import hub_home_founder_payload

hfv = hub_home_founder_payload()
errors: list[str] = []

pc = hfv.get("proof_counter") or {}
for key in ("verified_done", "total", "pct", "unproven_done", "kill"):
    if pc.get(key) is None and key != "unproven_done":
        errors.append(f"proof_counter.{key} missing")
if pc.get("kill") not in ("RED", "GREEN"):
    errors.append(f"proof_counter.kill must be RED or GREEN got {pc.get('kill')!r}")

pe = hfv.get("proof_export") or {}
if not pe.get("api", "").startswith("/api/event-chain-export-v1"):
    errors.append("proof_export.api must be /api/event-chain-export-v1?...")

action_ids = {a.get("id") for a in hfv.get("actions") or []}
for aid in ("founder-export-event-chain", "founder-overnight-verify-readonly"):
    if aid not in action_ids:
        errors.append(f"actions missing {aid}")

from event_chain_export_v1 import export_chain

sa = pe.get("sa_id") or "sa-0001"
_, meta = export_chain(sa, customer=True)
if "has_worker_started" not in meta:
    errors.append("export_chain meta missing has_worker_started")

if errors:
    print("FAIL: validate-hub-proof-ux-p0-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: validate-hub-proof-ux-p0-v1")
print(f"  verified_done={pc.get('verified_done')} kill={pc.get('kill')} export_sa={pe.get('sa_id')}")
PY

# Live API smoke when hub is up (optional — skip if down)
if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  SA=$(python3 -c "import json;from pathlib import Path;t=json.loads((Path.home()/'.sina'/'run-inbox-disk-truth-v1.json').read_text());print((t.get('queue')or{}).get('sa_id')or'sa-0001')" 2>/dev/null || echo "sa-0001")
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:13020/api/event-chain-export-v1?sa_id=${SA}&customer=1" || echo "000")
  if [[ "$CODE" != "200" && "$CODE" != "400" ]]; then
    fail "event-chain-export API returned HTTP $CODE"
  fi
  echo "  api_smoke=ok http=$CODE sa=$SA"
else
  echo "  api_smoke=skipped (hub not running)"
fi
