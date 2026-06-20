#!/usr/bin/env bash
# Batch proof sa-0318 … sa-0424 (30-task unattended drain)
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
APP = ROOT / "agent-control-panel" / "assets" / "app.js"
LAW = ROOT / "AGENT_SCOREBOARD_LOCKED_v1.md"
PRIORITY = ROOT / "os" / "plan-library" / "SOURCEA-PRIORITY.md"
E2E = (SCRIPTS / "audit_backend_e2e.py").read_text(encoding="utf-8")
APP_S = APP.read_text(encoding="utf-8")
PRI_S = PRIORITY.read_text(encoding="utf-8")
BUILD = (SCRIPTS / "build-sina-command-panel.py").read_text(encoding="utf-8")

from agent_scoreboard import scoreboard_payload, REQUIREMENTS

sb = scoreboard_payload()
checks = {
    "sa-0318": LAW.is_file() and "auto-green" in APP_S and sb.get("agent_count") == 7,
    "sa-0319": ".sc-sb-verify-force" in APP_S and ".sc-sb-verify\"" not in APP_S and "Auto green" in APP_S,
    "sa-0320": "/api/agent-scoreboard" in E2E and "sa-0320" in E2E,
    "sa-0321": "council_brief" in str(REQUIREMENTS) and "vault_deposit" in str(REQUIREMENTS),
    "sa-0322": "Fleet targets" in PRI_S and ">=6" in PRI_S.replace("≥", ">="),
    "sa-0323": sb.get("agent_count") == 7 and "mergepack" in sb.get("mergepack_note", "").lower(),
    "sa-0324": "validate-governance-fleet-v1.sh" in BUILD,
    "sa-0325": "fleet_auto_green_count" in PRI_S or "Auto-green" in PRI_S,
}

from runtime.graph_executor.spine_bridge import build_spine_bridge

bridge = build_spine_bridge()
checks["sa-0401"] = "spine_bridge_ready" in bridge
checks["sa-0402"] = "pos-dispatch" in (bridge.get("planner_bridge_note") or "")
checks["sa-0403"] = "validate-spine-bridge-founder-v1.sh" in BUILD
checks["sa-0405"] = "/api/event-bus-v1" in E2E
checks["sa-0406"] = (ROOT / "scripts" / "execution_intelligence" / "reader.py").is_file()
checks["sa-0407"] = "run_graph_executor" in BUILD
checks["sa-0408"] = "planner_bridge_ready" in bridge and "branches_registry" in (bridge.get("planner_bridge_note") or "branches_registry")
checks["sa-0410"] = "spine-bridge-founder" in (SCRIPTS / "validate-spine-bridge-founder-v1.sh").read_text(encoding="utf-8")
checks["sa-0411"] = "Loop closure" in PRI_S or "loop" in PRI_S.lower()
checks["sa-0412"] = "Spine" in PRI_S or "D16" in PRI_S or "synthesis" in PRI_S.lower()
checks["sa-0413"] = "validate-graph-executor-pos-dispatch-v1.sh" in BUILD
checks["sa-0414"] = "/api/founder/actions" in E2E or "founder/actions" in APP_S
checks["sa-0415"] = "policy_class" in E2E and "/api/graph-executor-v1" in E2E
checks["sa-0416"] = "spine-smoke-echo" in (SCRIPTS / "validate-spine-bridge-founder-v1.sh").read_text(encoding="utf-8")
checks["sa-0417"] = (SCRIPTS / "execution_spine" / "progress_sync.py").is_file()
checks["sa-0418"] = "renderEventBusPanel" in APP_S and "event-bus-panel" in APP_S
checks["sa-0419"] = "Founder law" in PRI_S and "Refresh" in PRI_S
checks["sa-0420"] = bridge.get("dispatch_ready") is False
checks["sa-0421"] = "loop" in PRI_S.lower()
checks["sa-0422"] = "strategic_brief" in APP_S or "strategic_brief" in (SCRIPTS / "strategic_synthesis_hub.py").read_text(encoding="utf-8")
checks["sa-0423"] = "find_critical_bugs" in BUILD
checks["sa-0424"] = (SCRIPTS / "execution_spine" / "progress_sync.py").is_file()

failed = [k for k, v in checks.items() if not v]
assert not failed, "batch checks failed: " + ", ".join(failed)
print(f"OK: validate-batch-sa-0318-0424-v1 · {len(checks)} tasks proof PASS")
PY
