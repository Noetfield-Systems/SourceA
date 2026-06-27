#!/usr/bin/env bash
# Validate portfolio upgrade canonical — Mac-safe counts + mapping only
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEEP="${1:-}"

python3 - "$ROOT" "$DEEP" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
deep = sys.argv[2] == "--deep"

master = json.loads((root / "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json").read_text())
if master.get("plan_count") != 6000:
    raise SystemExit(f"FAIL: plan_count {master.get('plan_count')}")

mapping_path = root / "data/upgrade-888-to-sa-next-mapping-v1.json"
if not mapping_path.is_file():
    raise SystemExit("FAIL: missing mapping manifest")
mapping = json.loads(mapping_path.read_text())
if mapping.get("entry_count") != 888:
    raise SystemExit(f"FAIL: mapping entry_count {mapping.get('entry_count')}")

sa_reg = json.loads((root / "brain-os/plan-registry/portfolio-next-6000/sourcea/REGISTRY.json").read_text())
legacy_missing = []
for rank in range(1, 889):
    pl = next((p for p in sa_reg["plans"] if p.get("priority_rank") == rank), None)
    if not pl or not pl.get("legacy_upgrade_id"):
        legacy_missing.append(rank)
if legacy_missing:
    raise SystemExit(f"FAIL: missing legacy_upgrade_id at ranks {legacy_missing[:5]}...")

stub = json.loads((root / "brain-os/roadmap/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json").read_text())
if stub.get("status") != "superseded":
    raise SystemExit("FAIL: roadmap 888 stub not superseded")

sup = root / "brain-os/ssot/superseded/SOURCEA_UPGRADE_PLANS_888_REGISTRY_v1.json"
if not sup.is_file() or sup.stat().st_size < 1000:
    raise SystemExit("FAIL: superseded lineage copy missing or too small")

gov = json.loads((root / "data/sourcea-governance-ssot-registry-v1.json").read_text())
ids = {e["id"]: e.get("status") for e in gov.get("entries", [])}
if ids.get("upgrade_plans_888") != "superseded":
    raise SystemExit("FAIL: governance upgrade_plans_888 not superseded")
if ids.get("portfolio_next_6000") != "active":
    raise SystemExit("FAIL: governance portfolio_next_6000 not active")

pack = root / "brain-os/plan-registry/portfolio-next-6000"
total = 0
for repo in ["sourcea", "witnessbc", "noetfield", "trustfield", "virlux", "mono"]:
    reg = json.loads((pack / repo / "REGISTRY.json").read_text())
    if reg.get("count") != 1000:
        raise SystemExit(f"FAIL: {repo} count {reg.get('count')}")
    total += reg["count"]
if total != 6000:
    raise SystemExit(f"FAIL: total {total}")

if deep:
    for pl in sa_reg["plans"][:888]:
        p = pack / "sourcea" / pl["path"]
        if not p.is_file():
            raise SystemExit(f"FAIL: missing prompt {pl['path']}")
    print("OK: deep prompt walk 888 files")

print(f"OK: portfolio-upgrade-canonical · 6000 plans · 888 mapped · governance wired")
PY
echo "validate-portfolio-upgrade-canonical-v1.sh: ALL PASS"
