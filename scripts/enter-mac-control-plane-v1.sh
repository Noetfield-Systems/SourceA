#!/usr/bin/env bash
# enter-mac-control-plane-v1.sh — Mac = control panel · cloud/API = execution
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/scripts/mac_control_plane_v1.py" --enter

mkdir -p "${HOME}/.sina"
touch "${HOME}/.sina/mac-light-validators-only-v1.flag"
python3 "$ROOT/scripts/mac_law_universal_wire_v1.py" --sync-receipt --json >/dev/null 2>&1 || true
python3 "$ROOT/scripts/mac_law_agent_execution_plane_lock_v1.py" --sync-receipt --json >/dev/null 2>&1 || true
python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --wire-gates --json >/dev/null 2>&1 || true
python3 "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" --json >/dev/null 2>&1 || true

echo ""
echo "=== HUB (:13020) — TCC-safe boot ==="
python3 "$ROOT/scripts/mac_launchd_tcc_guard_v1.py" --boot-hub --json 2>/dev/null \
  || bash "$ROOT/scripts/serve-sina-command.sh" || echo "WARN: Hub boot failed — see ~/.sina/mac-launchd-tcc-receipt-v1.json"

echo ""
echo "=== CLOUD WORKERS (:13027) — factory cockpit ==="
bash "$ROOT/scripts/serve-cloud-workers-v1.sh" || echo "WARN: Cloud Workers boot failed — see ~/.sina/cloud-workers-server.log"

echo ""
echo "=== MAC LAW SURFACES (:8781 · :8780) ==="
bash "$ROOT/scripts/mac_law_surfaces_boot_v1.sh" || echo "WARN: Mac Law surfaces boot failed — see ~/.sina/mac-law-server.log"

echo ""
echo "=== MORNING CLEANUP ==="
bash "$ROOT/scripts/mac-daily-cleanup-v1.sh" --morning --quiet 2>/dev/null || true
echo ""
echo "Mid-job (auto every 2h): install-mac-daily-cleanup-launchagent-v1.sh"
echo "End of day: bash ~/Desktop/SourceA/scripts/mac-daily-cleanup-v1.sh --night --restart-cursor"
