#!/usr/bin/env bash
# validate-commercial-film-routing-v1.sh — commercial film factory routing SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ROUTING="$ROOT/data/commercial-film-routing-v1.json"
LOCKED="$ROOT/data/COMMERCIAL_FILM_ROUTING_LOCKED_v1.md"

python3 - <<'PY'
import json
import sys
from pathlib import Path

root = Path(".")
routing_path = root / "data/commercial-film-routing-v1.json"
locked_path = root / "data/COMMERCIAL_FILM_ROUTING_LOCKED_v1.md"

if not routing_path.is_file():
    print(f"FAIL: missing {routing_path}")
    sys.exit(1)
if not locked_path.is_file():
    print(f"FAIL: missing {locked_path}")
    sys.exit(1)

data = json.loads(routing_path.read_text(encoding="utf-8"))
if data.get("schema") != "commercial-film-routing-v1":
    print("FAIL: schema must be commercial-film-routing-v1")
    sys.exit(1)

icp = data.get("icp_identity_routing") or {}
if not icp.get("trust_levels") or not icp.get("advisor_idea_to_layer"):
    print("FAIL: missing icp_identity_routing.trust_levels or advisor_idea_to_layer")
    sys.exit(1)
for layer_id in ("L1_face_first", "L2_product_first", "L3_hybrid_hook", "L4_digital_twin"):
    if layer_id not in icp["trust_levels"]:
        print(f"FAIL: icp_identity_routing missing {layer_id}")
        sys.exit(1)
print(f"PASS: ICP identity routing — {len(icp['trust_levels'])} trust levels · {len(icp['advisor_idea_to_layer'])} advisor maps")

beats_files: set[str] = set()
for lane_id, lane in (data.get("lanes") or {}).items():
    for asset_id, asset in (lane.get("assets") or {}).items():
        bf = asset.get("beats_file")
        if bf:
            beats_files.add(bf)
            p = root / bf
            if not p.is_file():
                print(f"FAIL: lanes.{lane_id}.assets.{asset_id} beats_file missing: {bf}")
                sys.exit(1)
            beats = json.loads(p.read_text(encoding="utf-8"))
            ref = beats.get("routing_ref", "")
            if ref and "commercial-film-routing-v1.json" not in ref:
                print(f"FAIL: {bf} routing_ref does not point at routing SSOT")
                sys.exit(1)

required_scripts = [
    "scripts/commercial_short_film_v1.py",
    "scripts/film_elevenlabs_wire_v1.py",
    "scripts/elevenlabs_alignment_to_ass_v1.py",
    "witnessbc-commercial-film.sh",
    "sourcea-commercial-film.sh",
]
for rel in required_scripts:
    if not (root / rel).is_file():
        print(f"FAIL: factory script missing: {rel}")
        sys.exit(1)

# active lanes must have accepted or draft_saved assets
for lane_id in ("witnessbc", "sourcea"):
    lane = data["lanes"][lane_id]
    if lane.get("status") != "active":
        print(f"FAIL: {lane_id} must be active")
        sys.exit(1)

print(f"PASS: routing SSOT v{data.get('version')} — {len(beats_files)} beats files wired")
for bf in sorted(beats_files):
    print(f"  · {bf}")
PY

echo "PASS: validate-commercial-film-routing-v1.sh"
