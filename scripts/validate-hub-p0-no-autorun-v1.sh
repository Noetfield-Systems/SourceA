#!/usr/bin/env bash
# validate-hub-p0-no-autorun-v1.sh — hub p0.next_action must not promote Cursor AUTO-RUN (AS-01)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Refresh projection from SSOT builder path
python3 scripts/align_command_data_ui_v1.py >/dev/null 2>&1 || true

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from founder_p0_next_action_v1 import rt_live_gate_active, validate_next_action

cmd = Path("agent-control-panel/command-data.json")
if not cmd.is_file():
    print("FAIL: command-data.json missing")
    sys.exit(1)

data = json.loads(cmd.read_text(encoding="utf-8"))
founder = (data.get("command_center") or {}).get("founder") or {}
p0 = founder.get("p0") or founder
na = str(p0.get("next_action") or "")
ok, msg = validate_next_action(na)
if not ok:
    print(f"FAIL: validate-hub-p0-no-autorun-v1 — {msg}")
    sys.exit(1)

try:
    from live_founder_decision_form_v1 import payload as live_form_payload

    open_picks = int(live_form_payload().get("open_questions_count") or 0) > 0
except Exception:
    open_picks = False

if not rt_live_gate_active() and not open_picks:
    sq = data.get("sourcea_sa_queue") or {}
    live = (sq.get("live_pick") or {}).get("id")
    if live and str(live).startswith("sa-") and live not in na:
        print(f"FAIL: validate-hub-p0-no-autorun-v1 — live_pick {live} not cited in next_action")
        sys.exit(1)

founder_surfaces = []
for key in ("command_center", "founder_actions", "goal1_auto_run", "goal1_loop", "home_founder_view", "sourcea_sa_queue"):
    if key in data:
        founder_surfaces.append(json.dumps(data[key]).lower())
raw = "\n".join(founder_surfaces)
for bad in ("start auto run", "goal 1 auto-run:", "▶ start auto run"):
    if bad in raw:
        print(f"FAIL: validate-hub-p0-no-autorun-v1 — stale Cursor copy {bad!r} in founder surfaces")
        sys.exit(1)

print("OK: validate-hub-p0-no-autorun-v1")
PY
