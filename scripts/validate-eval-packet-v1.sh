#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/scripts"
python3 - <<'PY'
import json
import urllib.request

from eval_packet_v1.runner import run_eval
from system_roadmap import system_roadmap_payload

rep = run_eval(write_report=True)
assert rep.get("schema") == "eval-packet-v1"
assert rep.get("task_count", 0) >= 8
assert rep.get("packet_win_pct", 0) >= 80, rep.get("summary")
assert rep.get("ok"), rep

sr = system_roadmap_payload()
ev = sr.get("eval_packet") or {}
assert ev.get("ok"), ev

with urllib.request.urlopen("http://127.0.0.1:13020/api/eval-packet-v1", timeout=60) as resp:
    live = json.loads(resp.read())
assert live.get("ok"), live
print("OK: validate-eval-packet-v1")
PY
