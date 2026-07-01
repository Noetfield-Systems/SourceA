#!/usr/bin/env bash
# validate-sourcea-boot-v1.sh — Graphify-class chain tool wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-sourcea-boot-v1 — $*" >&2; exit 1; }

PKG="$ROOT/packages/sourcea-boot"
LAW="$ROOT/brain-os/law/SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md"
CRITIC="$ROOT/scripts/critic_boot_v1.py"

[[ -d "$PKG/src/sourcea_boot" ]] || fail "missing package $PKG"
[[ -f "$LAW" ]] || fail "missing chain tools law $LAW"
[[ -f "$CRITIC" ]] || fail "missing critic_boot $CRITIC"

python3 - <<'PY' || fail "chain tools law contract"
from pathlib import Path
text = Path("brain-os/law/SOURCEA_CHAIN_TOOLS_PUBLISH_LOCKED_v1.md").read_text(encoding="utf-8")
for needle in ("sourcea-boot", "Graphify", "BOOT_REPORT.json", "pip install sourcea-boot", "hello@sourcea.app"):
    if needle not in text:
        raise SystemExit(f"missing {needle}")
print("OK: chain tools law contract")
PY

export PYTHONPATH="$PKG/src:${PYTHONPATH:-}"
BOOT_JSON="$(python3 -m sourcea_boot.cli --json 2>/dev/null || true)"
[[ -n "$BOOT_JSON" ]] || fail "sourcea-boot produced no JSON"
printf '%s' "$BOOT_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('schema') == 'sourcea-boot-v1'
assert row.get('verdict') in ('PASS', 'BLOCK')
assert len(row.get('checks') or []) == 4
print('OK: sourcea-boot CLI · 4 checks · verdict', row.get('verdict'))
" || fail "boot CLI contract"

[[ -f BOOT_REPORT.json ]] || fail "BOOT_REPORT.json not written"
rm -f BOOT_REPORT.json

python3 "$CRITIC" --json >/dev/null 2>&1 || true
CRITIC_JSON="$(python3 "$CRITIC" --json 2>/dev/null || true)"
[[ -n "$CRITIC_JSON" ]] || fail "critic_boot produced no JSON"
printf '%s' "$CRITIC_JSON" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('verdict') in ('PASS', 'BLOCK')
assert len(row.get('checks') or []) == 4
print('OK: critic_boot_v1 bridge')
" || fail "critic_boot still works"

echo "OK: validate-sourcea-boot-v1 · chain tool wired"
