#!/usr/bin/env bash
# INCIDENT-038 — next-100 must be mac_control + cloud_forge only; no Mac executes sa-mkt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DOC="$ROOT/data/secondary-cloud-drain-next-100-v1.json"
[[ -f "$DOC" ]] || { echo "FAIL missing $DOC"; exit 1; }
python3 - <<'PY'
import json, sys
from pathlib import Path
doc = json.loads(Path("data/secondary-cloud-drain-next-100-v1.json").read_text())
plans = doc.get("plans") or []
if len(plans) != 100:
    print(f"FAIL expected 100 plans got {len(plans)}")
    sys.exit(1)
mac = [p for p in plans if p.get("plane") == "mac_control"]
cloud = [p for p in plans if p.get("plane") == "cloud_forge"]
if len(mac) != 10 or len(cloud) != 90:
    print(f"FAIL want 10 mac_control + 90 cloud_forge got {len(mac)}+{len(cloud)}")
    sys.exit(1)
for p in cloud:
    if p.get("mac_executes_plan_body") is not False:
        print(f"FAIL {p.get('id')} mac_executes_plan_body must be false")
        sys.exit(1)
    if not p.get("maps_registry", "").startswith("sa-mkt-"):
        print(f"FAIL {p.get('id')} missing sa-mkt map")
        sys.exit(1)
for p in mac:
    if p.get("mac_build_forbidden") is not True:
        print(f"FAIL {p.get('id')} mac control must forbid build")
        sys.exit(1)
if "Worker on Mac runs every plan" not in str(doc.get("forbidden", [])):
    print("FAIL forbidden list missing bad phrase")
    sys.exit(1)
print("PASS secondary-cloud-drain-next-100-v1.json")
PY
echo "PASS validate-secondary-cloud-drain-next-100-v1.sh"
