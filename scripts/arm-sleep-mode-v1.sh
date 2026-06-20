#!/usr/bin/env bash
# Arm sleep — founder leaving. Flip ACTIVE_NOW + start overnight 3-engine (capped).
# Executor only. Founder: say "arm sleep" or tap Hub Action when shipped.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="$HOME/.sina/arm-sleep-mode-v1.log"

ACTIVE="$ROOT/ACTIVE_NOW.md"
python3 - <<'PY'
from pathlib import Path
import re
p = Path("/Users/sinakazemnezhad/Desktop/SourceA/ACTIVE_NOW.md")
text = p.read_text(encoding="utf-8")
text = re.sub(r"\*\*Current Founder Mode:\*\*.*", "**Current Founder Mode:** `founder_absent`", text)
text = re.sub(r"\*\*Current Sleep Escalation:\*\*.*", "**Current Sleep Escalation:** `on`", text)
text = re.sub(
    r"\*\*Current Sprint:\*\*.*",
    "**Current Sprint:** Sleep mode — API CHECK/verify · CLI ACT headless · Worker off",
    text,
)
text = re.sub(
    r"\*\*Current Blocker:\*\*.*",
    "**Current Blocker:** none — overnight dispatcher armed",
    text,
)
p.write_text(text, encoding="utf-8")
print("ACTIVE_NOW → founder_absent + sleep on")
PY

export SINA_OVERNIGHT_MAX_TURNS="${SINA_OVERNIGHT_MAX_TURNS:-20}"
export SINA_OVERNIGHT_SLEEP_SEC="${SINA_OVERNIGHT_SLEEP_SEC:-90}"

{
  echo "=== ARM SLEEP $(date -u +%Y-%m-%dT%H:%M:%SZ) max_turns=$SINA_OVERNIGHT_MAX_TURNS ==="
  bash scripts/pre-sleep-team-check-v1.sh || true
  bash scripts/stop-sidecar-engines-watch-v1.sh 2>/dev/null || true
  bash scripts/start-overnight-3engine-v1.sh
} | tee -a "$LOG"
echo "Sleep armed — log: $LOG"
echo "  overnight: $HOME/.sina/overnight-3engine-v1.log"
echo "  caretaker: event-driven on each dispatch (sleep-mac-caretaker-v1.jsonl)"
