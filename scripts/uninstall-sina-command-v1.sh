#!/usr/bin/env bash
# Retire Sina Command / museum / legacy auto-start on Mac (ASF order).
# Worker Hub (H1/H2) may still be started manually — this stops launchd + museum confusion.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
PLIST="${HOME}/Library/LaunchAgents/com.sourcea.hub.plist"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"
RETIRED_FLAG="${SINA}/sina-command-museum-retired-v1.flag"
RETIRED_JSON="${SINA}/sina-command-museum-retired-v1.json"

mkdir -p "${SINA}"

echo "=== Retiring Sina Command museum + auto-start on Mac ==="

bash "${ROOT}/scripts/kill-sina-command.sh" 2>/dev/null || {
  pkill -f 'sina-command-server.py' 2>/dev/null || true
  pkill -f 'build-sina-command-panel.py' 2>/dev/null || true
  pkill -f 'cloud-workers-server' 2>/dev/null || true
}

if [[ -f "${PLIST}" ]]; then
  launchctl bootout "${DOMAIN}" "${PLIST}" 2>/dev/null || launchctl unload "${PLIST}" 2>/dev/null || true
  rm -f "${PLIST}"
  echo "Removed launchd: com.sourcea.hub"
fi

# Standalone Sina Command apps (Desktop / Applications)
for base in "${HOME}/Applications" "${HOME}/Desktop" "/Applications" "${ROOT}/brand/macos-apps"; do
  [[ -d "${base}" ]] || continue
  for app in "${base}/Sina Command.app" "${base}/Sina Command Apps.app" \
    "${base}/Sina Decide.app" "${base}/Sina Dispatch.app" \
    "${base}/Sina Execute All.app" "${base}/Sina Prompt OS.app" \
    "${base}/Sina Run Now.app" "${base}/Sina Status.app"; do
    if [[ -d "${app}" ]]; then
      rm -rf "${app}"
      echo "Deleted app: ${app}"
    fi
  done
done

date -u +"%Y-%m-%dT%H:%M:%SZ" >"${RETIRED_FLAG}"
python3 - <<'PY'
import json
from datetime import datetime, timezone
from pathlib import Path

sina = Path.home() / ".sina"
row = {
    "schema": "sina-command-museum-retired-v1",
    "retired_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "law": "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md",
    "command_retired_forever": True,
    "no_hub_rebuild": True,
    "no_hub_archive": True,
    "launchd_removed": True,
    "note": "Sina Command museum deleted — no auto-start; Hub manual only if needed.",
}
(sina / "sina-command-museum-retired-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

latch = sina / "worker-asf-directive-latch-v1.json"
data = {}
if latch.is_file():
    try:
        data = json.loads(latch.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
data.update(
    {
        "schema": "worker-asf-directive-latch-v1",
        "command_retired_forever": True,
        "no_hub_rebuild": True,
        "no_hub_archive": True,
        "hub2_drain_allowed": True,
        "hub_status": "COMMAND_RETIRED_FOREVER",
        "set_at": row["retired_at"],
        "note": row["note"],
    }
)
latch.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print("Wrote latch + retired receipt")
PY

cd "${ROOT}"
python3 scripts/hub_stale_disk_purge_v1.py --json >/dev/null 2>&1 || python3 scripts/hub_stale_disk_purge_v1.py || true

echo "OK: Sina Command museum retired · launchd removed · no auto-start"
echo "Flag: ${RETIRED_FLAG}"
echo "Receipt: ${RETIRED_JSON}"
echo "To start Hub manually (dev): SINA_HUB_FORCE=1 bash scripts/serve-sina-command.sh fg"
