#!/usr/bin/env bash
# Open C12 Zenity clone in default browser
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
open "$ROOT/index.html"
echo "OK: C12 Zenity clone → $ROOT/index.html"
