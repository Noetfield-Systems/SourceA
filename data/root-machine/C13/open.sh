#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
open "$ROOT/index.html"
echo "OK: C13 Nomotic clone → $ROOT/index.html"
