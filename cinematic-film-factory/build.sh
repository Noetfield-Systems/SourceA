#!/usr/bin/env bash
# Cinematic film factory — GPT pipeline runner (SourceA pathway)
# capture → captions → assemble via compiler.py (truth + rules + memory loop)
set -euo pipefail
ROOT="$HOME/Desktop/SourceA"
LANE="${1:-witnessbc}"
LOG="$HOME/.sina/cinematic-film-factory-build.log"

if [[ "$LANE" != "witnessbc" && "$LANE" != "sourcea" ]]; then
  echo "Usage: bash cinematic-film-factory/build.sh [witnessbc|sourcea]"
  exit 1
fi

FREEZE_FLAG="$HOME/.sina/commercial-film-render-frozen-v1.flag"
if [[ -f "$FREEZE_FLAG" ]]; then
  echo "FAIL: cinematic film factory FROZEN — see $FREEZE_FLAG" >&2
  python3 -c "import json; print(json.dumps({'ok': False, 'error': 'film_render_frozen', 'freeze': json.load(open('$FREEZE_FLAG'))}))" 2>/dev/null \
    || echo '{"ok": false, "error": "film_render_frozen"}'
  exit 2
fi

echo "START: cinematic factory lane=$LANE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"

if [[ "$LANE" == "witnessbc" ]]; then
  SITE_DEPLOY="$ROOT/witnessbc-site/dist/deploy"
  PORT=8090
  if ! curl -sf -o /dev/null --max-time 3 "http://127.0.0.1:${PORT}/proof.html"; then
    echo "WARN: Proof Lab :${PORT} down — starting server..."
    if [[ ! -f "$SITE_DEPLOY/index.html" ]]; then
      bash "$ROOT/witnessbc-site/scripts/run-recipe.sh"
    fi
    nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$SITE_DEPLOY" \
      >>"$HOME/.sina/witnessbc-8090-serve.log" 2>&1 &
    for _ in $(seq 1 30); do
      curl -sf -o /dev/null --max-time 2 "http://127.0.0.1:${PORT}/proof.html" && break
      sleep 0.5
    done
  fi
fi

HEADED_FLAG=""
if [[ "${CINEMATIC_HEADED:-0}" == "1" ]]; then
  HEADED_FLAG="--headed"
fi

SKIP_FLAG=""
if [[ "${CINEMATIC_SKIP_CAPTURE:-0}" == "1" ]]; then
  SKIP_FLAG="--skip-capture"
fi

python3 "$ROOT/cinematic-film-factory/compiler.py" --lane "$LANE" --json $HEADED_FLAG $SKIP_FLAG \
  | tee -a "$LOG"

echo "END: cinematic factory lane=$LANE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"$LOG"
