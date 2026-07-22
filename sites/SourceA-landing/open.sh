#!/usr/bin/env bash
# Sync + open SourceA commercial landings (Zenity + Nomotic layouts)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SINA="$HOME/.sina"
mkdir -p "$SINA"

cp "$ROOT/zenity.html" "$SINA/sourcea-commercial-zenity-layout-v1.html"
cp "$ROOT/nomotic.html" "$SINA/sourcea-commercial-nomotic-layout-v1.html"
python3 "$(dirname "$ROOT")/scripts/generate_commercial_onepager_html_v1.py" nomotic >/dev/null 2>&1 || true

open "$ROOT/zenity.html"
open "$ROOT/nomotic.html"

echo "OK: SourceA landings opened"
echo "    $ROOT/zenity.html  (light · Buyer 1)"
echo "    $ROOT/nomotic.html (dark · Asset B + fleet)"
echo "    ~/.sina/sourcea-commercial-zenity-layout-v1.html"
echo "    ~/.sina/sourcea-commercial-nomotic-layout-v1.html"
echo ""
echo "Witness BC (separate): bash WitnessBC-landing/open.sh"
