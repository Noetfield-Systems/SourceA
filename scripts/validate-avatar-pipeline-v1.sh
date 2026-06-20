#!/usr/bin/env bash
# validate-avatar-pipeline-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 - <<'PY'
import json
import sys
from pathlib import Path

root = Path(".")
required = [
    "data/avatar-pipeline-config-v1.json",
    "data/avatar-scripts-v1.json",
    "scripts/avatar_pipeline_v1.py",
    "scripts/heygen_avatar_wire_v1.py",
    "scripts/heygen_avatar_setup_v1.py",
    "avatar-pipeline.sh",
]
for rel in required:
    if not (root / rel).is_file():
        print(f"FAIL: missing {rel}")
        sys.exit(1)

cfg = json.loads((root / "data/avatar-pipeline-config-v1.json").read_text())
scripts = json.loads((root / "data/avatar-scripts-v1.json").read_text())
routing = json.loads((root / "data/commercial-film-routing-v1.json").read_text())

if cfg.get("schema") != "avatar-pipeline-config-v1":
    print("FAIL: avatar config schema")
    sys.exit(1)

quality = cfg.get("quality") or {}
if quality.get("tier") != "high":
    print("FAIL: avatar config quality.tier must be 'high'")
    sys.exit(1)
if not quality.get("resolution"):
    print("FAIL: avatar config quality.resolution missing")
    sys.exit(1)

for lane_id in ("linkedin", "trustfield_social", "noetfield_social"):
    if lane_id not in (cfg.get("lanes") or {}):
        print(f"FAIL: missing lane {lane_id}")
        sys.exit(1)

for lane_id, lane in (cfg.get("lanes") or {}).items():
    sid = lane.get("script_id")
    if sid not in (scripts.get("scripts") or {}):
        print(f"FAIL: lane {lane_id} script_id {sid!r} missing")
        sys.exit(1)

rc = routing.get("render_commands") or {}
for key in ("avatar_linkedin", "avatar_trustfield_social", "avatar_noetfield_social", "avatar_setup_check"):
    if key not in rc:
        print(f"FAIL: routing render_commands missing {key}")
        sys.exit(1)

print(f"PASS: avatar pipeline v1 — {len(cfg.get('lanes') or {})} lanes wired")
PY

echo "PASS: validate-avatar-pipeline-v1.sh"
