#!/usr/bin/env bash
# WitnessBC E2E — ONE command, any directory. Never guess paths.
#
# From anywhere:
#   bash ~/Desktop/SourceA/witnessbc-site/scripts/wbc-e2e.sh
# From deploy folder:
#   bash e2e.sh
# From SourceA:
#   bash witnessbc-site/scripts/wbc-e2e.sh
#
set -euo pipefail

WBC_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WBC_ROOT="$(cd "$WBC_SCRIPT/.." && pwd)"
DEEP_PY="$WBC_SCRIPT/validate_witnessbc_deep_e2e_v1.py"
FULL_SH="$WBC_SCRIPT/validate_witnessbc_full_e2e_v1.sh"
TOOLKITS_SH="$WBC_SCRIPT/validate_toolkits_e2e_v1.sh"
RECEIPT="${HOME}/.sina/witnessbc-deep-e2e-receipt-v1.json"

BASE="${WBC_E2E_BASE:-https://witnessbc-commercial.pages.dev}"
MODE="deep"
LOCAL=0
EXTRA=()

usage() {
  cat <<EOF
WitnessBC E2E (cwd-safe — run from any folder)

  bash $WBC_SCRIPT/wbc-e2e.sh              # deep crawl (default)
  bash $WBC_SCRIPT/wbc-e2e.sh --quick      # pages + assets only
  bash $WBC_SCRIPT/wbc-e2e.sh --toolkits    # toolkits pages only
  bash $WBC_SCRIPT/wbc-e2e.sh --local       # test http://127.0.0.1:8091 (starts server)
  bash $WBC_SCRIPT/wbc-e2e.sh --base URL    # custom base URL

Env: WBC_E2E_BASE=https://...  (default preview URL)
Site root: $WBC_ROOT
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --deep) MODE="deep"; shift ;;
    --quick) MODE="quick"; shift ;;
    --toolkits) MODE="toolkits"; shift ;;
    --local) LOCAL=1; BASE="http://127.0.0.1:8091"; shift ;;
    --base)
      BASE="${2:-}"
      [[ -n "$BASE" ]] || { echo "FAIL: --base requires URL"; exit 1; }
      shift 2
      ;;
    -h | --help) usage; exit 0 ;;
    *) EXTRA+=("$1"); shift ;;
  esac
done

for f in "$DEEP_PY" "$FULL_SH" "$TOOLKITS_SH"; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f (site root=$WBC_ROOT)"; exit 1; }
done

SERVER_PID=""
cleanup() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

if [[ "$LOCAL" -eq 1 ]]; then
  DEPLOY="$WBC_ROOT/dist/deploy"
  [[ -d "$DEPLOY" ]] || { echo "FAIL: no deploy artifact — run: bash witnessbc-site/scripts/run-recipe.sh"; exit 1; }
  echo "=== starting local server on 8091 ($DEPLOY) ==="
  (cd "$DEPLOY" && python3 -m http.server 8091) >/dev/null 2>&1 &
  SERVER_PID=$!
  sleep 1
fi

echo "=== WBC E2E mode=$MODE base=$BASE ==="
echo "    (site root: $WBC_ROOT)"
echo ""

case "$MODE" in
  deep)
    if ((${#EXTRA[@]})); then
      python3 "$DEEP_PY" --base "$BASE" --receipt "$RECEIPT" "${EXTRA[@]}"
    else
      python3 "$DEEP_PY" --base "$BASE" --receipt "$RECEIPT"
    fi
    ;;
  quick)
    bash "$FULL_SH" "$BASE"
    ;;
  toolkits)
    bash "$TOOLKITS_SH" "$BASE"
    ;;
esac
