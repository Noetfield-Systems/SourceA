#!/usr/bin/env bash
# sa-0521 — commercial attests checklist in SOURCEA-PRIORITY founder section
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0521-commercial-attests-priority-founder_LOCKED_v1.md"
PRIORITY="brain-os/plan-registry/SOURCEA-PRIORITY.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$PRIORITY" || { echo "FAIL: missing $PRIORITY"; exit 1; }
bash scripts/validate-commercial-critique-program-progress-locks-v1.sh
python3 - <<'PY'
import json
import re
from pathlib import Path

priority = Path("brain-os/plan-registry/SOURCEA-PRIORITY.md").read_text(encoding="utf-8")
if "## Founder commercial attests" not in priority:
    raise SystemExit("FAIL: SOURCEA-PRIORITY missing Founder commercial attests section")
for sa in (f"sa-051{i}" for i in range(2, 10)):
    if sa not in priority:
        raise SystemExit(f"FAIL: founder section missing {sa}")
if "sa-0520" not in priority:
    raise SystemExit("FAIL: founder section missing sa-0520")
if "validate-commercial-attests-priority-v1" not in priority:
    raise SystemExit("FAIL: founder section missing validator pointer")

for sa in [f"sa-051{i}" for i in range(2, 10)] + ["sa-0520"]:
    rec = Path(f"receipts/{sa}-receipt.json")
    if not rec.is_file():
        raise SystemExit(f"FAIL: missing receipt {rec}")
    data = json.loads(rec.read_text(encoding="utf-8"))
    if data.get("status") != "DONE":
        raise SystemExit(f"FAIL: {sa} receipt status {data.get('status')!r}")

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
sig = pp.get("signals_auto") or {}
cac = sig.get("commercial_attests_checklist") or {}
for key in ("crossref_doc", "priority_section", "lane_sas", "pack"):
    if key not in cac:
        raise SystemExit(f"FAIL: signals_auto.commercial_attests_checklist missing {key}")
if "sa-0521-commercial-attests" not in str(cac.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0521 attachment")
lane = cac.get("lane_sas") or []
expected = [f"sa-051{i}" for i in range(2, 10)] + ["sa-0520"]
if lane != expected:
    raise SystemExit(f"FAIL: lane_sas {lane!r} expected {expected!r}")

for sa in ["sa-0512", "sa-0516", "sa-0517", "sa-0518", "sa-0519", "sa-0520", "sa-0521"]:
    if sa not in priority:
        raise SystemExit(f"FAIL: evidence log missing {sa}")

print("OK: validate-commercial-attests-priority-v1 · sa-0521")
PY
