#!/usr/bin/env bash
# validate-cross-lane-edit-v1.sh — highest governance guard must exist and block SSOT spill
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$ROOT/brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md"
GUARD="$ROOT/scripts/cross_lane_edit_guard_v1.py"
RULE="$ROOT/.cursor/rules/000-cross-lane-edit-forbidden.mdc"
COSPRO_RULE="$HOME/Desktop/Cursor OS Pro/.cursor/rules/000-cross-lane-edit-forbidden.mdc"

test -f "$LAW"
test -f "$GUARD"
test -f "$RULE"
test -f "$COSPRO_RULE"

# Research lane B must NOT write product SSOT
python3 - <<'PY'
import json, subprocess, sys
from pathlib import Path
guard = Path.home() / "Desktop/SourceA/scripts/cross_lane_edit_guard_v1.py"
ssot = Path.home() / "Desktop/Cursor OS Pro/docs/SINGLE-SOURCE-OF-TRUTH.md"
out = subprocess.check_output(
    ["python3", str(guard), "check", "--agent", "cursor_os_pro_research_lane_b",
     "--path", str(ssot), "--json"],
    text=True,
)
d = json.loads(out)
assert d.get("ok") is False and d.get("reason") == "CROSS_LANE_SSOT_FORBIDDEN", d
vault = Path.home() / "Desktop/Cursor OS Pro/docs/research/voice_dev_peer_comparison_v1.yaml"
out2 = subprocess.check_output(
    ["python3", str(guard), "check", "--agent", "cursor_os_pro_research_lane_b",
     "--path", str(vault), "--json"],
    text=True,
)
d2 = json.loads(out2)
assert d2.get("ok") is True, d2
agents = Path.home() / "Desktop/Cursor OS Pro/AGENTS.md"
out3 = subprocess.check_output(
    ["python3", str(guard), "check", "--agent", "cursor_os_pro_research_lane_b",
     "--path", str(agents),
     "--explicit-order", f"EDIT ALLOWED: {agents} ACTION: fix typo", "--json"],
    text=True,
)
d3 = json.loads(out3)
assert d3.get("ok") is True, d3
PY

echo "PASS: validate-cross-lane-edit-v1"
