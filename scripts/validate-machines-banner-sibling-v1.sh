#!/usr/bin/env bash
# validate-machines-banner-sibling-v1.sh — sa-0820 H2 banner sibling-hub copy (not sub-page)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-machines-banner-sibling-v1 — $*" >&2; exit 1; }

html_path="$ROOT/agent-control-panel/machines/index.html"
test -f "$html_path" || fail "missing machines/index.html"

python3 - <<'PY' || fail "disk banner copy"
import re
from pathlib import Path

html = Path("agent-control-panel/machines/index.html").read_text(encoding="utf-8")
m = re.search(r'<div class="banner">(.*?)</div>', html, re.S)
banner = m.group(1) if m else ""
if not banner:
    raise SystemExit("missing .banner block")
low = banner.lower()
if "sibling hub" not in low:
    raise SystemExit("banner must say sibling hub")
if "not a sub-page" not in low:
    raise SystemExit("banner must negate sub-page wording")
if "own url" not in low:
    raise SystemExit("banner must declare own URL")
for bad in ("nested under h1", "child of h1", "sub-page only"):
    if bad in low:
        raise SystemExit(f"forbidden wording: {bad}")
print("OK: disk banner · sibling hub · not a sub-page")
PY

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"
live="$(curl -sf "${BASE}/machines/")"
echo "$live" | grep -qi "sibling hub" || fail "live /machines/ missing sibling hub"
echo "$live" | grep -qi "not a sub-page" || fail "live /machines/ missing not a sub-page negation"

echo "OK: validate-machines-banner-sibling-v1 · sa-0820"
