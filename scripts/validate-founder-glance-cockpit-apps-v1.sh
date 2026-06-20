#!/usr/bin/env bash
# validate-founder-glance-cockpit-apps-v1.sh — all Mac cockpit apps wired to founder_glance SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
fail=0

check() { if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi; }

echo "=== Founder Glance Cockpit Apps — full wire audit ==="

check test -f "$ROOT/data/founder-glance-cockpit-apps-v1.json"
check test -f "$ROOT/brain-os/law/enforcement/SINA_FOUNDER_GLANCE_COCKPIT_APPS_LOCKED_v1.md"

python3 <<PY || fail=1
import json, os, urllib.request
from pathlib import Path

ROOT = Path("${ROOT}")
registry = json.loads((ROOT / "data/founder-glance-cockpit-apps-v1.json").read_text())
apps = registry.get("apps") or {}

# Link graph + command lib standalone URLs
link_py = (ROOT / "scripts/sina_link_graph.py").read_text()
cmd_py = (ROOT / "scripts/sina_command_lib.py").read_text()
for app_id, cfg in apps.items():
    url = cfg.get("url", "")
    port = cfg.get("port")
    assert url in link_py or f":{port}" in link_py, f"sina_link_graph missing {url}"
    assert f":{port}" in cmd_py or url in cmd_py, f"sina_command_lib missing :{port} for {app_id}"

for app_id, cfg in apps.items():
    port = cfg["port"]
    contract_rel = cfg.get("contract")
    if app_id == "mac_health":
        continue  # dedicated validator
    contract = json.loads((ROOT / contract_rel).read_text())
    base = f"http://127.0.0.1:{port}"
    try:
        html = urllib.request.urlopen(f"{base}/", timeout=8).read().decode()
    except Exception as e:
        raise AssertionError(f"{app_id} UI not reachable on {base}: {e}") from e
    for needle in contract.get("dom_must_contain") or []:
        assert needle in html, f"{app_id} missing {needle!r}"
    for bad in contract.get("dom_must_not_contain") or []:
        assert bad not in html, f"{app_id} forbidden {bad!r}"
    health = json.loads(urllib.request.urlopen(f"{base}/health", timeout=8).read())
    ui = health.get("ui_contract") or {}
    assert ui.get("ui_mode") == "founder_glance", f"{app_id} health ui_contract {ui}"
    assert ui.get("primary_cta") == cfg.get("primary_cta"), f"{app_id} primary_cta"
    assert ui.get("tab_count") == 0, f"{app_id} tab_count"
    print(f"PASS: {app_id} :{port} founder_glance wired")
PY

check bash "$ROOT/scripts/validate-mac-health-founder-glance-v1.sh"

# Static wiring — no stale hub mini-app URLs for cockpit fleet
for stale in \
  "13020/mini-apps/apple-health" \
  "mini-apps/apple-health"; do
  if rg -q "$stale" scripts/sina_link_graph.py scripts/sina_command_lib.py scripts/apple_health_mini.py scripts/roadmaps_goals.py 2>/dev/null; then
    echo "FAIL: stale hub URL still present: $stale"
    fail=1
  else
    echo "PASS: no stale $stale in core wiring"
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo "validate-founder-glance-cockpit-apps-v1: ALL PASS"
  exit 0
fi
echo "validate-founder-glance-cockpit-apps-v1: FAILED"
exit 1
