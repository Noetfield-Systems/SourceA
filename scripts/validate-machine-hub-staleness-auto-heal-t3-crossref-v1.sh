#!/usr/bin/env bash
# validate-machine-hub-staleness-auto-heal-t3-crossref-v1.sh — sa-0887 T3 spike cross-ref → canonical sa-0812
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-machine-hub-staleness-auto-heal-t3-crossref-v1 — $*" >&2; exit 1; }

PROMPT="$ROOT/brain-os/plan-registry/sourcea-1000/prompts/phase-s8-hub-ui-ux/T3/sa-0887.md"
T2_CROSS="$ROOT/archive/attachments/2026-06-15/sa-0862-machine-hub-staleness-auto-heal-t2-crossref_LOCKED_v1.md"
CANONICAL="$ROOT/scripts/validate-machine-hub-staleness-auto-heal-v1.sh"
T2_SCRIPT="$ROOT/scripts/validate-machine-hub-staleness-auto-heal-t2-crossref-v1.sh"

[[ -f "$PROMPT" ]] || fail "missing sa-0887 prompt"
[[ -f "$T2_CROSS" ]] || fail "missing sa-0862 T2 cross-ref doc"
[[ -f "$CANONICAL" ]] || fail "missing canonical validator"
[[ -f "$T2_SCRIPT" ]] || fail "missing T2 cross-ref validator"

python3 - <<'PY' || fail "sa-0887 prompt audit"
from pathlib import Path

prompt = Path("../brain-os/plan-registry/sourcea-1000/prompts/phase-s8-hub-ui-ux/T3/sa-0887.md")
text = prompt.read_text(encoding="utf-8")
for needle in (
    "sa-0887",
    "machine_hub_staleness_v1",
    "auto-heal",
    "phase-s8-hub-ui-ux",
):
    if needle not in text:
        raise SystemExit(f"prompt missing {needle}")
print("OK: sa-0887 prompt cites machine_hub_staleness auto-heal task")
PY

bash "$T2_SCRIPT" >/dev/null || fail "T2 echo chain sa-0862"

python3 - <<'PY' || fail "live auto-heal wiring"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".").resolve()))
from machine_hub_staleness_v1 import machine_hub_staleness_probe  # noqa: E402

hub_src = Path("machine_hub_v1.py").read_text(encoding="utf-8")
if "_maybe_sync_registry" not in hub_src or "sync_h2_registry" not in hub_src:
    raise SystemExit("machine_hub_v1 missing sync_h2_registry auto-heal gate")

heal_src = Path("worker_anti_staleness_heal_v1.py").read_text(encoding="utf-8")
if "h2_health_before" not in heal_src or "sync_h2_registry" not in heal_src:
    raise SystemExit("worker_anti_staleness_heal missing H2 sync path")

row = machine_hub_staleness_probe()
if row.get("schema") != "machine-hub-staleness-v1":
    raise SystemExit(f"bad probe schema: {row.get('schema')}")
if "auto_heal_recommended" not in row:
    raise SystemExit("probe missing auto_heal_recommended")

receipt = Path.home() / ".sina/worker-anti-staleness-heal-receipt-v1.json"
if receipt.is_file():
    rec = json.loads(receipt.read_text(encoding="utf-8"))
    if rec.get("reason") and "0887" not in str(rec.get("reason")):
        print(f"WARN: latest heal reason={rec.get('reason')} (not sa-0887)")
print(
    f"OK: live probe status={row.get('status')} auto_heal={row.get('auto_heal_recommended')} "
    f"form_aligned={row.get('form_aligned')}"
)
PY

echo "OK: validate-machine-hub-staleness-auto-heal-t3-crossref-v1 · canonical=sa-0812 · sa-0887"
