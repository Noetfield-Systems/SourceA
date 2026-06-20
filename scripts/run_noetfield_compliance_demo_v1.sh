#!/usr/bin/env bash
# Noetfield Compliance Demo — prep + open surfaces (NW1 · Copilot governance lane).
# Law: NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SINA="${HOME}/.sina"
LAW="$ROOT/NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md"
NW1_URL="https://www.noetfield.com/copilot/pilot/"
PREP_ONLY=0
OPEN_ONLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --prep-only) PREP_ONLY=1; shift ;;
    --open-only) OPEN_ONLY=1; shift ;;
    -h|--help)
      echo "Usage: run_noetfield_compliance_demo_v1.sh [--prep-only | --open-only]"
      echo "Product: Noetfield Copilot Governance · Engine: SourceA (bridge only)"
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
  say "  WARN ${name} :${port} not healthy"
  return 1
}

if [[ "$OPEN_ONLY" -ne 1 ]]; then
  say "=== Noetfield Compliance Demo — prep ==="
  say "Product: Noetfield · Copilot Governance Pack · NW1"
  say "Law: NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md"
  say ""

  start_if_down "Chat Unify" "serve-chat-unify.sh" 13023 || true

  say ""
  say "Layer 1 — critic boot (policy re-brief gate):"
  python3 "$ROOT/scripts/critic_boot_v1.py" --json | python3 -c "
import sys, json
r = json.load(sys.stdin)
print(f'  verdict: {r.get(\"verdict\")}')
print(f'  line:    {r.get(\"founder_line\")}')
for c in r.get('checks') or []:
    mark = 'OK' if c.get('ok') else 'FAIL'
    print(f'    [{mark}] {c.get(\"name\")}: {c.get(\"reason\")}')
"

  say ""
  say "Machine governance critic (fixtures):"
  if [[ -f "$ROOT/scripts/governance_critic_eval_v1.py" ]]; then
    python3 "$ROOT/scripts/governance_critic_eval_v1.py" --fixtures --json 2>/dev/null | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(f'  ok: {r.get(\"ok\")} passed {r.get(\"passed\")}/{r.get(\"total\")}')
except Exception:
    print('  WARN: critic eval skipped')
" || say "  WARN: governance critic eval failed"
  fi

  say ""
  say "AI unify API (Layer 2 provider):"
  python3 "$ROOT/scripts/ai_unify_api_v1.py" --action status --json 2>/dev/null | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    print(f'  openrouter: {r.get(\"openrouter_ready\")} gemini_direct: {r.get(\"gemini_direct_ready\")} auto: {r.get(\"auto_provider\")}')
except Exception:
    print('  WARN: ai status skipped')
" || true

  [[ -f "$SINA/critic-boot-v1.json" ]] && say "  OK receipt: critic-boot-v1.json" || say "  MISSING: critic-boot-v1.json"
  [[ -f "$SINA/governance-critic-eval-latest-v1.json" ]] && say "  OK receipt: governance-critic-eval-latest-v1.json" || true

  say ""
  if [[ "$PREP_ONLY" -eq 1 ]]; then
    say "Prep done. Pitch:"
    say "  Noetfield — Copilot actions signed · policy changes re-brief same day."
    say ""
    say "NW1 link: ${NW1_URL}"
    say "Next: bash scripts/run_noetfield_compliance_demo_v1.sh --open-only"
    exit 0
  fi
fi

say "=== Opening demo surfaces ==="
open "http://127.0.0.1:13023/" 2>/dev/null || true
open "$NW1_URL" 2>/dev/null || true
[[ -f "$LAW" ]] && open "$LAW" 2>/dev/null || true

say ""
say "Follow: NOETFIELD_COMPLIANCE_DEMO_SCRIPT_LOCKED_v1.md"
say "Close: NF-QS QuickScan → NF-RD Readiness Pilot · CAD \$2K deposit"
say "NW1 email: SOURCEA_UNIFIED_PORTFOLIO_COMMERCIAL_SSOT_LOCKED_v3.1.md §16"
