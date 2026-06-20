#!/usr/bin/env bash
# validate-three-zone-hub-spine-v1.sh — sa-0816 H2 sibling not nested under H1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-three-zone-hub-spine-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"
test -f "$ROOT/SOURCEA_THREE_ZONE_HUB_SPINE_LOCKED_v1.md" || fail "missing three-zone law"

bash "$ROOT/scripts/validate-machine-hub-v1.sh" >/dev/null || fail "validate-machine-hub-v1"

python3 - <<'PY' || fail "three-zone navigation contract"
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(".")
base = "http://127.0.0.1:13020"

h1 = (ROOT / "agent-control-panel/worker-hub/index.html").read_text()
h2 = (ROOT / "agent-control-panel/machines/index.html").read_text()

if "sibling" not in h1.lower() or "/machines/" not in h1:
    raise SystemExit("H1 must link /machines/ as sibling hub")
if re.search(r'<iframe[^>]+machines', h1, re.I):
    raise SystemExit("H1 must not iframe H2 (nested)")
if "sub-page" in h2.lower() and "not a sub-page" not in h2.lower():
    raise SystemExit("H2 banner must deny sub-page nesting")
if "sibling hub" not in h2.lower():
    raise SystemExit("H2 must declare sibling hub")

with urllib.request.urlopen(base + "/api/machine-hub/v1", timeout=10) as r:
    mh = json.loads(r.read().decode())
if mh.get("hub") != "H2":
    raise SystemExit("machine-hub must be H2")
if mh.get("h1_url") not in ("/", "http://127.0.0.1:13020/"):
    raise SystemExit(f"unexpected h1_url: {mh.get('h1_url')}")
if "/legacy/" not in str(mh.get("legacy_url") or ""):
    raise SystemExit("machine-hub must expose legacy_url separately")

with urllib.request.urlopen(base + "/api/worker-hub/v1", timeout=10) as r:
    wh = json.loads(r.read().decode())
if not wh.get("ok"):
    raise SystemExit("worker-hub ok=false")
if wh.get("hub") == "H2" or "/machines/" in str(wh.get("api") or ""):
    raise SystemExit("worker-hub must remain H1-only API")

code = urllib.request.urlopen(base + "/machines/").status
if code != 200:
    raise SystemExit(f"/machines/ HTTP {code}")

print("OK: three-zone spine · H1=/ · H2=/machines/ sibling · legacy separate")
PY

echo "OK: validate-three-zone-hub-spine-v1 · sa-0816"
