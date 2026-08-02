#!/usr/bin/env bash
# Clone trial Vercel projects on noetfield-systems (backup before main move).
# Law: clone first on trial → verify → then main Chrome move.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCOPE="${VERCEL_TRIAL_SCOPE:-noetfield-systems}"
VC="${VERCEL_CMD:-npx --yes vercel}"
NOETFIELD="${NOETFIELD_ROOT:-$HOME/Desktop/noetfield/Noetfield-All-Documents/Noetfield}"
SINA="${HOME}/.sina"
RECEIPT="${SINA}/trial-vercel-clones-receipt-v1.json"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

deploy_clone() {
  local name="$1" path="$2"
  local tmp
  tmp="$(mktemp -d)"
  echo "=== clone: $name ← $path ==="
  cp -R "$path"/. "$tmp/"
  rm -rf "$tmp/.vercel"
  # --name creates new project when no .vercel link (do not use --project on first create)
  $VC deploy "$tmp" --prod --yes --scope="$SCOPE" --name="$name"
  rm -rf "$tmp"
}

mkdir -p "$SINA"
echo "Trial clone run · scope=$SCOPE · at=$TS"
echo ""

deploy_clone "sourcea-landing-clone" "$ROOT/SourceA-landing/green-unified/dist"
echo ""
deploy_clone "deploy-clone" "$ROOT/witnessbc-site/dist/deploy"
echo ""
if [[ -d "$NOETFIELD" ]]; then
  deploy_clone "www-clone" "$NOETFIELD"
else
  echo "SKIP www-clone — missing NOETFIELD_ROOT: $NOETFIELD"
fi

python3 - <<PY
import json
from pathlib import Path
r = {
    "schema": "trial-vercel-clones-v1",
    "at": "$TS",
    "scope": "$SCOPE",
    "clones": [
        {"name": "sourcea-landing-clone", "url": "https://sourcea-landing-clone.vercel.app/sourcea/"},
        {"name": "deploy-clone", "url": "https://deploy-clone.vercel.app/"},
        {"name": "www-clone", "url": "https://www-clone-murex.vercel.app/", "note": "alias may vary if name taken"},
    ],
    "originals_keep": [
        {"name": "sourcea-landing", "url": "https://sourcea-landing.vercel.app"},
        {"name": "deploy", "url": "https://deploy-sooty-seven-93.vercel.app"},
        {"name": "www", "url": "https://project-gc7lm.vercel.app"},
    ],
    "next": "Verify clones on trial dashboard → then main Chrome the-777-foundation move",
}
Path("$RECEIPT").write_text(json.dumps(r, indent=2) + "\n")
print(f"OK: receipt → $RECEIPT")
PY

echo ""
echo "PASS: trial clones on noetfield-systems. Verify:"
echo "  https://sourcea-landing-clone.vercel.app/sourcea/"
echo "  https://deploy-clone.vercel.app/"
echo "  https://www-clone-murex.vercel.app/  (check dashboard for www-clone alias)"
