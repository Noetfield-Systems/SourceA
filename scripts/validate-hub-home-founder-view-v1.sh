#!/usr/bin/env bash
# HUB_HOME_REDESIGN_SPEC_LOCKED_v1.md — home_founder_view payload + UI gate (sa-0821)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

grep -q "home_founder_view" "$ROOT/scripts/sina_command_lib.py"
grep -q "homeFounderView" "$ROOT/agent-control-panel/assets/app.js"
grep -q "renderHomeFounderView" "$ROOT/agent-control-panel/assets/app.js"
grep -q "sc-home-founder-detail" "$ROOT/agent-control-panel/assets/app.css"
grep -q "sc-home-founder-safety" "$ROOT/agent-control-panel/assets/app.css"
grep -q "btn-safety-check" "$ROOT/agent-control-panel/assets/shell.html"
grep -q "data-home-detail-toggle" "$ROOT/agent-control-panel/assets/app.js"
grep -q "sc-home-founder-safety" "$ROOT/agent-control-panel/assets/app.js"
grep -q "renderMissedActionsCard" "$ROOT/agent-control-panel/assets/app.js"
grep -q "sc-home-missed" "$ROOT/agent-control-panel/assets/app.css"
grep -q "proof_counter" "$ROOT/scripts/hub_home_founder_view_v1.py"
grep -q "sc-home-founder-proof" "$ROOT/agent-control-panel/assets/app.js"

python3 - <<'PY'
import json
import re
import sys
from pathlib import Path

panel = Path("../agent-control-panel/command-data.json")
if not panel.is_file():
    print("FAIL: command-data.json missing — run build-sina-command-panel.py first")
    sys.exit(1)

data = json.loads(panel.read_text(encoding="utf-8"))
hfv = data.get("home_founder_view") or {}
errors: list[str] = []

if not hfv.get("ok"):
    errors.append("home_founder_view.ok is not true")
if hfv.get("schema") != "hub-home-founder-v1":
    errors.append(f"schema expected hub-home-founder-v1 got {hfv.get('schema')!r}")

status = hfv.get("status") or {}
for key in ("headline", "subline", "next_plain"):
    if not status.get(key):
        errors.append(f"status.{key} missing")
    elif re.search(r"\bsa-\d{4}\b", str(status[key]), re.I):
        errors.append(f"status.{key} must not expose sa-XXXX in plain view")

goals = hfv.get("goals") or []
if len(goals) < 1:
    errors.append("goals array empty")
for g in goals:
    if not g.get("title"):
        errors.append("goal missing title")
    if g.get("progress_pct") is None:
        errors.append(f"goal {g.get('id')} missing progress_pct")

actions = hfv.get("actions") or []
if len(actions) < 3:
    errors.append("actions need at least 3 entries")
for a in actions:
    if not a.get("label"):
        errors.append("action missing label")

events = hfv.get("recent_events") or []
if len(events) < 1:
    errors.append("recent_events empty (need at least 1)")

pc = hfv.get("proof_counter") or {}
if pc.get("verified_done") is None:
    errors.append("proof_counter.verified_done missing (HUB-P0-1)")
if pc.get("kill") not in ("RED", "GREEN"):
    errors.append(f"proof_counter.kill must be RED or GREEN got {pc.get('kill')!r}")

detail = hfv.get("technical_detail") or {}
if "sa_id" not in detail:
    errors.append("technical_detail.sa_id missing (expand panel field)")

next_steps = hfv.get("next_steps") or []
if len(next_steps) < 3:
    errors.append("next_steps need at least 3 numbered steps")
for step in next_steps:
    if not step.get("n") or not step.get("text"):
        errors.append("next_steps entry missing n or text")

safety = hfv.get("safety_panel") or {}
if not safety.get("title") or not safety.get("safety_id"):
    errors.append("safety_panel missing title or safety_id")
safety_ids = {a.get("id") for a in actions}
if safety.get("safety_id") and safety["safety_id"] not in safety_ids:
    errors.append("safety_panel.safety_id not in actions")
if not any(a.get("kind") == "safety" for a in actions):
    errors.append("actions missing kind=safety entry")

mac = hfv.get("missed_actions_card") or {}
if not mac.get("ok"):
    errors.append("missed_actions_card.ok is not true")
elif not (mac.get("items") or []):
    errors.append("missed_actions_card.items empty")
else:
    for it in mac["items"]:
        if not it.get("id") and not (it.get("kind") == "tab" and it.get("tab")):
            errors.append("missed_actions_card item missing id/tab")
        if not it.get("label"):
            errors.append("missed_actions_card item missing label")

wd = hfv.get("worker_drain_next_10") or {}
if not wd.get("ok"):
    errors.append("worker_drain_next_10.ok is not true")
elif not (wd.get("drain") or []):
    errors.append("worker_drain_next_10.drain empty")
elif len(wd.get("drain") or []) > 10:
    errors.append("worker_drain_next_10.drain exceeds 10")

if errors:
    print("FAIL: validate-hub-home-founder-view-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: validate-hub-home-founder-view-v1")
print(f"  goals={len(goals)} actions={len(actions)} events={len(events)} sa_detail={detail.get('sa_id')}")
PY
