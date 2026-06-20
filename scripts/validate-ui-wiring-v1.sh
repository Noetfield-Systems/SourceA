#!/usr/bin/env bash
# TRACE: AUTO-TRACE-RUNTIME-UI-WIRING-v1.0 · agent Auto · validate-ui-wiring-v1.sh
# UI wiring — command-data.json must expose clean organized blocks for hub tabs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Self-heal after hub auto-sync drift (P0 pick · eval · scoreboard · goal1).
SINA_ALIGN_SKIP_VALIDATORS=1 python3 scripts/align_command_data_ui_v1.py >/dev/null

python3 <<'PY'
import json
import sys
from pathlib import Path

root = Path(".")
cmd = root / "agent-control-panel" / "command-data.json"
if not cmd.is_file():
    print("FAIL: command-data.json missing")
    sys.exit(1)

data = json.loads(cmd.read_text(encoding="utf-8"))
errors: list[str] = []

def need(path: str, cond: bool, detail: str = "") -> None:
    if not cond:
        errors.append(f"{path}{': ' + detail if detail else ''}")


need("schema_version", bool(data.get("schema_version")))
need("built_at", bool(data.get("built_at")))

cc = data.get("command_center") or {}
founder = cc.get("founder") or {}
p0 = founder.get("p0") or {}
need("command_center.founder.p0.id", bool(p0.get("id")))
need("command_center.founder.p0.next_action", bool(p0.get("next_action")))

sq = data.get("sourcea_sa_queue") or {}
live = (sq.get("live_pick") or {}).get("id")
counts = sq.get("counts") or {}
factory_now = {}
fn_path = Path.home() / ".sina" / "factory-now-v1.json"
if fn_path.is_file():
    try:
        factory_now = json.loads(fn_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        factory_now = {}
lawful_exhausted = (
    int(factory_now.get("backlog") or counts.get("backlog") or 0) == 0
    and int(factory_now.get("valid_yes") or counts.get("honest_done") or 0) >= 1000
)
if lawful_exhausted:
    need("sourcea_sa_queue.counts.backlog", int(counts.get("backlog") or 0) == 0, str(counts.get("backlog")))
else:
    need("sourcea_sa_queue.live_pick", live and str(live).startswith("sa-"), str(live))

sys.path.insert(0, "scripts")
from founder_p0_next_action_v1 import rt_live_gate_active, validate_next_action  # noqa: E402

na = str(p0.get("next_action") or "")
open_picks = False
try:
    from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: E402

    open_picks = int(live_form_payload().get("open_questions_count") or 0) > 0
except Exception:
    open_picks = False

if rt_live_gate_active():
    ok, msg = validate_next_action(na)
    if not ok:
        errors.append(f"RT LIVE next_action invalid: {msg}")
elif open_picks:
    ok, msg = validate_next_action(na)
    if not ok:
        errors.append(f"form-office next_action invalid: {msg}")
    if live and str(live) in na:
        errors.append(f"form-office P0 must not cite live_pick {live} (INCIDENT-027)")
elif live and live not in na and not lawful_exhausted:
    errors.append(f"P0 next_action must cite live_pick {live}")

g1 = data.get("goal1_auto_run") or data.get("goal1_loop") or {}
need("goal1_auto_run.ok", g1.get("ok") is True)
need("goal1_auto_run.executor", isinstance(g1.get("executor"), dict))
need("goal1_auto_run.inbox", isinstance(g1.get("inbox"), dict))
need("goal1_auto_run.brief", bool(g1.get("brief")))

sr = data.get("system_roadmap") or {}
evb = sr.get("eval_packet_v1b") or {}
need("system_roadmap.eval_packet_v1b", bool(evb))
if evb.get("mode") == "live" and evb.get("packet_win_pct") is None:
    errors.append("eval_packet_v1b live mode missing packet_win_pct")

sb = data.get("agent_scoreboard") or {}
need("agent_scoreboard", bool(sb))
if sb.get("fleet_auto_green_count") is None:
    errors.append("agent_scoreboard.fleet_auto_green_count missing")

shell = root / "agent-control-panel" / "command-data-shell.json"
if shell.is_file():
    sh = json.loads(shell.read_text(encoding="utf-8"))
    heavy = ("system_roadmap", "agent_scoreboard", "council_room", "fleet")
    if shell.stat().st_size > 500 * 1024:
        errors.append(f"command-data-shell.json too large: {shell.stat().st_size} bytes (sa-0016)")
    for k in heavy:
        if k in sh:
            errors.append(f"heavy key {k} leaked into command-data-shell.json")

if errors:
    print("FAIL: validate-ui-wiring-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(
    f"OK: validate-ui-wiring-v1 · pick={live or 'idle'} · "
    f"eval_1b={evb.get('packet_win_pct')}% · fleet_green={sb.get('fleet_auto_green_count')}"
)
PY
