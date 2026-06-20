#!/usr/bin/env bash
# Sync + open SourceA commercial landings (SourceA + SourceA layouts)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SINA="$HOME/.sina"
mkdir -p "$SINA"

cp "$ROOT/sourcea-layout-light.html" "$SINA/sourcea-commercial-sourcea-layout-light-layout-v1.html"
cp "$ROOT/sourcea-layout-dark.html" "$SINA/sourcea-commercial-sourcea-layout-dark-layout-v1.html"
python3 "$(dirname "$ROOT")/scripts/generate_commercial_onepager_html_v1.py" sourcea-layout-dark >/dev/null 2>&1 || true

open "$ROOT/sourcea-layout-light.html"
open "$ROOT/sourcea-layout-dark.html"

echo "OK: SourceA landings opened"
echo "    $ROOT/sourcea-layout-light.html  (light · Buyer 1)"
echo "    $ROOT/sourcea-layout-dark.html (dark · Asset B + fleet)"
echo "    ~/.sina/sourcea-commercial-sourcea-layout-light-layout-v1.html"
echo "    ~/.sina/sourcea-commercial-sourcea-layout-dark-layout-v1.html"
echo ""
echo "Witness BC (separate): bash WitnessBC-landing/open.sh"
