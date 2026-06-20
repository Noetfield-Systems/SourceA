#!/usr/bin/env bash
# validate-founder-directive-propagation-v1.sh — ASF order on every layer (INCIDENT-031 fix)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-founder-directive-propagation-v1 — $*" >&2; exit 1; }

[[ -f founder_directive_ssot_v1.py ]] || fail "missing founder_directive_ssot_v1.py"
grep -q 'founder_input_cascade_v1\|founder_directive_ssot_v1' worker_turn_entry_v1.sh || fail "turn entry missing founder cascade"
grep -q 'founder_directive_ssot_v1' incident_fix_ownership_lib_v1.py || fail "stairlift payload missing founder_directive"
grep -q 'founder_directive_ssot_v1' run_inbox_disk_truth_v1.py || fail "disk truth missing founder block"
grep -q 'founder_directive_ssot_v1' monitor_honesty_lib_v1.py || fail "monitor missing founder rail"
grep -q 'HUB_CLOSED_LATCH\|founder_directive_ssot' worker_inject_lib.py || fail "inject missing hub block"
grep -q 'RUNTIME_WATCH' governance_stairlift_sync_v1.py || fail "stairlift missing runtime watch"

python3 founder_directive_ssot_v1.py --sync-all --json >/dev/null || fail "sync-all"

python3 - <<'PY' || fail "layer audit"
import json, sys
from pathlib import Path

SINA = Path.home() / ".sina"
errors = []

lat = json.loads((SINA / "worker-asf-directive-latch-v1.json").read_text())
if lat.get("no_hub"):
    sl = json.loads((SINA / "governance-stairlift-v1.json").read_text())
    if not sl.get("no_hub"):
        errors.append("stairlift missing no_hub")
    if not sl.get("founder_directive"):
        errors.append("stairlift missing founder_directive")
    rt = json.loads((SINA / "run-inbox-routing-v1.json").read_text())
    order = rt.get("order") or ""
    if not any(tok in order for tok in ("ARCHIVED", "RETIRED", "QUARANTINE")):
        errors.append("routing missing hub-closed rail (ARCHIVED/RETIRED/QUARANTINE)")
    ib = json.loads((SINA / "worker-prompt-inbox-v1.json").read_text())
    if "FOUNDER DIRECTIVE" not in (ib.get("prompt") or ""):
        errors.append("INBOX missing FOUNDER DIRECTIVE block")

if errors:
    print("\n".join(errors), file=sys.stderr)
    sys.exit(1)
print("OK: founder directive layers aligned")
PY

echo "OK: validate-founder-directive-propagation-v1"
