#!/usr/bin/env bash
# deploy_fbe_fly_free_v1.sh — Fly FBE worker · FREE-ONLY (auto-stop · scale-to-zero · shared-cpu-1x 256mb)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CONFIG="$ROOT/data/fbe_cloud_worker_config_v1.json"
FLY_TOML="$ROOT/cloud/fly.toml"
RECEIPT="$HOME/.sina/fbe-fly-deploy-receipt-v1.json"
FLY_BIN="${FLYCTL_INSTALL:-$HOME/.fly}/bin/flyctl"

install_flyctl() {
  if [[ -x "$FLY_BIN" ]]; then
    return 0
  fi
  echo "Installing flyctl to $HOME/.fly/bin …"
  curl -fsSL https://fly.io/install.sh | sh
  FLY_BIN="$HOME/.fly/bin/flyctl"
  [[ -x "$FLY_BIN" ]] || { echo "FAIL: flyctl install failed"; exit 1; }
}

fly_cmd() {
  "$FLY_BIN" "$@"
}

require_auth() {
  if ! fly_cmd auth whoami >/dev/null 2>&1; then
    echo "FAIL: Fly not authenticated."
    echo "Founder one tap: $FLY_BIN auth login"
    exit 1
  fi
}

app_name() {
  python3 - <<'PY'
import re
from pathlib import Path
text = Path("cloud/fly.toml").read_text(encoding="utf-8")
m = re.search(r'^app\s*=\s*["\']([^"\']+)["\']', text, re.M)
print(m.group(1) if m else "sourcea-fbe-worker-v1")
PY
}

ensure_app() {
  local app
  app="$(app_name)"
  if fly_cmd apps list --json 2>/dev/null | python3 -c "import json,sys; apps={a.get('Name') for a in json.load(sys.stdin)}; print('yes' if '$app' in apps else 'no')" | grep -q yes; then
    echo "OK: Fly app exists · $app"
    return 0
  fi
  echo "Creating Fly app · $app (yyz · no deploy yet)"
  if ! fly_cmd apps create "$app" --org personal 2>&1; then
    if fly_cmd apps create "$app" 2>&1; then
      return 0
    fi
    python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path
receipt = {
    "schema": "fbe-fly-deploy-receipt-v1",
    "ok": False,
    "blocked": "fly_billing_required",
    "app": "$app",
    "free_only": True,
    "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "message": "Fly requires billing on org before first app — add card then re-run deploy script",
    "billing_url": "https://fly.io/dashboard/personal/billing",
    "law": "auto_stop · min_machines_running=0 · shared-cpu-1x 256mb",
}
Path("$RECEIPT").parent.mkdir(parents=True, exist_ok=True)
Path("$RECEIPT").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
PY
    exit 2
  fi
}

deploy_free() {
  local app
  app="$(app_name)"
  echo "=== Deploy FBE worker · FREE-ONLY (auto_stop · min_machines=0) ==="
  fly_cmd deploy --config "$FLY_TOML" --remote-only --ha=false --yes
  local url="https://${app}.fly.dev"
  echo "Health: ${url}/health"
  if command -v curl >/dev/null 2>&1; then
    for i in 1 2 3 4 5 6; do
      if curl -fsS "${url}/health" >/tmp/fbe-fly-health.json 2>/dev/null; then
        echo "PASS: /health"
        cat /tmp/fbe-fly-health.json
        break
      fi
      echo "Waiting for cold start (${i}/6)…"
      sleep 8
    done
  fi
  python3 - <<PY
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path("$ROOT")
cfg_path = root / "data/fbe_cloud_worker_config_v1.json"
url = "https://${app}.fly.dev"
cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
cfg["worker_url"] = url
cfg["fly"]["app"] = "${app}"
cfg["fly"]["deployed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
cfg["fly"]["free_only"] = True
cfg["fly"]["auto_stop"] = True
cfg["fly"]["min_machines_running"] = 0
cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
receipt = {
    "schema": "fbe-fly-deploy-receipt-v1",
    "ok": True,
    "app": "${app}",
    "url": url,
    "health": url + "/health",
    "free_only": True,
    "deployed_at": cfg["fly"]["deployed_at"],
    "law": "auto_stop · min_machines_running=0 · shared-cpu-1x 256mb",
}
Path("$RECEIPT").parent.mkdir(parents=True, exist_ok=True)
Path("$RECEIPT").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
PY
  echo ""
  echo "Set on Mac Hub (optional): export FBE_CLOUD_WORKER_URL=https://${app}.fly.dev"
}

main() {
  install_flyctl
  require_auth
  ensure_app
  deploy_free
}

main "$@"
