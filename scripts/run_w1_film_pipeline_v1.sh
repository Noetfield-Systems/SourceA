#!/usr/bin/env bash
# W1 AI proof film — capture real UI B-roll + AI narration → w1-demo.mp4
# No outbound email. Video artifact only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"

say() { printf '%s\n' "$*"; }

say "=== W1 AI film pipeline $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
say ""

say "Step 1 — ensure landing server :5180..."
SERVER_PID=""
if ! curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null 2>&1; then
  say "Deploying landing..."
  bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -5
  if [[ -f "$HOME/Desktop/agentrun-app/serve.sh" ]]; then
    say "Starting Agent Run server..."
    (cd "$HOME/Desktop/agentrun-app" && python3 -m http.server 5180 --bind 127.0.0.1) >/tmp/sourcea-serve-5180.log 2>&1 &
    SERVER_PID=$!
    sleep 2
  fi
fi
curl -sf "http://127.0.0.1:5180/sourcea/" >/dev/null || {
  say "FAIL: landing not reachable — run: cd ~/Desktop/agentrun-app && ./serve.sh"
  exit 1
}
say "OK: landing live"
say ""

say "Step 2 — generate film (Playwright B-roll + AI voice)..."
python3 "$ROOT/scripts/w1_film_generate_v1.py" --capture-landing --json
say ""

say "Step 3 — validate receipt..."
bash "$ROOT/scripts/validate-w1-film-receipt-v1.sh"
say ""

say "Step 4 — redeploy with mp4..."
bash "$ROOT/SourceA-landing/green-unified/scripts/run-recipe.sh" 2>&1 | tail -8
say ""

say "PASS: W1 AI film pipeline"
say "  Watch: http://127.0.0.1:5180/sourcea/proof.html#w1-demo-film"
say "  Asset:  $ROOT/SourceA-landing/green-unified/assets/w1-demo.mp4"
say "  Receipt: $SINA/enforcement/w1-film-receipt-v1.json"
if [[ -n "${SERVER_PID:-}" ]]; then
  kill "$SERVER_PID" 2>/dev/null || true
fi
