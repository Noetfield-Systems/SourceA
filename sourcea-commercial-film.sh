#!/usr/bin/env bash
# SourceA commercial film ONLY — NOT WitnessBC
# Render rules: data/commercial-film-render-rules-v1.json
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
SINA="${HOME}/.sina"
RENDER_LOG="$SINA/commercial-film-render-sourcea.log"
GUARD="$ROOT/scripts/commercial_film_render_guard_v1.py"

_on_exit() {
  local code=$?
  python3 "$GUARD" release --lane sourcea >/dev/null 2>&1 || true
  echo "END: SourceA commercial film exit=$code $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$RENDER_LOG"
  exit "$code"
}

echo "=== SOURCEA commercial film $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a "$RENDER_LOG"

echo "Step 1 — SourceA landing :5180..."
if ! curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null 2>&1; then
  bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -6
fi
curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null || {
  echo "FAIL: SourceA landing not on :5180"
  exit 1
}
echo "OK: SourceA landing"

echo "Step 2 — Worker Hub :13020 (optional)..."
curl -sf "http://127.0.0.1:13020/" >/dev/null && echo "OK: Hub" || echo "WARN: Hub down — factory beat may be thin"

echo "Step 3 — Mac Health :13024 (optional)..."
curl -sf "http://127.0.0.1:13024/health" >/dev/null && echo "OK: Mac Health" || echo "WARN: Mac Health down"

python3 "$ROOT/scripts/sourcea_elevenlabs_vo_setup_v1.py" --check --json 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('OK: ElevenLabs wired' if d.get('ok') else 'WARN: ElevenLabs fallback — wire sourcea_elevenlabs_vo_setup_v1.py')
except Exception:
    pass
" || true

python3 "$GUARD" machine-check --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('snapshot',{}).get('founder_line','machine ok'))" || true
python3 "$GUARD" acquire --lane sourcea --holder-pid $$ --json || {
  python3 "$GUARD" status --json
  exit 1
}

trap _on_exit EXIT
echo "START: SourceA commercial film PID=$$ $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RENDER_LOG"
python3 "$ROOT/scripts/sourcea_commercial_film_v1.py" "$@" 2>&1 | tee -a "$RENDER_LOG"
exit "${PIPESTATUS[0]}"
