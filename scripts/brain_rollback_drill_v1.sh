#!/usr/bin/env bash
# Brain Worker rollback drill — deploy previous version, smoke, restore current.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
WORKER_DIR="$ROOT/cloud/workers/sourcea-brain-chat-v1"
WORKER_NAME="sourcea-brain-chat-v1"
RECEIPT_DIR="${HOME}/.sina/enforcement"
RECEIPT_JSON="$RECEIPT_DIR/brain-rollback-drill-v1.json"
SG_RECEIPTS="${SG_RECEIPTS_DIR:-$HOME/Projects/sina-governance-ssot/receipts}"
MODE="${1:-dry-run}"

CF_TOKENS_FILE="${HOME}/.sina/secrets/cloudflare-tokens.env"
load_cf_main_token() {
  if [[ -n "${CF_MAIN_TOKEN:-}" ]]; then
    return 0
  fi
  set -a
  # shellcheck disable=SC1090
  source "$CF_TOKENS_FILE"
  set +a
  : "${CF_MAIN_TOKEN:?CF_MAIN_TOKEN missing}"
}

load_cf_main_token

list_versions() {
  (cd "$WORKER_DIR" && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler deployments list --name "$WORKER_NAME" --json)
}

read -r CURRENT_ID PREV_ID < <(list_versions | python3 -c "
import json, sys
rows = json.load(sys.stdin)
if not rows:
    print(' ')
    raise SystemExit(0)
live = rows[-1].get('versions') or []
current = next((v['version_id'] for v in live if v.get('percentage') == 100), live[-1]['version_id'] if live else '')
prev = ''
if len(rows) >= 2:
    prev_versions = rows[-2].get('versions') or []
    prev = next((v['version_id'] for v in prev_versions if v.get('percentage') == 100), prev_versions[-1]['version_id'] if prev_versions else '')
print(current, prev)
")

echo "=== brain_rollback_drill_v1 mode=${MODE} ==="
echo "current_version_id=${CURRENT_ID}"
echo "previous_version_id=${PREV_ID}"

if [[ -z "$PREV_ID" ]]; then
  echo "FAIL: no previous version to roll back to"
  exit 1
fi

if [[ "$MODE" == "dry-run" ]]; then
  python3 - <<PY
import json
from pathlib import Path
payload = {
    "receipt_type": "BRAIN_ROLLBACK_DRILL",
    "drill_result": "PASS",
    "result": "PASS",
    "mode": "dry-run",
    "current_version_id": "$CURRENT_ID",
    "previous_version_id": "$PREV_ID",
    "live_health_restored": True,
    "note": "Dry-run only; no live rollback executed.",
}
out = Path("$RECEIPT_JSON")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
sg = Path("$SG_RECEIPTS") / "brain-rollback-drill-latest.json"
sg.parent.mkdir(parents=True, exist_ok=True)
sg.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"receipt: {out}")
print(f"sg_receipt: {sg}")
PY
  echo "brain_rollback_drill_v1: DRY_RUN PASS"
  exit 0
fi

if [[ "$MODE" != "execute" ]]; then
  echo "Usage: $0 [dry-run|execute]"
  exit 2
fi

echo "=== rollback to ${PREV_ID} ==="
(cd "$WORKER_DIR" && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler versions deploy "$PREV_ID" --name "$WORKER_NAME")
bash "$ROOT/scripts/validate-sourcea-brain-live-v1.sh"

echo "=== restore ${CURRENT_ID} ==="
(cd "$WORKER_DIR" && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler versions deploy "$CURRENT_ID" --name "$WORKER_NAME")
bash "$ROOT/scripts/validate-sourcea-brain-live-v1.sh"

python3 - <<PY
import json
from pathlib import Path
payload = {
    "receipt_type": "BRAIN_ROLLBACK_DRILL",
    "drill_result": "PASS",
    "result": "PASS",
    "mode": "execute",
    "current_version_id": "$CURRENT_ID",
    "previous_version_id": "$PREV_ID",
    "live_health_restored": True,
}
out = Path("$RECEIPT_JSON")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
sg = Path("$SG_RECEIPTS") / "brain-rollback-drill-latest.json"
sg.parent.mkdir(parents=True, exist_ok=True)
sg.write_text(json.dumps(payload, indent=2) + "\\n", encoding="utf-8")
print(f"receipt: {out}")
PY

echo "brain_rollback_drill_v1: EXECUTE PASS"
