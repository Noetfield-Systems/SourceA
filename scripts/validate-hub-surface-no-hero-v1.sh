#!/usr/bin/env bash
# validate-hub-surface-no-hero-v1.sh — sa-0815 hub_surface tab slices without command-data hero
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-hub-surface-no-hero-v1 — $*" >&2; exit 1; }

bash "$ROOT/scripts/validate-hub-surface-v1.sh" >/dev/null || fail "validate-hub-surface-v1"

python3 - <<'PY' || fail "no-hero contract"
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(".")
src = (ROOT / "scripts/hub_surface_v1.py").read_text()
if "command-data.json" in src:
    raise SystemExit("hub_surface_v1 must not read command-data.json hero")
if "command-data-shell.json" not in src:
    raise SystemExit("hub_surface_v1 must use command-data-shell.json")

base = "http://127.0.0.1:13020"
with urllib.request.urlopen(base + "/api/surface/v1", timeout=10) as r:
    body = r.read()
    surface = json.loads(body.decode())

if len(body) > 16384:
    raise SystemExit(f"surface too large for slim tab slices: {len(body)} bytes")
if surface.get("schema") != "hub-surface-v1":
    raise SystemExit(f"bad schema: {surface.get('schema')}")

HERO = ROOT / "agent-control-panel/command-data.json"
hero_size = HERO.stat().st_size if HERO.is_file() else 9_000_000
hero_limit = min(max(hero_size // 10, 65536), 2_000_000)

nav = surface.get("nav") or []
if not nav:
    raise SystemExit("nav empty")
for item in nav:
    if not isinstance(item, dict):
        raise SystemExit("nav item not object")
    slice_path = str(item.get("slice") or "")
    if not slice_path.startswith("/api/"):
        raise SystemExit(f"nav slice must be /api/* not hero: {item.get('id')} -> {slice_path!r}")
    url = base + slice_path
    try:
        with urllib.request.urlopen(url, timeout=12) as r:
            if r.status != 200:
                raise SystemExit(f"slice {slice_path} HTTP {r.status}")
            chunk = r.read(hero_limit + 1)
    except Exception as exc:
        raise SystemExit(f"slice load failed {slice_path}: {exc}") from exc
    if len(chunk) > hero_limit:
        raise SystemExit(
            f"slice {slice_path} too large ({len(chunk)} bytes) — likely command-data hero (>{hero_limit})"
        )

print(
    f"OK: hub_surface no-hero · {len(nav)} nav slices · surface={len(body)}b · "
    f"hero_disk={hero_size}b limit={hero_limit}b · queue={surface.get('queue_sa_id')}"
)
PY

echo "OK: validate-hub-surface-no-hero-v1 · sa-0815"
