#!/usr/bin/env bash
# Rebuild founder desktop apps — realtime governance wire · no Worker Hub · light smoke only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="$HOME/.sina"
RECEIPT="$SINA/founder-desktop-apps-wire-receipt-v1.json"
NOW="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

bash "$ROOT/scripts/sync-official-links-bar-v1.sh"

APPS=(
  "build-chat-unify-standalone-app-v1.sh"
  "build-cloud-workers-standalone-app-v1.sh"
  "build-portfolio-mail-standalone-app-v1.sh"
  "build-n8n-integration-standalone-app-v1.sh"
  "build-ag-routing-panel-standalone-app-v1.sh"
)

mkdir -p "$SINA"
results=()
fail=0

for script in "${APPS[@]}"; do
  name="${script#build-}"
  name="${name%-standalone-app-v1.sh}"
  echo ""
  echo "═══ $script ═══"
  if bash "$ROOT/scripts/$script"; then
    results+=("\"$name\": \"PASS\"")
  else
    results+=("\"$name\": \"FAIL\"")
    fail=$((fail + 1))
  fi
done

bash "$ROOT/scripts/sync-standalone-apps-to-bundles-v1.sh" || true

verify_out=""
if bash "$ROOT/scripts/verify-founder-desktop-apps-v1.sh" 2>/dev/null; then
  verify_out="PASS"
else
  verify_out="FAIL"
  fail=$((fail + 1))
fi

python3 - <<PY
import json
from pathlib import Path
receipt = {
    "schema": "founder-desktop-apps-wire-receipt-v1",
    "at": "$NOW",
    "ok": ${fail} == 0 and "$verify_out" == "PASS",
    "law": "SOURCEA_POISON_AND_REALTIME_BLOCKER_TERMINOLOGY_LOCKED_v1.md",
    "cockpit": "http://127.0.0.1:13027/",
    "form_ui": "http://127.0.0.1:13023/form/",
    "chat_unify": "http://127.0.0.1:13023/",
    "worker_hub": "RETIRED",
    "builds": {$(IFS=,; echo "${results[*]}")},
    "verify": "$verify_out",
}
Path("$RECEIPT").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, indent=2))
PY

if [[ "$fail" -gt 0 ]]; then
  echo "FAIL: $fail build step(s) failed — see $RECEIPT" >&2
  exit 1
fi
echo "OK: founder desktop apps wired — $RECEIPT"
