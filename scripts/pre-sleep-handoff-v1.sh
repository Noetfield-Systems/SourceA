#!/usr/bin/env bash
# Pre-sleep handoff — Worker 20-paste queue + sidecars + ACTIVE_NOW sync. Founder still awake.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LOG="$HOME/.sina/pre-sleep-handoff-v1.log"
mkdir -p "$(dirname "$LOG")"
{
  echo "=== PRE-SLEEP HANDOFF $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

  # Ensure kill flag ON while founder at desk (Worker paste only)
  touch "$HOME/.sina/auto-run-disabled-v1.flag"
  echo "autorun kill flag ON (Worker lane until arm sleep)"
  python3 scripts/factory_control_v1.py now --line 2>/dev/null || true

  # Worker paste queue — next 20 turns from current pos
  python3 scripts/generate-worker-100-paste-queue-v1.py -n 20 \
    -o "$ROOT/.sina-loop/WORKER-PRE-SLEEP-20-PASTE-QUEUE.md"

  # Sidecars — API scout + CLI prep watch loop (Phase 1 ON until arm sleep)
  bash scripts/start-sidecar-engines-watch-v1.sh

  # Deliver INBOX if orchestrator idle
  st="$(python3 -c "import json;from pathlib import Path;p=Path.home()/'.sina/healthy-drain-orchestrator-v1.json';print(json.loads(p.read_text()).get('status','') if p.is_file() else '')" 2>/dev/null || true)"
  if [[ "$st" != "awaiting_worker" ]]; then
    python3 scripts/healthy-drain-orchestrator-v1.py deliver --force
  else
    echo "INBOX already awaiting_worker — skip deliver"
  fi

  bash scripts/pre-sleep-team-check-v1.sh || true

  echo "=== HANDOFF READY ==="
} | tee -a "$LOG"
echo "Log: $LOG"
