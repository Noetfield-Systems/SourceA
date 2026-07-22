#!/usr/bin/env bash
# SourceA Agency Product Demo — prep + open surfaces (Buyer 1 · agency lane).
# Law: SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"
LAW="$ROOT/SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md"
PREP_ONLY=0
OPEN_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prep-only) PREP_ONLY=1; shift ;;
    --open-only) OPEN_ONLY=1; shift ;;
    -h|--help)
      echo "Usage: run_sourcea_agency_product_demo_v1.sh [--prep-only | --open-only]"
      echo "Product: SourceA governed agent execution · Package: Mac Guard (agency invoice)"
      exit 0
      ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

say() { printf '%s\n' "$*"; }

start_if_down() {
  local name="$1" script="$2" port="$3"
  if curl -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
    say "  OK ${name} :${port}"
    return 0
  fi
  say "  starting ${name} :${port}..."
  bash "$ROOT/scripts/${script}" >/dev/null 2>&1 || true
  for _ in $(seq 1 20); do
    if curl -sf "http://127.0.0.1:${port}/health" >/dev/null 2>&1; then
      say "  OK ${name} :${port}"
      return 0
    fi
    sleep 0.5
  done
  say "  WARN ${name} :${port} not healthy — see ~/.sina logs"
  return 1
}

if [[ "$OPEN_ONLY" -ne 1 ]]; then
  say "=== SourceA Agency Product Demo — prep ==="
  say "Product: SourceA (Buyer 1) · Package: Mac Guard agency SKUs"
  say "Law: SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md"
  say ""

  start_if_down "Chat Unify" "serve-chat-unify.sh" 13023 || true
  start_if_down "Mac Health" "serve-mac-health-guard.sh" 13024 || true
  start_if_down "N8N Integration" "serve-n8n-integration.sh" 13026 || true

  say ""
  say "SourceA Layer 1 — critic boot:"
  python3 "$ROOT/scripts/critic_boot_v1.py" --json | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f'  verdict: {r.get(\"verdict\")}')
print(f'  line:    {r.get(\"founder_line\")}')
for c in r.get('checks') or []:
    mark = 'OK' if c.get('ok') else 'FAIL'
    print(f'    [{mark}] {c.get(\"name\")}: {c.get(\"reason\")}')
"

  if [[ -f "$ROOT/scripts/n8n_commercial_grade_v1.py" ]]; then
    say ""
    say "Mac Guard commercial pack (SourceA export bundle):"
    python3 "$ROOT/scripts/n8n_commercial_grade_v1.py" --pack --json 2>/dev/null | python3 -c "
import sys, json
try:
    d=json.load(sys.stdin)
    print('  commercial_ready:', d.get('commercial_ready', d.get('ok')))
except Exception:
    print('  WARN: pack refresh skipped')
" || say "  WARN: commercial grade script failed"
  fi

  for f in n8n-commercial-client-sow-v1.html n8n-commercial-client-weekly-v1.html; do
    [[ -f "$SINA/$f" ]] && say "  OK client asset: $f" || say "  MISSING: $SINA/$f"
  done

  say ""
  if [[ "$PREP_ONLY" -eq 1 ]]; then
    say "Prep done. Pitch:"
    say "  SourceA — agents don't run until PASS; Mac Guard is the agency package."
    say ""
    say "Next: bash scripts/run_sourcea_agency_product_demo_v1.sh --open-only"
    exit 0
  fi
fi

say "=== Opening demo surfaces ==="
open "http://127.0.0.1:13023/" 2>/dev/null || true
open "http://127.0.0.1:13024/" 2>/dev/null || true
open "http://127.0.0.1:13026/" 2>/dev/null || true
[[ -f "$SINA/n8n-commercial-client-sow-v1.html" ]] && open "$SINA/n8n-commercial-client-sow-v1.html" || true
[[ -f "$SINA/n8n-commercial-client-weekly-v1.html" ]] && open "$SINA/n8n-commercial-client-weekly-v1.html" || true
[[ -f "$LAW" ]] && open "$LAW" 2>/dev/null || true

say ""
say "Follow: SOURCEA_AGENCY_PRODUCT_DEMO_SCRIPT_LOCKED_v1.md"
say "Close: SourceA $750 audit (Mac Guard invoice) → $299/mo agency"
