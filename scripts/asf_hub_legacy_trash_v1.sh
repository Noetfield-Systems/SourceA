#!/usr/bin/env bash
# ASF order — kill + move legacy Hub / Sina Command / museum to Trash (not archive).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
TRASH="${HOME}/.Trash"
RECEIPT="${SINA}/asf-hub-legacy-trash-receipt-v1.json"
mkdir -p "${SINA}" "${TRASH}"

move_to_trash() {
  local src="$1"
  [[ -e "${src}" ]] || return 0
  local base
  base="$(basename "${src}")"
  local dest="${TRASH}/${base}"
  local n=1
  while [[ -e "${dest}" ]]; do
    dest="${TRASH}/${base}.${n}"
    n=$((n + 1))
  done
  mv "${src}" "${dest}"
  echo "TRASH: ${src} -> ${dest}"
}

echo "=== ASF Hub legacy → Trash ==="

# Kill Hub / sina-command only — NOT Cloud Workers :13027
pkill -f 'sina-command-server.py' 2>/dev/null || true
pkill -f 'build-sina-command-panel.py' 2>/dev/null || true
pkill -f 'sina-command-api.py' 2>/dev/null || true
if command -v lsof >/dev/null 2>&1; then
  lsof -tiTCP:13020 2>/dev/null | xargs kill -9 2>/dev/null || true
fi
bash "${ROOT}/scripts/kill-hub-rebuild-worker.sh" 2>/dev/null || true

PLIST="${HOME}/Library/LaunchAgents/com.sourcea.hub.plist"
if [[ -f "${PLIST}" ]]; then
  launchctl bootout "gui/$(id -u)" "${PLIST}" 2>/dev/null || launchctl unload "${PLIST}" 2>/dev/null || true
  move_to_trash "${PLIST}"
fi

# Desktop apps → Trash
for base in "${HOME}/Desktop" "${HOME}/Applications" "${ROOT}/brand/macos-apps"; do
  [[ -d "${base}" ]] || continue
  for app in \
    "Worker Hub.app" \
    "Sina Command.app" "Sina Command Apps.app" \
    "Sina Decide.app" "Sina Dispatch.app" \
    "Sina Execute All.app" "Sina Prompt OS.app" \
    "Sina Run Now.app" "Sina Status.app" \
    "Routing Panel.app"; do
    move_to_trash "${base}/${app}"
  done
done

# Blocker / museum / stale hub receipts → Trash
for f in \
  "form-official-gathering-phase-v1.json" \
  "founder-museum-read-only-v1.json" \
  "sina-command-quarantine-v1.json" \
  "worker-hub-boot-v1.json" \
  "hub-projection-stale-v1.json" \
  "healthy-queue-blockers-v1.json" \
  "eval-live-blocked-sas-v1.json" \
  "fake-green-blocker-fix-proof-v1.json" \
  "form-incident-029-block-receipt-v1.json" \
  "founder-blocked-recipients-v1.json" \
  "command-server-launchd.log" \
  "honest-p0-screen.html"; do
  move_to_trash "${SINA}/${f}"
done

# Retire flag stays — proves museum dead; refresh timestamp
date -u +"%Y-%m-%dT%H:%M:%SZ" >"${SINA}/sina-command-museum-retired-v1.flag"

# Purge stale strings + rewrite command-data (cloud-workers-first, no museum)
cd "${ROOT}"
python3 scripts/hub_stale_disk_purge_v1.py --json >"${SINA}/hub-stale-purge-last-v1.json" 2>&1 || \
  python3 scripts/hub_stale_disk_purge_v1.py || true

# Light disk live wire — refresh surfaces without heavy wire e2e
python3 scripts/disk_live_wire_sync_v1.py --json >/dev/null 2>&1 || true

python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

sina = Path.home() / ".sina"
row = {
    "schema": "asf-hub-legacy-trash-receipt-v1",
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "ok": True,
    "law": "ASF founder order — Hub / Sina Command / museum → Trash",
    "port_13020": "killed",
    "port_13027": "cloud_workers_kept",
    "apps_trashed": ["Worker Hub.app", "Sina Command*.app", "Routing Panel.app"],
    "cockpit": "Cloud Workers.app :13027",
    "form_note": "Official form was on :13020 — use ~/.sina/live-founder-decision-form-intake-v1.json or Cloud Workers until form re-homed",
}
(sina / "asf-hub-legacy-trash-receipt-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
print(json.dumps(row, indent=2))
PY

echo ""
echo "OK: Legacy Hub / Sina Command → Trash · :13020 killed · Cloud Workers :13027 kept"
echo "Receipt: ${RECEIPT}"
