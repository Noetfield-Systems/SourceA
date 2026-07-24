#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 scripts/sourcea_plan_traceability_machine_v1.py --json --no-live --limit 25 >/tmp/sourcea-plan-traceability-machine-v1.json

python3 - <<'PY'
import json
from pathlib import Path

row = json.loads(Path("/tmp/sourcea-plan-traceability-machine-v1.json").read_text(encoding="utf-8"))
assert row.get("schema") == "sourcea-plan-traceability-machine-receipt-v1"
assert row.get("ok") is True
assert row.get("summary", {}).get("total", 0) > 0
assert "threads_needing_follow_up" in row.get("summary", {})
assert "rows_needing_follow_up" in row.get("summary", {})
assert row.get("git_scope", {}).get("changed_files") is not None
assert row.get("live_probe", {}).get("skipped") is True
assert row.get("rows") and all("trace_state" in r for r in row["rows"])
assert all("needs_follow_up" in r and "evidence_quality" in r for r in row["rows"])
print("validate-sourcea-plan-traceability-machine-v1 PASS")
PY
