#!/usr/bin/env bash
# Open C12 SourceA clone in default browser
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
open "$ROOT/index.html"
echo "OK: C12 SourceA clone → $ROOT/index.html"
