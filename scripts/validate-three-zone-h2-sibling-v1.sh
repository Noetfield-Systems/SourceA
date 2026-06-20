#!/usr/bin/env bash
# validate-three-zone-h2-sibling-v1.sh — sa-0816 THREE_ZONE_HUB_SPINE: H2 not nested under H1 nav
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-three-zone-h2-sibling-v1 — $*" >&2; exit 1; }

test -f "$ROOT/SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md" || fail "missing three-zone law"

python3 - <<'PY' || fail "H2 sibling navigation law"
import json
from pathlib import Path

root = Path(".")
boot = json.loads((root / "agent-control-panel/worker-hub/boot.json").read_text(encoding="utf-8"))
h1 = (root / "agent-control-panel/worker-hub/index.html").read_text(encoding="utf-8")
h2 = (root / "agent-control-panel/machines/index.html").read_text(encoding="utf-8")

hero = boot.get("hero_actions") or []
h2_hero = [
    a
    for a in hero
    if isinstance(a, dict)
    and (a.get("id") == "h2_machines" or "/machines/" in (a.get("path") or ""))
]
if not h2_hero:
    raise SystemExit("boot hero_actions missing h2_machines sibling")

up = boot.get("upgrade") or {}
if up.get("daily_url") != "/":
    raise SystemExit(f"daily_url must be / got {up.get('daily_url')!r}")
if up.get("h2_machines_url") != "/machines/":
    raise SystemExit(f"h2_machines_url must be /machines/ got {up.get('h2_machines_url')!r}")

dr = boot.get("daily_rooms") or {}
for key, val in dr.items():
    if key == "actions" or not isinstance(val, dict):
        continue
    if "/machines/" in json.dumps(val):
        raise SystemExit(f"daily_rooms.{key} embeds /machines/ — H2 must stay sibling")

if "iframe" in h1.lower() and "machines" in h1.lower():
    raise SystemExit("H1 must not iframe /machines/")
if "sibling" not in h1.lower():
    raise SystemExit("H1 index missing sibling-hub language")
if "sibling hub" not in h2.lower() or "not a sub-page" not in h2.lower():
    raise SystemExit("H2 must declare sibling hub · not a sub-page")

print(
    f"OK: validate-three-zone-h2-sibling-v1 · hero_h2={len(h2_hero)} "
    f"daily={up.get('daily_url')} h2={up.get('h2_machines_url')}"
)
PY

bash "$ROOT/scripts/validate-machine-hub-v1.sh" >/dev/null || fail "machine-hub sibling route"

echo "OK: validate-three-zone-h2-sibling-v1 · sa-0816"
