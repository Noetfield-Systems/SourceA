#!/usr/bin/env bash
# UI-0 — unified SVG icon system; no emoji/legacy glyphs in sidebar nav.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ICON_JS="$ROOT/agent-control-panel/assets/icon-system-v1.js"
APP_JS="$ROOT/agent-control-panel/assets/app.js"
SHELL_HTML="$ROOT/agent-control-panel/assets/shell.html"
INDEX_HTML="$ROOT/agent-control-panel/index.html"

test -f "$ICON_JS" || { echo "FAIL: missing icon-system-v1.js"; exit 1; }
grep -q "icon-system-v1.js" "$SHELL_HTML" || { echo "FAIL: shell.html missing icon-system-v1.js script"; exit 1; }
grep -q "scIcon(" "$APP_JS" || { echo "FAIL: app.js buildNav must use scIcon"; exit 1; }
grep -q 'sc-nav-icon">\${scIconOrText' "$APP_JS" || grep -q "scIconOrText(it.icon" "$APP_JS" || {
  echo "FAIL: buildNav must render icons via scIconOrText"
  exit 1
}

python3 - <<'PY'
import re
import sys
from pathlib import Path

root = Path(".")
app = (root / "agent-control-panel/assets/app.js").read_text(encoding="utf-8")
icons_js = (root / "agent-control-panel/assets/icon-system-v1.js").read_text(encoding="utf-8")

# Extract registered icon keys from icon-system-v1.js
registered = set(re.findall(r'^\s+"?([a-z][a-z0-9-]*)"?\s*:', icons_js, re.M))
registered |= set(re.findall(r"^\s+([a-z][a-z0-9-]*):\s*'<", icons_js, re.M))

emoji_re = re.compile(r"[\U0001F300-\U0001FAFF]")
legacy_re = re.compile(r"^[\u25CE\u25C6\u25C7\u2302\u27A1\u25A3\u25C8\u2B21\u2301\u25CB\u25C9\u27F3\u27E1\u2630\u25A4\u2387?]$")

# Parse NAV block icon fields
nav_start = app.find("const NAV = [")
nav_end = app.find("const PAGE = ", nav_start)
if nav_start < 0 or nav_end < 0:
    print("FAIL: could not locate NAV block", file=sys.stderr)
    sys.exit(1)
nav_block = app[nav_start:nav_end]
icons = re.findall(r'icon:\s*"([^"]+)"', nav_block)

errors = []
for ic in icons:
    if emoji_re.search(ic):
        errors.append(f"NAV icon is emoji: {ic!r}")
    if legacy_re.match(ic) or (len(ic) == 1 and ord(ic) > 127 and not ic.isascii()):
        errors.append(f"NAV icon is legacy glyph: {ic!r}")
    if ic not in registered:
        errors.append(f"NAV icon not registered in icon-system-v1.js: {ic!r}")

if "${it.icon}" in nav_block and "scIconOrText" not in app[app.find("function buildNav"):app.find("function buildNav") + 2500]:
    errors.append("buildNav still injects raw it.icon")

for path in (root / "agent-control-panel/index.html", root / "agent-control-panel/assets/shell.html"):
    text = path.read_text(encoding="utf-8")
    if "\U0001F6D1" in text or "\U0001F6E1" in text:
        errors.append(f"{path.name}: top bar still uses emoji Emergency/Safety")

if errors:
    print("FAIL: validate-icon-system-v1")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: validate-icon-system-v1 · {len(icons)} NAV icons registered")
PY

echo "OK: validate-icon-system-v1"
