#!/usr/bin/env bash
# WitnessBC commercial film — linear recut with ElevenLabs VO when wired
# Render rules: data/commercial-film-render-rules-v1.json
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
SITE_DEPLOY="$ROOT/witnessbc-site/dist/deploy"
PORT=8090
LOG="$HOME/.sina/witnessbc-8090-serve.log"
RENDER_LOG="$HOME/.sina/commercial-film-render-witnessbc.log"
GUARD="$ROOT/scripts/commercial_film_render_guard_v1.py"

ensure_proof_lab() {
  if curl -sf -o /dev/null --max-time 3 "http://127.0.0.1:${PORT}/"; then
    echo "OK: Proof Lab live http://127.0.0.1:${PORT}/"
    return 0
  fi
  echo "WARN: :${PORT} down — starting WitnessBC Proof Lab server..."
  if [[ ! -f "$SITE_DEPLOY/index.html" ]]; then
    bash "$ROOT/witnessbc-site/scripts/run-recipe.sh"
  fi
  mkdir -p "$HOME/.sina"
  nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITE_DEPLOY" >>"$LOG" 2>&1 &
  for _ in $(seq 1 30); do
    if curl -sf -o /dev/null --max-time 2 "http://127.0.0.1:${PORT}/"; then
      echo "OK: Proof Lab started http://127.0.0.1:${PORT}/ (log: $LOG)"
      return 0
    fi
    sleep 0.5
  done
  echo "FAIL: Proof Lab not reachable on :${PORT}"
  echo "  Manual: cd $SITE_DEPLOY && python3 -m http.server ${PORT} --bind 127.0.0.1"
  exit 1
}

_on_exit() {
  local code=$?
  python3 "$GUARD" release --lane witnessbc >/dev/null 2>&1 || true
  echo "END: WitnessBC commercial film exit=$code $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$RENDER_LOG"
  exit "$code"
}

ensure_proof_lab

python3 "$ROOT/scripts/witnessbc_elevenlabs_vo_setup_v1.py" --migrate-legacy --json >/dev/null 2>&1 || true
python3 "$ROOT/scripts/sourcea_elevenlabs_vo_setup_v1.py" --organize --json >/dev/null 2>&1 || true
python3 "$ROOT/scripts/sourcea_elevenlabs_vo_setup_v1.py" --check --json 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('ok'):
        print('OK: ElevenLabs shared key wired (' + str(d.get('key_mask', 'key')) + ')')
    else:
        print('WARN: ElevenLabs not wired — edge_neural fallback')
        print('  Wire once: python3 scripts/sourcea_elevenlabs_vo_setup_v1.py --api-key sk_...')
except Exception:
    pass
" || true

# R1 one render · R2–R14 machine gate (Mac Guard RAM CPU GPU thermal)
python3 "$GUARD" machine-check --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('snapshot',{}).get('founder_line','machine ok'))" || true
python3 "$GUARD" acquire --lane witnessbc --holder-pid $$ --json || {
  python3 "$GUARD" status --json
  exit 1
}

trap _on_exit EXIT
echo "START: WitnessBC commercial film PID=$$ $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$RENDER_LOG"
python3 "$ROOT/scripts/witnessbc_commercial_film_v1.py" "$@" 2>&1 | tee -a "$RENDER_LOG"
exit "${PIPESTATUS[0]}"
