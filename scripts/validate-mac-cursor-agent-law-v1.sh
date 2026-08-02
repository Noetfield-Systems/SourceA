#!/usr/bin/env bash
# validate-mac-cursor-agent-law-v1.sh — Mac Cursor Agent Law gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$HOME/Desktop/MacLaw/MAC_CURSOR_AGENT_LAW_LOCKED_v1.md"
fail() { echo "FAIL: validate-mac-cursor-agent-law-v1 — $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing law: $LAW"
[[ -f "$ROOT/scripts/cursor_agent_law_v1.py" ]] || fail "missing enforce module"
[[ -f "$ROOT/scripts/founder_mac_fresh_start_v1.py" ]] || fail "missing fresh-start module"
[[ -f "$ROOT/scripts/cursor_ultra_light_v1.py" ]] || fail "missing ultra-light module"

python3 "$ROOT/scripts/cursor_agent_law_v1.py" --enforce --json >/dev/null \
  || fail "cursor_agent_law enforce failed"

[[ -f "$HOME/.sina/cursor-ultra-light-v1.flag" ]] || fail "missing cursor-ultra-light flag"
[[ -f "$HOME/.sina/mac-cloud-body-only-v1.flag" ]] || fail "missing mac-cloud-body-only flag"

echo "PASS: validate-mac-cursor-agent-law-v1.sh"
