#!/usr/bin/env bash
# Mechanical gate: monitor labels + broker cycle law + progress counter (INCIDENT-006).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

python3 - <<'PY'
import json
import sys

sys.path.insert(0, ".")
from monitor_honesty_lib_v1 import audit_monitor, load_dual_proof_system, quarantine_batch_yaml_on_honest_done

# Auto-hygiene: quarantine stale batch YAML beside honest receipts
q = quarantine_batch_yaml_on_honest_done(dry_run=False)
if q.get("file_count"):
    print(f"OK: quarantined {q['file_count']} stale batch YAML on {q['sa_count']} honest-done sas")

d = audit_monitor(filter_mode="road")
i = d.get("integrity") or {}
errors = []

if d.get("unproven_done", 0) != 0:
    errors.append(f"unproven_done={d['unproven_done']}")
if i.get("backlog_broker_pass", 0) != 0:
    errors.append(f"backlog_broker_pass={i['backlog_broker_pass']}")
if i.get("active_batch_yaml_on_honest_done", 0) != 0:
    errors.append(f"active_batch_yaml_on_honest={i['active_batch_yaml_on_honest_done']}")
if not i.get("valid_yes_matches_map_done"):
    errors.append(
        f"valid_yes={d['progress']['valid_yes']} map_done={d['counts']['done_both']} mismatch"
    )

prog = d.get("progress") or {}
vy = int(prog.get("valid_yes") or 0)
hy_ok = bool(d.get("ok")) and int(d.get("unproven_done") or 0) == 0
dual = load_dual_proof_system(valid_yes=vy, hygiene_ok=hy_ok)
if not dual.get("dual_proof_ok"):
    brain_vy = (dual.get("brain") or {}).get("valid_yes")
    # INCIDENT-014: factory-now / receipts can advance before brain snapshot — auto-sync once
    if brain_vy is not None and brain_vy != vy:
        import os

        os.environ.setdefault("SINA_BRAIN_FAST", "1")
        from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

        healed = sync_brain_snapshot(mode="light", caller="validate_monitor_honesty")
        if healed.get("ok"):
            d = audit_monitor(filter_mode="road")
            prog = d.get("progress") or {}
            vy = int(prog.get("valid_yes") or 0)
            hy_ok = bool(d.get("ok")) and int(d.get("unproven_done") or 0) == 0
            dual = load_dual_proof_system(valid_yes=vy, hygiene_ok=hy_ok)
            brain_vy = (dual.get("brain") or {}).get("valid_yes")
            if dual.get("dual_proof_ok"):
                print(
                    f"OK: auto brain_sync · brain_vy {healed.get('before', {}).get('brain_vy')} "
                    f"→ {brain_vy} (live_vy={vy})"
                )
    if not dual.get("dual_proof_ok"):
        brain_vy = (dual.get("brain") or {}).get("valid_yes")
        errors.append(f"dual_proof GAP brain_vy={brain_vy} live_vy={vy}")

print(
    f"OK: monitor honesty · Valid YES {prog.get('valid_yes')}/1000 ({prog.get('pct')}%) · "
    f"receipts {d.get('receipt_done')} · STALE broker {i.get('broker_stale')} · "
    f"PARTIAL {d['counts'].get('valid_partial', 0)}"
)

if errors:
    print("FAIL: " + "; ".join(errors), file=sys.stderr)
    sys.exit(1)
PY

echo "OK: validate-monitor-honesty-v1"
