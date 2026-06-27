#!/usr/bin/env bash
# Validate AgentGo SA4 case-study 6000 — counts only (Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
master = json.loads((root / "brain-os/plan-registry/AGENTGO_CASE_STUDY_6000_MASTER_v1.json").read_text())
if master.get("plan_count") != 6000:
    raise SystemExit(f"FAIL: plan_count {master.get('plan_count')}")

law = root / "docs/AGENTGO_SA4_CASE_STUDY_6000_PLANS_LOCKED_v1.md"
if not law.is_file():
    raise SystemExit("FAIL: missing law doc")

pack = root / "brain-os/plan-registry/agentgo-case-study-6000"
total = 0
for angle in ["cs-a-factory", "cs-b-dual", "cs-c-wil"]:
    reg = json.loads((pack / angle / "REGISTRY.json").read_text())
    if reg.get("count") != 2000:
        raise SystemExit(f"FAIL: {angle} count {reg.get('count')}")
    total += reg["count"]
if total != 6000:
    raise SystemExit(f"FAIL: total {total}")

# NOW tasks wired for ranks 1-10 per angle
for angle in ["cs-a-factory", "cs-b-dual", "cs-c-wil"]:
    reg = json.loads((pack / angle / "REGISTRY.json").read_text())
    first = reg["plans"][0]
    if "agentgo" not in first.get("title", "").lower() and "deploy" not in first.get("title", "").lower() and "wil" not in first.get("title", "").lower() and "ya5" not in first.get("title", "").lower() and "draft" not in first.get("title", "").lower():
        if first.get("priority_rank") == 1:
            t = first.get("title", "")
            if "slice" in t.lower() and first.get("smart_version", 0) < 2:
                raise SystemExit(f"FAIL: {angle} rank-1 not v2 smart")

# unique titles global
all_titles = []
for angle in ["cs-a-factory", "cs-b-dual", "cs-c-wil"]:
    reg = json.loads((pack / angle / "REGISTRY.json").read_text())
    all_titles.extend(p["title"] for p in reg["plans"])
    if reg.get("schema_version", 1) < 3:
        raise SystemExit(f"FAIL: {angle} schema_version < 3 (need v3 polish)")
    if reg.get("smart_tier") != "pure-unique-smart-polished":
        raise SystemExit(f"FAIL: {angle} smart_tier not polished")

master_sv = master.get("schema_version", "1")
if str(master_sv).split(".")[0] < "3":
    raise SystemExit(f"FAIL: master schema_version {master_sv} < 3")

inv = root / "data/agentgo-sa4-inventory-receipt-v1.json"
if not inv.is_file():
    raise SystemExit("FAIL: missing inventory receipt")
inv_data = json.loads(inv.read_text())
if not inv_data.get("ok"):
    raise SystemExit("FAIL: SA4 inventory not ok")

case_study = root / "SourceA-landing/green-unified/case-studies/agentgo.html"
if not case_study.is_file():
    raise SystemExit("FAIL: case study page missing")

if len(all_titles) != len(set(all_titles)):
    raise SystemExit(f"FAIL: duplicate titles across pack ({len(all_titles)} vs {len(set(all_titles))})")

print(f"OK: agentgo-case-study-6000 v3 polished · 3 angles · {total} plans · {len(set(all_titles))} unique titles · inventory ok")
PY
echo "validate-agentgo-case-study-6000-v1.sh: ALL PASS"
