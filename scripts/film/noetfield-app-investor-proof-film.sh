#!/usr/bin/env bash
# Noetfield App investor proof film — LOCKED B_proof lane
# Beats: data/noetfield-app-investor-proof-film-beats-v1.json
# Law: data/NOETFIELD_APP_INVESTOR_PROOF_FILM_LOCKED_v1.md
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ -d "$HERE/data" && -d "$HERE/scripts" ]]; then
  ROOT="$HERE"
elif [[ -d "$HERE/../../data" && -d "$HERE/../../scripts" ]]; then
  ROOT="$(cd "$HERE/../.." && pwd)"
else
  ROOT="$HOME/Desktop/SourceA"
fi
SINA="${HOME}/.sina"
RENDER_LOG="$SINA/commercial-film-render-noetfield-app.log"
GUARD="$ROOT/scripts/commercial_film_render_guard_v1.py"
BEATS="$ROOT/data/noetfield-app-investor-proof-film-beats-v1.json"

_on_exit() {
  local code=$?
  python3 "$GUARD" release --lane noetfield >/dev/null 2>&1 || true
  echo "END: Noetfield app investor proof film exit=$code $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$RENDER_LOG"
  exit "$code"
}

mkdir -p "$SINA"
echo "=== NOETFIELD APP investor proof film $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$RENDER_LOG"

if [[ ! -f "$BEATS" ]]; then
  echo "FAIL: missing beats $BEATS" >&2
  exit 1
fi

python3 "$ROOT/scripts/sourcea_elevenlabs_vo_setup_v1.py" --check --json 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('OK: ElevenLabs wired' if d.get('ok') else 'WARN: ElevenLabs not ready — wire ~/.sina/elevenlabs-v1.env')
except Exception:
    print('WARN: ElevenLabs check skipped')
" || true

python3 "$GUARD" machine-check --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('snapshot',{}).get('founder_line','machine ok'))" || true
python3 "$GUARD" acquire --lane noetfield --holder-pid $$ --json || {
  python3 "$GUARD" status --json || true
  exit 1
}

trap _on_exit EXIT
echo "START: Noetfield app investor proof PID=$$ $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RENDER_LOG"
python3 "$ROOT/scripts/commercial_short_film_v1.py" \
  --beats "$BEATS" \
  --product noetfield \
  "$@" 2>&1 | tee -a "$RENDER_LOG"
exit "${PIPESTATUS[0]}"
