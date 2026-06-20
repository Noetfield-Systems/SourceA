#!/usr/bin/env bash
# validate-machine-hub-staleness-auto-heal-v1.sh — sa-0812 H2 auto-heal path cross-check
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${SINA_COMMAND_URL:-http://127.0.0.1:13020}"

fail() { echo "FAIL: validate-machine-hub-staleness-auto-heal-v1 — $*" >&2; exit 1; }

curl -sf "${BASE}/health" >/dev/null || fail "hub not up"

python3 - <<'PY' || fail "staleness contract"
import inspect
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from machine_hub_staleness_v1 import (  # noqa: E402
    AGING_SEC,
    CRITICAL_SEC,
    STALE_SEC,
    machine_hub_staleness_probe,
)

now = datetime.now(timezone.utc)

def probe_at(age_sec: float, *, form_aligned: bool = True) -> dict:
    ts = (now - timedelta(seconds=age_sec)).isoformat().replace("+00:00", "Z")
    reg = {"updated_at": ts, "form_open": {"count": 0}}
    if not form_aligned:
        reg["form_open"] = {"count": 99}
    return machine_hub_staleness_probe(registry=reg)

cases = [
    (30, True, "fresh", False),
    (AGING_SEC + 10, True, "aging", False),
    (STALE_SEC + 10, True, "stale", True),
    (CRITICAL_SEC + 10, True, "critical", True),
    (30, False, "critical", True),
]
for age, aligned, want_status, want_heal in cases:
    row = probe_at(age, form_aligned=aligned)
    if row.get("status") != want_status:
        raise SystemExit(f"age={age} aligned={aligned}: status={row.get('status')} want={want_status}")
    if bool(row.get("auto_heal_recommended")) != want_heal:
        raise SystemExit(
            f"age={age} aligned={aligned}: auto_heal={row.get('auto_heal_recommended')} want={want_heal}"
        )

src = Path("scripts/machine_hub_v1.py").read_text()
if "_maybe_sync_registry" not in src or "auto_heal_recommended" not in src:
    raise SystemExit("machine_hub_v1 missing _maybe_sync_registry auto_heal gate")

as_src = Path("scripts/worker_anti_staleness_heal_v1.py").read_text()
if "machine_hub_staleness_probe" not in as_src or "h2_health_before" not in as_src:
    raise SystemExit("worker_anti_staleness_heal missing H2 probe in need_heal path")

machines = Path("agent-control-panel/machines/index.html").read_text()
if "auto_heal_recommended" not in machines or "runHeal" not in machines:
    raise SystemExit("machines/index.html missing auto_heal → runHeal wiring")

print(
    f"OK: staleness contract fresh/aging/stale/critical · thresholds "
    f"aging={AGING_SEC}s stale={STALE_SEC}s critical={CRITICAL_SEC}s"
)
PY

python3 - <<'PY' || fail "live API health"
import json, os, urllib.request
base = os.environ.get("SINA_COMMAND_URL", "http://127.0.0.1:13020")
with urllib.request.urlopen(base + "/api/machine-hub/v1", timeout=8) as r:
    d = json.loads(r.read().decode())
h = d.get("health") or {}
if h.get("schema") != "machine-hub-staleness-v1":
    raise SystemExit(f"bad health schema: {h.get('schema')}")
if "auto_heal_recommended" not in h:
    raise SystemExit("live API missing auto_heal_recommended")
print(f"OK: live H2 health={h.get('status')} auto_heal={h.get('auto_heal_recommended')}")
PY

echo "OK: validate-machine-hub-staleness-auto-heal-v1 · sa-0812"
