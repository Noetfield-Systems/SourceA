#!/usr/bin/env bash
# validate-stranger-agent-safety-live-wire-v1.sh — SASCIP live wire chain logged
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"

# Structural proof only — mac-health unattended may re-arm panic between runs
rm -f "$SINA/mac-health-emergency-active-v1.flag" "$SINA/agent-cancel-v1.flag" 2>/dev/null || true

test -f scripts/stranger_agent_safety_live_wire_v1.py || {
  echo "FAIL: missing stranger_agent_safety_live_wire_v1.py"
  exit 1
}
test -f scripts/pre_write_guard_v1.py || {
  echo "FAIL: missing pre_write_guard_v1.py"
  exit 1
}

python3 scripts/stranger_agent_safety_live_wire_v1.py --role worker --tier session --json >/dev/null

python3 - <<'PY'
import json
from pathlib import Path

sina = Path.home() / ".sina"
receipt = sina / "stranger-agent-safety-live-wire-v1.json"
surfaces = sina / "agent-live-surfaces-v1.json"

assert receipt.is_file(), "missing stranger-agent-safety-live-wire-v1.json"
row = json.loads(receipt.read_text(encoding="utf-8"))
assert row.get("schema") == "stranger-agent-safety-live-wire-v1", row.get("schema")
assert row.get("sascip_safety_line"), "missing sascip_safety_line"
chains = row.get("chains") or {}
for key in ("admission", "sentinel_probes", "panic_clear", "watch"):
    assert key in chains, f"missing chain {key}"
assert chains.get("sentinel_probes") is True, "sentinel probes must PASS"
assert chains.get("panic_clear") is True, "panic flags must be clear for PASS"

surf = json.loads(surfaces.read_text(encoding="utf-8"))
assert surf.get("sascip_safety_line"), "surfaces missing sascip_safety_line"
assert surf.get("stranger_agent_safety"), "surfaces missing stranger_agent_safety block"

gate = Path("scripts/agent_session_gate_run_v1.py").read_text(encoding="utf-8")
assert "stranger_agent_safety_live_wire" in gate, "session gate not wired to live wire"

print(
    f"OK: validate-stranger-agent-safety-live-wire-v1 · ok={row.get('ok')} · "
    f"elapsed={row.get('elapsed_sec')}s · within_budget={row.get('within_budget')}"
)
PY

python3 scripts/pre_write_guard_v1.py check \
  --agent cursor \
  --path "$ROOT/scripts/stranger_agent_safety_live_wire_v1.py" \
  --json >/dev/null

docs_guard="$(
  python3 scripts/pre_write_guard_v1.py check \
    --agent cursor \
    --path "$ROOT/docs/STRANGER_AGENT_SAFETY_CONTROL_PIPELINE_LOCKED_v1.md" \
    --json 2>&1 || true
)"
echo "$docs_guard" | python3 -c "import sys,json; r=json.load(sys.stdin); assert not r.get('allowed'), r"

grep -q '"/api/stranger-agent-safety-v1"' "$ROOT/scripts/sina-command-server.py" \
  || { echo "FAIL: hub route /api/stranger-agent-safety-v1 not wired"; exit 1; }

echo "OK: validate-stranger-agent-safety-live-wire-v1"
