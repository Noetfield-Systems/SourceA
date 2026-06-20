#!/usr/bin/env bash
# P0 E2E hardening — factory lock + synthesis eval sync from disk
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

test -f "$SCRIPTS/factory_validation_lock_v1.py"
test -f "$SCRIPTS/eval_report_capture.py"
grep -q "sync_synthesis_eval_line_from_disk" "$SCRIPTS/eval_report_capture.py"
grep -q "factory_validation_lock_v1" "$SCRIPTS/validate-sourcea-e2e-full-v1.sh"
grep -q "factory_validation_lock_v1" "$SCRIPTS/validate-goal1-e2e-v1.sh"
grep -q "sync_synthesis_eval_line_from_disk" "$SCRIPTS/build-sina-command-panel.py"

bash "$SCRIPTS/validate-cross-lane-edit-v1.sh" >/dev/null
bash "$SCRIPTS/validate-factory-e2e-protection-v1.sh" >/dev/null

python3 - <<'PY'
import json
import sys
from pathlib import Path

scripts = Path("scripts")
sys.path.insert(0, str(scripts))
from factory_validation_lock_v1 import acquire, release  # noqa: E402

release(holder="test_p0")
ac = acquire(holder="test_p0")
assert ac["ok"], ac
blk = acquire(holder="other")
assert not blk["ok"], blk
release(holder="test_p0")

# synthesis sync round-trip on temp copy logic
sys.path.insert(0, str(scripts))
from eval_report_capture import sync_synthesis_eval_line_from_disk, SYNTHESIS_PATH, REPORT_PATH  # noqa: E402

if not REPORT_PATH.is_file():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "schema": "eval-packet-v1b",
                "mode": "live",
                "live_ok": True,
                "ok": True,
                "live_pilot_wins": 4,
                "live_pilot_count": 5,
                "live_pilot_win_pct": 80,
            }
        )
        + "\n",
        encoding="utf-8",
    )
rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
wins = int(rep.get("live_pilot_wins") or rep.get("packet_wins") or 0)
count = int(rep.get("live_pilot_count") or rep.get("task_count") or 0)
pct = int(rep.get("live_pilot_win_pct") or rep.get("packet_win_pct") or 0)
ratio = f"{wins}/{count}"
orig = SYNTHESIS_PATH.read_text(encoding="utf-8")
try:
    row = sync_synthesis_eval_line_from_disk(strict=True)
    assert row.get("ok"), row
    text = SYNTHESIS_PATH.read_text(encoding="utf-8")
    assert ratio in text and f"{pct}%" in text, f"synthesis missing disk ratio {ratio} {pct}%"
finally:
    SYNTHESIS_PATH.write_text(orig, encoding="utf-8")
PY

echo "PASS: validate-e2e-hardening-p0-v1"
