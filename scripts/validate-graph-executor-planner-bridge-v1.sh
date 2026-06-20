#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
from pathlib import Path

app = Path(__file__).resolve().parents[1] / "agent-control-panel" / "assets" / "app.js"
src = app.read_text(encoding="utf-8")
assert "function renderGraphExecutorPanel" in src, "renderGraphExecutorPanel missing"
assert "sa-0308" in src, "sa-0308 marker missing"
assert "sa-0358" in src, "sa-0358 marker missing"
assert "planner_bridge_ready" in src and "first_action_id" in src, "planner bridge + first_action required"
assert "plannerMode" in src or "planner_auto_bridge_ready" in src, "sa-0358 planner mode hardening missing"
assert "Planner bridge ready" in src or "plannerNote" in src, "planner note injection missing"
print("OK: validate-graph-executor-planner-bridge-v1 · first_action_id note (sa-0308 · sa-0358)")
PY
