#!/usr/bin/env bash
# validate-agent-three-pipelines-v1.sh — three pipeline orchestrators + registry + law
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
REG="${SINA}/agent-three-pipelines-registry-v1.json"
LAW="${ROOT}/AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md"

fail() { echo "FAIL: validate-agent-three-pipelines-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing law $LAW"

for s in agent_three_pipelines_lib_v1.py agent_three_pipelines_router_v1.py \
  agent_orientation_pipeline_v1.py agent_hospital_pipeline_v1.py agent_maze_pipeline_v1.py; do
  [[ -f "${ROOT}/scripts/${s}" ]] || fail "missing script scripts/${s}"
  python3 -m py_compile "${ROOT}/scripts/${s}" || fail "py_compile ${s}"
done

[[ -f "$REG" ]] || fail "missing registry $REG"

python3 - <<'PY' "$REG" "$ROOT"
import json, sys
from pathlib import Path
reg_path, root = Path(sys.argv[1]), Path(sys.argv[2])
reg = json.loads(reg_path.read_text())
if reg.get("schema") not in ("agent-three-pipelines-registry-v1", "agent-three-pipelines-registry-v2"):
    raise SystemExit("registry schema mismatch")
pipes = reg.get("pipelines") or {}
for key in ("orientation", "hospital", "maze"):
    p = pipes.get(key) or {}
    script = p.get("script")
    if not script or not (root / "scripts" / script).is_file():
        raise SystemExit(f"registry pipeline {key} script missing: {script}")
    trig = p.get("trigger")
    if trig != key:
        raise SystemExit(f"trigger mismatch {key}: {trig}")
if not reg.get("escalation", {}).get("hospital_to_maze_if_critical"):
    raise SystemExit("escalation hospital_to_maze_if_critical must be true")
policy = reg.get("founder_trigger_policy") or {}
for k in ("session_start", "founder_triggers", "forbidden_on_session_start"):
    if not policy.get(k):
        raise SystemExit(f"founder_trigger_policy missing {k}")
if set(policy.get("founder_triggers") or []) != {"orientation", "hospital", "maze"}:
    raise SystemExit("founder_triggers must be orientation|hospital|maze")
print(f"OK: registry {len(pipes)} pipelines · escalation wired · founder-word-only policy")
PY

grep -q "Session start = session gate only" "$LAW" || fail "law missing session start = session gate only"
grep -q "founder word ONLY" "$ROOT/.cursor/rules/agent-memory-mirror.mdc" || fail "agent-memory-mirror.mdc missing founder-word-only rule"
grep -q "Speed balance (INCIDENT-035" "$LAW" || fail "law missing speed balance section"
grep -q "maze_status_line" "$ROOT/scripts/agent_three_pipelines_lib_v1.py" || fail "lib missing maze_status_line"

python3 - <<'PY' "$ROOT"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
from agent_three_pipelines_lib_v1 import (
    find_critical_fresh,
    hospital_green_fresh,
    anti_staleness_bundle_fresh,
    maze_speed_mode,
    maze_status_line,
    sync_pipelines_registry,
)
for fn in (find_critical_fresh, hospital_green_fresh, anti_staleness_bundle_fresh, maze_speed_mode, maze_status_line):
    if not callable(fn):
        raise SystemExit(f"missing callable {fn}")
sync_pipelines_registry()
line = maze_status_line()
if not line.startswith("MAZE "):
    raise SystemExit(f"maze_status_line bad: {line!r}")
print(f"OK: speed helpers + registry sync · {line[:72]}")
PY

MR="${SINA}/agent-maze-receipt-v1.json"
if [[ -f "$MR" ]]; then
python3 - <<'PY' "$MR"
import json, sys
r = json.loads(open(sys.argv[1]).read())
if r.get("schema") != "agent-maze-receipt-v2":
    raise SystemExit("maze receipt schema v2 expected")
if "speed_mode" not in r:
    raise SystemExit("maze receipt missing speed_mode block")
if "duration_mode" not in r and r.get("ok"):
    raise SystemExit("passed maze receipt missing duration_mode")
print(f"OK: maze receipt ok={r.get('ok')} mode={r.get('duration_mode')} elapsed={r.get('elapsed_sec')}")
PY
fi

echo "== orientation smoke =="
python3 "${ROOT}/scripts/agent_orientation_pipeline_v1.py" --role any --json >/dev/null \
  || fail "orientation pipeline run"

OR="${SINA}/agent-orientation-receipt-v1.json"
[[ -f "$OR" ]] || fail "orientation receipt missing"
python3 - <<'PY' "$OR"
import json, sys
r = json.loads(open(sys.argv[1]).read())
if r.get("schema") not in ("agent-orientation-receipt-v1", "agent-orientation-receipt-v2"):
    raise SystemExit("orientation receipt schema")
if r.get("tier") != 1:
    raise SystemExit("orientation must be tier 1")
if r.get("execution_authority") is not False:
    raise SystemExit("orientation must not grant execution authority")
print(f"OK: orientation receipt ok={r.get('ok')} stations={len(r.get('stations') or [])}")
PY

echo "OK: validate-agent-three-pipelines-v1 · law + scripts + registry + orientation smoke + orient routing"
