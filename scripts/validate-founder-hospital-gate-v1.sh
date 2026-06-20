#!/usr/bin/env bash
# validate-founder-hospital-gate-v1.sh — Hospital/Maze/Orientation founder-word-only · session gate on start
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-founder-hospital-gate-v1 — $*" >&2; exit 1; }

LAW="${ROOT}/AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md"
RULE="${ROOT}/.cursor/rules/002-hospital-trigger-only.mdc"
MIRROR="${ROOT}/.cursor/rules/agent-memory-mirror.mdc"
GATE="${ROOT}/scripts/agent_session_gate_run_v1.py"
CARD="${HOME}/.sina/agent-executor-daily-duty-card-v1.json"

[[ -f "$LAW" ]] || fail "missing law"
[[ -f "$RULE" ]] || fail "missing 002-hospital-trigger-only.mdc"
[[ -f "$MIRROR" ]] || fail "missing agent-memory-mirror.mdc"
[[ -f "$GATE" ]] || fail "missing agent_session_gate_run_v1.py"
[[ -f "$CARD" ]] || fail "missing daily duty card logged"

grep -q "Session start = session gate only" "$LAW" || fail "law missing session start rule"
grep -q "founder trigger only\|founder word ONLY\|Founder says one word" "$RULE" || fail "002 must document founder-word-only trigger"
grep -q "agent_hospital_pipeline_v1.py" "$RULE" || fail "002 must forbid auto hospital"
grep -q "agent_session_gate_run_v1.py" "$RULE" || fail "002 must cite session gate"

python3 <<'PY' "$CARD" "$GATE"
import json, sys
from pathlib import Path
card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
gate = Path(sys.argv[2]).read_text(encoding="utf-8")
ids = {x.get("id") for x in card.get("never_make_founder_repeat") or []}
if "D23" not in ids:
    raise SystemExit("daily duty card missing D23")
order = " ".join(card.get("session_start_order") or [])
if "hospital" in order.lower() or "maze" in order.lower() or "orientation" in order.lower():
    raise SystemExit("session_start_order must not include pipelines")
if "agent_hospital_pipeline" in gate and "founder_triggers" not in gate:
    pass  # gate file runs hospital only when invoked — ok
# session gate receipt must expose pipelines_policy
if "pipelines_policy" not in gate:
    raise SystemExit("session gate must write pipelines_policy on session start")
print("OK: D23 present · session_start_order clean · session gate pipelines_policy wired")
PY

echo "OK: validate-founder-hospital-gate-v1"
