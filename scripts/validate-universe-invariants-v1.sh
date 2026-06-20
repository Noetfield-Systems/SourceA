#!/usr/bin/env bash
# validate-universe-invariants-v1.sh — semantic universe checks (Invariant OS fragment)
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"

python3 - <<'PY'
import json
import sys
from pathlib import Path

ROOT = Path.cwd()
SINA = Path.home() / ".sina"
RECEIPT = SINA / "rt-live-gate-receipt-v1.json"
GATE = SINA / "rt-live-gate-v1.json"
CMD = ROOT / "agent-control-panel" / "command-data.json"

sys.path.insert(0, str(ROOT / "scripts"))
from governance_event_spine_v1 import find_by_event_id  # noqa: E402
from founder_p0_next_action_v1 import rt_live_gate_active, DRAIN_HEADLINE_PATTERNS  # noqa: E402
from rt_live_gate_v1 import _verify_receipt_checksum  # noqa: E402

failures: list[str] = []


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


rec = load_json(RECEIPT)
gate = load_json(GATE)

if rec.get("gate") == "PASS":
    if not rec.get("spine_event_id"):
        failures.append("PASS receipt missing spine_event_id — run rt_live_gate_v1.py --bind-spine")
    elif not _verify_receipt_checksum(rec):
        failures.append("receipt checksum mismatch — hand-edited without cascade? re-prove or --bind-spine")
    else:
        row = find_by_event_id(str(rec["spine_event_id"]))
        if not row:
            failures.append(f"spine row missing for {rec['spine_event_id']}")
        elif str(row.get("proof") or "") != str(RECEIPT):
            failures.append("spine proof path does not point at rt-live-gate-receipt-v1.json")

if gate.get("status") == "pass" and rec.get("gate") != "PASS":
    failures.append("rt-live-gate-v1.json status=pass but receipt gate != PASS")

if rt_live_gate_active() and CMD.is_file():
    data = json.loads(CMD.read_text(encoding="utf-8"))
    p0 = (
        ((data.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    ).get("next_action") or ""
    if "RT LIVE" not in p0:
        failures.append(f"RT LIVE gate active but hub P0 missing RT LIVE: {p0[:80]!r}")
    low = p0.lower()
    for pat in DRAIN_HEADLINE_PATTERNS:
        if pat.lower() in low:
            failures.append(f"hub P0 contains drain pattern {pat!r} while RT LIVE gate active")
            break

if failures:
    for f in failures:
        print(f"FAIL: {f}")
    sys.exit(1)

print("OK: validate-universe-invariants-v1 · receipt↔spine · gate↔hero consistent")
PY
