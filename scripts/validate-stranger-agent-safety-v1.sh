#!/usr/bin/env bash
# validate-stranger-agent-safety-v1.sh — SASCIP admission pipeline v1.2
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
fail=0
check() { [[ "$1" == "true" ]] && echo "PASS: $2" || { echo "FAIL: $2"; fail=1; }; }

[[ -f "$ROOT/scripts/stranger_agent_safety_lib_v1.py" ]] && check true "safety lib" || check false "safety lib"
[[ -f "$ROOT/scripts/stranger_agent_safety_pipeline_v1.py" ]] && check true "pipeline script" || check false "pipeline script"
[[ -f "$ROOT/config/stranger-agent-safety-v1.default.json" ]] && check true "default config" || check false "default config"
[[ -f "$ROOT/config/stranger-agent-external-tokens-v1.default.json" ]] && check true "external tokens default" || check false "external tokens default"
[[ -f "$ROOT/docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md" ]] && check true "law doc" || check false "law doc"

python3 "$ROOT/scripts/stranger_agent_safety_pipeline_v1.py" --role worker --agent cursor --json >/dev/null
[[ -f "$SINA/stranger-agent-admission-receipt-v1.json" ]] && check true "admission receipt" || check false "admission receipt"
[[ -f "$SINA/stranger-agent-monitor-v1.json" ]] && check true "monitor projection" || check false "monitor projection"

python3 - <<'PY' || { echo "FAIL: receipt schema v1.2"; fail=1; }
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/stranger-agent-admission-receipt-v1.json").read_text())
assert str(r.get("schema", "")).startswith("stranger-agent-admission-v1")
assert "fingerprint" in r and "classification" in r and "control" in r
assert "mcp" in (r.get("fingerprint") or {})
assert "risk" in (r.get("classification") or {})
stages = {s.get("stage") for s in r.get("stages") or []}
assert stages >= {"IDENTIFY", "CLASSIFY", "CONTROL", "SERVE"}
print("PASS: receipt schema v1.2 + MCP + risk + SERVE")
PY

python3 - <<'PY' || { echo "FAIL: monitor schema"; fail=1; }
import json
from pathlib import Path
m = json.loads((Path.home() / ".sina/stranger-agent-monitor-v1.json").read_text())
assert str(m.get("schema", "")).startswith("stranger-agent-monitor-v1")
assert m.get("one_line")
assert "hub_tile" in m
print("PASS: monitor schema + hub_tile")
PY

python3 - <<'PY' || { echo "FAIL: lib imports"; fail=1; }
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "Desktop/SourceA/scripts"))
from stranger_agent_safety_lib_v1 import (
    build_fingerprint, classify_agent, resolve_cross_lane_agent,
    compute_risk_score, _mcp_fingerprint, run_watch_pulse,
)
fp = build_fingerprint(agent_id="cursor", role_hint="worker")
assert (fp.get("mcp") or {}).get("server_count", 0) >= 0
cls = classify_agent(fp)
assert cls.get("resolved_agent_id") in ("sourcea_worker", "sourcea_execution_core")
assert "risk" in cls
row = resolve_cross_lane_agent("cursor", role_hint="worker")
assert row.get("ok") is True
watch = run_watch_pulse()
assert watch.get("schema") == "stranger-agent-watch-v1.2"
print("PASS: lib classify + MCP + watch pulse")
PY

python3 "$ROOT/scripts/stranger_agent_safety_pipeline_v1.py" --resolve-only --agent unknown --role any --json >/dev/null
python3 "$ROOT/scripts/cross_lane_edit_guard_v1.py" check --agent cursor --path "$ROOT/scripts/stranger_agent_safety_pipeline_v1.py" --json | python3 -c "import sys,json; r=json.load(sys.stdin); assert r.get('ok')"

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-stranger-agent-safety-v1"
  exit 0
fi
echo "FAIL: validate-stranger-agent-safety-v1"
exit 1
