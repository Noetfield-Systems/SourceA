#!/usr/bin/env bash
# validate-serve-panel-build-v1.sh — serve must not swallow panel build failures (AS-13)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVE="$ROOT/scripts/serve-sina-command.sh"

fail() { echo "FAIL: validate-serve-panel-build-v1 — $*" >&2; exit 1; }

[[ -f "$SERVE" ]] || fail "missing serve-sina-command.sh"

if grep -q 'build-sina-command-panel.py.*|| true' "$SERVE"; then
  fail "serve-sina-command.sh still swallows panel build with || true"
fi

grep -q "panel_build_stale" "$SERVE" || fail "serve must set panel_build_stale flag on build fail"

echo "OK: validate-serve-panel-build-v1"
