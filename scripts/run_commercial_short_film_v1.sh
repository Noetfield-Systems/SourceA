#!/usr/bin/env bash
# Commercial short film — full stack real UI capture → mp4 + proof embed
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"

say() { printf '%s\n' "$*"; }

say "=== Commercial short film pipeline $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

say "Step 1 — landing :5180..."
if ! curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null 2>&1; then
  bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -6
fi
curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null || {
  say "FAIL: landing not reachable at :5180"
  exit 1
}
say "OK: landing"

say "Step 2 — Worker Hub :13020 (optional)..."
if ! curl -sf "http://127.0.0.1:13020/" >/dev/null 2>&1; then
  say "WARN: Hub not up — factory beat may show blank; start hub for best capture"
else
  say "OK: Hub"
fi

say "Step 3 — Mac Health :13024 (optional)..."
if ! curl -sf "http://127.0.0.1:13024/health" >/dev/null 2>&1; then
  say "WARN: Mac Health not up — ops beat uses landing fallback"
else
  say "OK: Mac Health"
fi

say "Step 4 — generate film (1080p Playwright + narration + captions)..."
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
python3 "$ROOT/scripts/sourcea_elevenlabs_vo_setup_v1.py" --check --json 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('ok'):
        print('OK: SourceA ElevenLabs wired')
    else:
        print('WARN: ElevenLabs not wired — macOS say fallback')
        print('  Wire once: python3 scripts/sourcea_elevenlabs_vo_setup_v1.py --api-key sk_...')
except Exception:
    pass
" || true
python3 "$ROOT/scripts/sourcea_commercial_film_v1.py" --json

say "Step 5 — redeploy landing with mp4..."
bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -8

say ""
say "PASS: Commercial short film"
say "  Watch: http://127.0.0.1:5180/sourcea/proof.html#w1-demo-film"
say "  Desktop: ~/Desktop/SourceA-Commercial-Short.mp4"
say "  Asset: $ROOT/SourceA-landing/green-unified/assets/commercial-short-demo.mp4"
say "  Receipt: $SINA/enforcement/commercial-short-film-receipt-v1.json"
