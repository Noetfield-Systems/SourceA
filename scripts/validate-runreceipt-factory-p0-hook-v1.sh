#!/usr/bin/env bash
# sa-0514 — RunReceipt factory hook in command center P0 card
set -euo pipefail
cd "$(dirname "$0")/.."
DOC="archive/attachments/2026-06-14/sa-0514-runreceipt-factory-p0-hook_LOCKED_v1.md"
DATA="agent-control-panel/command-data.json"
test -f "$DOC" || { echo "FAIL: missing $DOC"; exit 1; }
test -f "$DATA" || { echo "FAIL: missing $DATA"; exit 1; }
python3 - <<'PY'
import json
from pathlib import Path

root = Path(".")
data = json.loads((root / "agent-control-panel/command-data.json").read_text(encoding="utf-8"))
p0 = (data.get("command_center") or {}).get("founder", {}).get("p0") or {}
assert p0.get("id") == "STRATEGIC-SLICE", p0.get("id")
rr = p0.get("runreceipt_parallel") or {}
assert rr.get("id") == "P0-RUNRECEIPT", rr
assert rr.get("thread") == "THREAD-FACTORY", rr
assert "RunReceipt" in (rr.get("title") or ""), rr.get("title")
prog = json.loads((root / "PROGRAM_PROGRESS.json").read_text(encoding="utf-8"))
plan = next((p for p in prog.get("parallel_plans", []) if p.get("id") == "P0-RUNRECEIPT"), None)
assert plan, "missing P0-RUNRECEIPT in PROGRAM_PROGRESS"
assert plan.get("thread") == "THREAD-FACTORY", plan.get("thread")
schema = root / "product/RUNRECEIPT_ARTIFACT_SCHEMA_LOCKED_v1.md"
assert schema.is_file(), schema
PY
echo "OK: validate-runreceipt-factory-p0-hook-v1 · sa-0514"
