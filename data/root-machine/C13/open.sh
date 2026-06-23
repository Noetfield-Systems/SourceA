#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
open "$ROOT/index.html"
echo "OK: C13 SourceA clone → $ROOT/index.html"
