#!/bin/bash
# Fix commercial queue poisoning + restart overnight loop.
# Run once: bash ~/Desktop/SourceA/scripts/fix-queue-and-restart-overnight.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="$HOME/.sina"

echo "=== FIX QUEUE + RESTART OVERNIGHT ==="

# 1. Kill stale overnight processes
pkill -f "start-overnight-3engine-v1.sh" 2>/dev/null || true
pkill -f "autorun_dispatcher_v1.py" 2>/dev/null || true
rm -f "$SINA/overnight-3engine-v1.pid"
echo "STEP1: stale procs killed"

# 2. Restore good eval-dispatch queue (sa-0153–sa-0166) from repo
REPO_QUEUE="$ROOT/brain-os/plan-registry/sourcea-1000/prompts/healthy-queue-30-active.json"
if [[ -f "$REPO_QUEUE" ]]; then
    cp "$REPO_QUEUE" "$SINA/healthy-queue-30-active.json"
    echo "STEP2: queue restored from repo (sa-0153–sa-0166)"
else
    # Fallback: regenerate (now patched to skip commercial)
    python3 "$ROOT/scripts/generate-healthy-prompt-pack-v1.py"
    PACK_Q="$ROOT/os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json"
    [[ -f "$PACK_Q" ]] && cp "$PACK_Q" "$SINA/healthy-queue-30-active.json"
    echo "STEP2: queue regenerated (patched generator)"
fi

# 3. Verify queue is not commercial
python3 - <<'PY'
import json, sys
from pathlib import Path
q = Path.home() / ".sina/healthy-queue-30-active.json"
d = json.loads(q.read_text())
first = (d.get("queue") or [{}])[0]
sa = first.get("sa_id","?")
phase = first.get("phase","?")
if phase == "phase-s5-commercial-lanes" or sa.startswith("sa-05"):
    print(f"ABORT: queue still commercial ({sa}). Do not start overnight.")
    sys.exit(1)
print(f"OK: queue head = {sa} / {phase}")
PY

# 4. Reset queue state to pos 1
python3 - <<'PY'
import json
from pathlib import Path
p = Path.home() / ".sina/healthy-queue-state-v1.json"
q = json.loads((Path.home()/".sina/healthy-queue-30-active.json").read_text())
total = q.get("count", 30)
p.write_text(json.dumps({"next_pos": 1, "queue_total": total, "reset_at": "2026-06-08"}) + "\n")
print(f"STEP3: queue state reset to pos 1/{total}")
PY

# 5. Reset broker to idle
python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path
p = Path.home() / ".sina/goal1-lane-broker-v1.json"
st = {
    "schema": "goal1-lane-broker-v1",
    "status": "idle",
    "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "note": "fix-queue-and-restart",
}
p.write_text(json.dumps(st, indent=2) + "\n")
print("STEP4: broker reset to idle")
PY

# 6. Start overnight engine
echo "STEP5: starting overnight engine..."
bash "$ROOT/scripts/start-overnight-3engine-v1.sh"

echo ""
echo "=== DONE — watch log: tail -f ~/.sina/overnight-3engine-v1.log ==="
