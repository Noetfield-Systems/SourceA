#!/usr/bin/env bash
# sa-0517 — PRODUCT_FACTORY roadmap vs hub progress signals cross-check
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0517-product-factory-roadmap-hub-signals_LOCKED_v1.md"
ROADMAP="PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$ROADMAP" || { echo "FAIL: missing $ROADMAP"; exit 1; }
python3 - <<'PY'
import json
from pathlib import Path

pp = json.loads(Path("PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
cd = json.loads(Path("agent-control-panel/command-data.json").read_text(encoding="utf-8"))

pfh = (pp.get("signals_auto") or {}).get("product_factory_hub") or {}
for key in ("roadmap_doc", "crossref_doc", "aligned", "two_speed_note"):
    if key not in pfh:
        raise SystemExit(f"FAIL: signals_auto.product_factory_hub missing {key}")
if "sa-0517-product-factory-roadmap" not in str(pfh.get("crossref_doc", "")):
    raise SystemExit("FAIL: crossref_doc must point to sa-0517 attachment")

locks = pp.get("locks") or {}
if locks.get("founder_p0_id") != "STRATEGIC-SLICE":
    raise SystemExit(f"FAIL: founder_p0_id {locks.get('founder_p0_id')}")
if locks.get("p0_sku") != "RunReceipt":
    raise SystemExit(f"FAIL: p0_sku {locks.get('p0_sku')}")

plans = {p.get("id"): p for p in pp.get("parallel_plans", [])}
for pid in ("MERGEPACK-L1", "P0-RUNRECEIPT"):
    if pid not in plans:
        raise SystemExit(f"FAIL: missing parallel_plan {pid}")

p0 = (cd.get("command_center") or {}).get("founder", {}).get("p0") or {}
rr = p0.get("runreceipt_parallel") or {}
if rr.get("id") != "P0-RUNRECEIPT":
    raise SystemExit(f"FAIL: runreceipt_parallel {rr}")

blob = json.dumps(cd)
if "MERGEPACK" not in blob.upper():
    raise SystemExit("FAIL: command-data missing MERGEPACK signal")

print("OK: validate-product-factory-roadmap-hub-signals-v1 · sa-0517")
PY
