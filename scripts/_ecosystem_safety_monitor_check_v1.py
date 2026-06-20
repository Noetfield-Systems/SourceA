#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from monitor_honesty_lib_v1 import audit_monitor, load_dual_proof_system  # noqa: E402

m = audit_monitor(filter_mode="road")
q = audit_monitor(filter_mode="queue")
y = m.get("you_are_here") or {}
integ = m.get("integrity") or {}
prog = m.get("progress") or {}
vy = int(prog.get("valid_yes") or 0)
hy_ok = bool(m.get("ok")) and int(m.get("unproven_done") or 0) == 0
dual = load_dual_proof_system(valid_yes=vy, hygiene_ok=hy_ok)

assert integ.get("broker_stale", -1) == 0, f"broker_stale={integ.get('broker_stale')}"
assert y.get("sa_id"), "you_are_here missing sa_id"
assert vy >= 1, "valid_yes missing"
assert dual.get("dual_proof_ok"), f"dual_proof={dual}"

qc = int((q.get("counts") or {}).get("showing") or 0)
if qc == 0 and y.get("sa_id"):
    raise SystemExit(
        f"queue tab empty but HERE={y.get('sa_id')} pos={y.get('queue_pos')} — pointer/filter bug"
    )
print(
    f"monitor: HERE={y.get('sa_id')} role={y.get('role')} "
    f"valid_yes={prog.get('valid_yes')} broker_stale=0 queue_rows={qc} dual_proof=True"
)
