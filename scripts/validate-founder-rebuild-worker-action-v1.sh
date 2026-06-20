#!/usr/bin/env bash
# Founder one-tap rebuild worker action — hub stabilization P9 gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

grep -q 'founder-restart-rebuild-worker' "$ROOT/scripts/sina_command_lib.py"
grep -q 'restart_rebuild_worker' "$ROOT/scripts/sina_command_lib.py"
grep -q 'founder-restart-rebuild-worker' "$ROOT/scripts/hub_home_founder_view_v1.py"
grep -q 'worker_health' "$ROOT/scripts/hub_home_founder_view_v1.py"

bash "$ROOT/scripts/ensure-hub-rebuild-worker-v1.sh"

curl -sf "http://127.0.0.1:13030/health" >/dev/null

SHELL="$ROOT/agent-control-panel/command-data-shell.json"
test -f "$SHELL"

python3 - "$SHELL" <<'PY'
import json
import sys
from pathlib import Path

shell = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
hfv = shell.get("home_founder_view") or {}
actions = [a.get("id") for a in hfv.get("actions") or []]
founder = shell.get("founder_actions") or []
flat_ids: list[str] = []
for grp in founder if isinstance(founder, list) else []:
    for a in grp.get("actions") or []:
        flat_ids.append(a.get("id") or "")

target = "founder-restart-rebuild-worker"
if target not in actions and target not in flat_ids:
    # Also scan grouped founder_actions in payload modules
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    if target not in text:
        sys.exit(f"FAIL: {target} missing from panel shell JSON")
PY

echo "OK: validate-founder-rebuild-worker-action-v1 · action wired + :13030 healthy"
