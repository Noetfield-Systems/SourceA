#!/usr/bin/env bash
# worker_turn_entry_v1.sh — gate + fast anti-staleness auto-heal
set -euo pipefail
export SINA_WORKER_LOOP=1
export SINA_COMMERCIAL_LOOP=1
export SINA_BROKER_FAST=1
export SINA_BRAIN_FAST=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: worker_turn_entry_v1 — $*" >&2; exit 1; }

export GATE_RECEIPT="${HOME}/.sina/cursor_entry_gate_receipt_v1.json"
export WORKER_GATE_TTL_SEC="${WORKER_GATE_TTL_SEC:-1800}"

python3 cursor_entry_gate.py --role worker || fail "cursor_entry_gate"

python3 worker_stale_prompt_scrub_v1.py --json >/dev/null || true

python3 brain_fast_startup_v1.py --caller worker-turn-entry --json >/dev/null || fail "brain_fast_startup"

python3 anti_staleness_auto_wire_v1.py --role worker --tier worker --json >/dev/null || fail "anti-staleness auto wire L0.5→L1→L2"

python3 agent_session_gate_run_v1.py --role worker --worker-wire --json >/dev/null || {
  if [ "${SINA_WORKER_HEAL_ON_ENTRY:-1}" = "1" ]; then
    python3 outbound_disk_coherence_heal_v1.py --json >/dev/null || true
    python3 agent_session_gate_run_v1.py --role worker --worker-wire --json >/dev/null || fail "worker-wire after heal"
  else
    fail "worker-wire connected gate"
  fi
}

# UI FIRST CHECK — mandatory before ANY form/app/website UI edit (026 zero exception)
bash validate-ui-upgrade-first-check-live-wire-v1.sh >/dev/null || fail "UI FIRST CHECK live wire — run ui_upgrade_first_check_v1.py --wire"

python3 live_ongoing_prompts_v1.py --rebuild --json >/dev/null || true
python3 confirm_worker_inject_routing_v1.py --json >/dev/null 2>&1 || true

python3 worker_factory_heal_v1.py --json >/dev/null || fail "factory heal (honest registry + queue head)"

python3 governance_stairlift_sync_v1.py --if-stale --tier hot --json >/dev/null || fail "governance stairlift sync"

python3 worker_asf_directive_latch_v1.py block 2>/dev/null | head -8 || true

python3 founder_input_cascade_v1.py --verify-only --json >/dev/null 2>&1 || python3 founder_input_cascade_v1.py --source turn_entry_sync --json >/dev/null 2>&1 || true

if python3 - <<'PY'
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

p = Path(os.environ["GATE_RECEIPT"])
ttl = int(os.environ.get("WORKER_GATE_TTL_SEC", "600"))
if not p.is_file():
    sys.exit(1)
try:
    row = json.loads(p.read_text())
    at = row.get("at") or row.get("built_at") or ""
    if not at:
        sys.exit(1)
    dt = datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - dt).total_seconds()
    if age < ttl:
        print(f"OK: worker_turn_entry skip session-start (gate fresh {int(age)}s)")
        sys.exit(0)
except Exception:
    pass
sys.exit(1)
PY
then
  echo "OK: worker_turn_entry_v1 · gate + AS-heal (fresh gate)"
  exit 0
fi

python3 cursor_agent_self_audit.py session-start >/dev/null 2>&1 || true
bash validate-execution-spine-v1.sh >/dev/null 2>&1 || fail "execution-spine"
echo "OK: worker_turn_entry_v1 · gate + AS-heal + session-start (cold)"
