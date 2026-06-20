#!/usr/bin/env bash
# PORT_CATALOG hub-stabilization stack — :13020 + :13030 SSOT gate (Phase 6).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
catalog_path = ROOT / "PORT_CATALOG.json"
data = json.loads(catalog_path.read_text(encoding="utf-8"))

by_port: dict[int, dict] = {}
for entry in data.get("ports", []):
    if "port" in entry:
        by_port[int(entry["port"])] = entry

hub = by_port.get(13020)
worker = by_port.get(13030)
if not hub or hub.get("owner_id") != "sina_command":
    sys.exit("FAIL: PORT_CATALOG missing 13020 sina_command")
if not worker or worker.get("owner_id") != "hub_rebuild_worker":
    sys.exit("FAIL: PORT_CATALOG missing 13030 hub_rebuild_worker")

meta = data.get("hub_stabilization_ports") or {}
if meta.get("hub") != 13020 or meta.get("worker") != 13030:
    sys.exit("FAIL: hub_stabilization_ports metadata mismatch")

forbidden = {"sina_command", "hub_rebuild_worker"}
for sidecar in (13021, 13022, 13023):
    entry = by_port.get(sidecar)
    if entry and entry.get("owner_id") in forbidden:
        sys.exit(f"FAIL: sidecar port {sidecar} wrongly assigned to hub stack owner")

updated = data.get("catalog_updated_at", "")
if updated < "2026-06-10":
    sys.exit(f"FAIL: catalog_updated_at stale ({updated})")

print("OK: validate-port-catalog-hub-stabilization-v1 · :13020 + :13030 registered")
PY
