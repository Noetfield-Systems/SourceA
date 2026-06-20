#!/usr/bin/env bash
# validate-h2-scheduled-cadence-up-pending-total-v1.sh — sa-0822 UP-01..UP-06 not in pending_total
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-scheduled-cadence-up-pending-total-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/2026-06-15/sa-0822-scheduled-cadence-up-pending-total_LOCKED_v1.md"
REG="${HOME}/.sina/h2-pending-registry-v1.json"
LAW="$ROOT/SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md"

[[ -f "$DOC" ]] || fail "missing LOCKED doc $DOC"
[[ -f "$REG" ]] || fail "missing registry $REG"
[[ -f "$LAW" ]] || fail "missing $LAW"
grep -q "scheduled_cadence UP-01" "$LAW" || grep -q "UP-01…UP-06" "$LAW" || fail "H2 plan missing slot 22 pointer"

python3 - <<'PY' || fail "scheduled cadence audit"
import copy
import json
import sys
from pathlib import Path

ROOT = Path(".")
DOC = ROOT / "archive/attachments/2026-06-15/sa-0822-scheduled-cadence-up-pending-total_LOCKED_v1.md"
REG = Path.home() / ".sina/h2-pending-registry-v1.json"

text = DOC.read_text(encoding="utf-8")
expected = [f"UP-{i:02d}" for i in range(1, 7)]
for needle in ("UP-01", "UP-06", "scheduled_cadence", "pending_total"):
    if needle not in text:
        raise SystemExit(f"LOCKED doc missing {needle}")

sys.path.insert(0, str(ROOT / "scripts"))
from h2_pending_count_lib_v1 import count_h2_pending, _maintainer_open  # noqa: E402
from machine_three_pipelines_lib_v1 import UPGRADE_BOARD  # noqa: E402

board_ids = [s["id"] for s in UPGRADE_BOARD]
if board_ids != expected:
    raise SystemExit(f"UPGRADE_BOARD ids mismatch: {board_ids}")

reg = json.loads(REG.read_text(encoding="utf-8"))
scheduled = list(reg.get("scheduled_cadence") or [])
sched_ids = [r.get("id") for r in scheduled if isinstance(r, dict)]
missing = [rid for rid in expected if rid not in sched_ids]
if missing:
    raise SystemExit(f"scheduled_cadence missing UP rows: {missing}")

for bucket in ("deferred", "next_phase", "ops_blocker"):
    bad = [r.get("id") for r in (reg.get(bucket) or []) if str(r.get("id", "")).startswith("UP-")]
    if bad:
        raise SystemExit(f"UP-* must not be in {bucket}: {bad}")

open_maint = [r for r in (reg.get("maintainer_ship") or []) if _maintainer_open(r)]
up_open = [r.get("id") for r in open_maint if str(r.get("id", "")).startswith("UP-")]
if up_open:
    raise SystemExit(f"UP-* must not be open maintainer_ship: {up_open}")

counts = count_h2_pending(reg)
if counts["scheduled_total"] < len(expected):
    raise SystemExit(
        f"scheduled_total {counts['scheduled_total']} < {len(expected)} for UP-01..06"
    )

# scheduled_cadence must not change pending_total (only scheduled_total)
reg_no_sched = copy.deepcopy(reg)
reg_no_sched["scheduled_cadence"] = []
counts_no = count_h2_pending(reg_no_sched)
if counts["pending_total"] != counts_no["pending_total"]:
    raise SystemExit(
        f"scheduled_cadence must not affect pending_total: "
        f"{counts['pending_total']} vs {counts_no['pending_total']}"
    )
if counts["scheduled_total"] <= counts_no["scheduled_total"]:
    raise SystemExit("scheduled_cadence must increase scheduled_total")

for rid in expected:
    if _maintainer_open({"id": rid, "status": "open"}):
        raise SystemExit(f"_maintainer_open must be False for {rid}")

print(
    f"OK: scheduled_cadence UP-01..06 · pending={counts['pending_total']} "
    f"scheduled={counts['scheduled_total']} · not in open pending"
)
PY

bash "$ROOT/scripts/validate-h2-pending-honest-count-v1.sh" >/dev/null || fail "h2 honest count"

echo "OK: validate-h2-scheduled-cadence-up-pending-total-v1 · sa-0822"
