#!/usr/bin/env bash
# Permanent H1 stability — launchd supervisor + boot snapshot + heal + verify.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
PORT="${SINA_COMMAND_PORT:-13020}"

echo "→ Worker hub heal + boot snapshot…"
python3 worker_hub_heal_v1.py --reason hub-stable-fix || python3 worker_hub_v1.py --json --no-cache >/dev/null

echo "→ Install hub launchd (auto-restart on login)…"
bash "$ROOT/scripts/install-hub-launchd-v1.sh"

echo "→ Verify boot.json + API…"
test -f "$ROOT/agent-control-panel/worker-hub/boot.json" || {
  python3 worker_hub_v1.py --json --no-cache >/dev/null
  test -f "$ROOT/agent-control-panel/worker-hub/boot.json"
}

python3 - <<PY
import json, os, urllib.request, pathlib
root = pathlib.Path("${ROOT}")
boot = json.loads((root / "agent-control-panel/worker-hub/boot.json").read_text())
assert boot.get("ok") is True, "boot.json not ok"
port = os.environ.get("SINA_COMMAND_PORT", "13020")
with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/worker-hub/v1", timeout=8) as r:
    live = json.loads(r.read().decode())
assert live.get("ok") is True
print(f"OK: boot task={boot.get('queue_sa_id')} live={live.get('queue_sa_id')} honest={live.get('honest_ok')}")
PY

bash "$ROOT/scripts/validate-super-fast-hub-v1.sh"
echo ""
echo "✓ H1 stable — launchd supervises :${PORT} · boot.json fallback · heal wired"
echo "  Hard refresh: http://127.0.0.1:${PORT}/"
