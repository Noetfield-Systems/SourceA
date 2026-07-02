#!/usr/bin/env bash
# sourcea-mac-v1.sh — run SourceA Mac helpers from any directory (~/.sina launcher)
set -euo pipefail
SINA="${HOME}/.sina"
ROOT_FILE="${SINA}/sourcea-root-v1.json"
if [[ -f "$ROOT_FILE" ]]; then
  ROOT="$(python3 -c "import json; print(json.load(open('${ROOT_FILE}'))['root'])")"
else
  ROOT="${HOME}/Desktop/SourceA"
fi
if [[ ! -d "$ROOT/scripts" ]]; then
  echo "FAIL: SourceA not found at $ROOT" >&2
  echo "Fix: cd ~/Desktop/SourceA && bash scripts/sync-mac-launchd-wrappers-v1.sh" >&2
  exit 1
fi
cd "$ROOT"
CMD="${1:-help}"
shift || true
case "$CMD" in
  dispatch)
    exec python3 scripts/mac_cloud_deploy_dispatch_v1.py --target dispatch "$@"
    ;;
  cf-tick|trigger-cf-tick)
    exec python3 scripts/cloud_workers_hub_v1.py --action trigger_cf_tick "$@"
    ;;
  cloud-workers|cw)
    exec bash scripts/serve-cloud-workers-v1.sh
    ;;
  cloud-workers-status)
    exec curl -sf "http://127.0.0.1:${CLOUD_WORKERS_PORT:-13027}/health" | python3 -m json.tool
    ;;
  brain)
    exec python3 scripts/mac_cloud_deploy_dispatch_v1.py --target brain "$@"
    ;;
  validate-dispatch)
    exec bash scripts/validate-mac-control-dispatch-v1.sh
    ;;
  control-plane|boot)
    exec bash scripts/enter-mac-control-plane-v1.sh
    ;;
  fda|launchd-fda)
    exec bash scripts/open-mac-launchd-fda-v1.sh
    ;;
  hub)
    exec bash scripts/serve-sina-command.sh
    ;;
  help|-h|--help)
    cat <<EOF
SourceA Mac helpers (from any directory)

  ~/.sina/sourcea-mac-v1.sh dispatch --plan-id MAC-CTL-002 --json
  ~/.sina/sourcea-mac-v1.sh cf-tick --json
  ~/.sina/sourcea-mac-v1.sh cloud-workers
  ~/.sina/sourcea-mac-v1.sh cloud-workers-status
  ~/.sina/sourcea-mac-v1.sh brain --json
  ~/.sina/sourcea-mac-v1.sh validate-dispatch
  ~/.sina/sourcea-mac-v1.sh control-plane
  ~/.sina/sourcea-mac-v1.sh fda
  ~/.sina/sourcea-mac-v1.sh hub

Repo: $ROOT
EOF
    ;;
  *)
    echo "Unknown command: $CMD (try: help)" >&2
    exit 1
    ;;
esac
