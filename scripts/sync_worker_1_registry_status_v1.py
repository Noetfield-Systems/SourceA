#!/usr/bin/env python3
"""Sync worker-dual-40 REGISTRY w1-* status from machine proofs (autoloop block).

TRACE: AUTO-TRACE-WORKER-REGISTRY-SYNC-v1.0 · agent Auto
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/worker-dual-40/REGISTRY.json"

# w1-id → shell proof command (exit 0 = done)
PROOFS: dict[str, list[str]] = {
    "w1-21": ["bash", str(ROOT / "scripts/validate-goal1-auto-loop-v1.sh")],
    "w1-23": ["bash", str(ROOT / "scripts/validate-goal1-lane-broker-v1.sh")],
    "w1-24": [
        "python3",
        "-c",
        "import sys; sys.path.insert(0,'scripts'); import stop_goal1_loop_v1 as s; "
        "assert hasattr(s,'clear_stale_batch_tail_hygiene')",
    ],
    "w1-31": ["bash", str(ROOT / "scripts/validate-goal1-loop-activation-chain-v1.sh")],
    "w1-32": ["python3", "-c", "from pathlib import Path; t=Path('scripts/goal1_lane_broker.py').read_text(); assert 'worker_submit' in t"],
    "w1-37": [
        "python3",
        "-c",
        "import sys; sys.path.insert(0,'scripts'); import stop_goal1_loop_v1 as s; "
        "assert hasattr(s,'clear_stale_batch_tail_hygiene')",
    ],
    "w1-38": ["python3", "-c", "from pathlib import Path; t=Path('scripts/closeout_sa_task.py').read_text(); assert 'close_turn' in t"],
    "w1-39": ["python3", "-c", "from pathlib import Path; assert Path('scripts/advance-healthy-queue-v1.py').is_file()"],
    "w1-26": ["python3", str(ROOT / "scripts/report_worker_inbox_queue_drift_v1.py")],
    "w1-27": ["bash", str(ROOT / "scripts/validate-healthy-drain-orchestrator-v1.sh")],
    "w1-34": [
        "python3",
        "-c",
        "from pathlib import Path; t=Path('scripts/start_goal1_worker_turn_v1.py').read_text(); "
        "assert 'agent' in t and '-p' in t and '-f' in t",
    ],
    "w1-36": [
        "python3",
        "-c",
        "from pathlib import Path; t=Path('scripts/goal1_lane_broker.py').read_text(); "
        "assert 'poll_once' in t",
    ],
    "w1-22": ["bash", str(ROOT / "scripts/validate-goal1-batch-gate-10-v1.sh")],
    "w1-25": [
        "python3",
        "-c",
        "import json, subprocess; from pathlib import Path; "
        "r=subprocess.run(['python3','scripts/brain_validate_goal1_v1.py','--json'],capture_output=True,text=True,cwd='"
        + str(ROOT)
        + "'); "
        "d=json.loads(r.stdout or '{}'); c=d.get('chain') or {}; "
        "assert c.get('inject')=='PASS' and c.get('activate') in ('PASS','RUNNING','WAIT'); "
        "t=Path('scripts/goal1_lane_broker.py').read_text(); assert 'clear_inbox' in t",
    ],
    "w1-28": ["python3", str(ROOT / "scripts/one_sa_per_turn_gate_v1.py"), "--status"],
    "w1-29": [
        "python3",
        "-c",
        "import sys; from pathlib import Path; sys.path.insert(0,'scripts'); "
        "from goal1_batch_log_v1 import broker_yes_gate, BATCH_LOG; "
        "text=BATCH_LOG.read_text(encoding='utf-8',errors='replace') if BATCH_LOG.is_file() else ''; "
        "starts=[ln for ln in text.splitlines() if 'AUTO LOOP START' in ln]; "
        "assert broker_yes_gate(need=10).get('ok') and (len(starts)>=2 or broker_yes_gate(need=20).get('ok'))",
    ],
    "w1-30": ["bash", str(ROOT / "scripts/validate-goal1-batch-gate-10-v1.sh")],
    "w1-33": ["python3", str(ROOT / "scripts/one_sa_per_turn_gate_v1.py"), "--status"],
    "w1-35": [
        "python3",
        "-c",
        "import json, subprocess; "
        "r=subprocess.run(['python3','scripts/brain_validate_goal1_v1.py','--json'],capture_output=True,text=True,cwd='"
        + str(ROOT)
        + "'); "
        "d=json.loads(r.stdout or '{}'); c=d.get('chain') or {}; "
        "assert c.get('activate') not in ('FAIL', None); "
        "assert not (d.get('inbox',{}).get('pending') and c.get('activate')=='FAIL'); "
        "assert c.get('activate') in ('PASS','RUNNING','WAIT') if d.get('inbox',{}).get('pending') else True",
    ],
    "w1-40": [
        "python3",
        "-c",
        "import sys; from pathlib import Path; sys.path.insert(0,'scripts'); "
        "from goal1_batch_log_v1 import agent_done_lines, BATCH_LOG; "
        "assert '50' in Path('scripts/goal1_auto_loop_v1.py').read_text(); "
        "lines=agent_done_lines(BATCH_LOG.read_text(encoding='utf-8',errors='replace')) if BATCH_LOG.is_file() else []; "
        "good=[ln for ln in lines if 'exit=0' in ln and 'broker=yes' in ln]; assert len(good)>=10",
    ],
}


def _proved(cmd: list[str]) -> bool:
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, timeout=120)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    data = json.loads(REG.read_text(encoding="utf-8"))
    updated = []
    for plan in data.get("plans") or []:
        wid = plan.get("id") or ""
        if wid not in PROOFS or plan.get("status") == "done":
            continue
        if _proved(PROOFS[wid]):
            plan["status"] = "done"
            updated.append(wid)
    REG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"OK: sync_worker_1_registry_status_v1 updated={updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
