#!/usr/bin/env bash
# validate-h2-ops-blocker-row-contracts-v1.sh — sa-0821 ops_blocker bucket row contracts
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-ops-blocker-row-contracts-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/2026-06-15/sa-0821-ops-blocker-row-contracts-mp-ship-wire-g3-b-001_LOCKED_v1.md"
REG="${HOME}/.sina/h2-pending-registry-v1.json"
LAW="$ROOT/SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md"

[[ -f "$DOC" ]] || fail "missing LOCKED doc $DOC"
[[ -f "$REG" ]] || fail "missing registry $REG"
[[ -f "$LAW" ]] || fail "missing $LAW"
grep -q "ops_blocker row contracts" "$LAW" || fail "H2 plan missing slot 21 pointer"

python3 - <<'PY' || fail "contract audit"
import json
import re
from pathlib import Path

ROOT = Path(".")
DOC = ROOT / "archive/attachments/2026-06-15/sa-0821-ops-blocker-row-contracts-mp-ship-wire-g3-b-001_LOCKED_v1.md"
REG = Path.home() / ".sina/h2-pending-registry-v1.json"
LIB = (ROOT / "scripts/sina_command_lib.py").read_text(encoding="utf-8")

text = DOC.read_text(encoding="utf-8")
for needle in ("MP-SHIP", "WIRE-G3", "B-001", "ops_blocker", "founder_actions"):
    if needle not in text:
        raise SystemExit(f"LOCKED doc missing {needle}")

if "def ops_blockers" not in LIB:
    raise SystemExit("sina_command_lib.ops_blockers missing")

reg = json.loads(REG.read_text(encoding="utf-8"))
rows = list(reg.get("ops_blocker") or [])
ids = [r.get("id") for r in rows]
expected = ["MP-SHIP", "WIRE-G3", "B-001"]
if ids != expected:
    raise SystemExit(f"ops_blocker ids mismatch: got {ids} want {expected}")

allowed_sev = {"high", "medium", "critical"}
for row in rows:
    rid = row.get("id")
    for key in ("id", "severity", "action"):
        if not row.get(key):
            raise SystemExit(f"{rid}: missing required key {key}")
    if row["severity"] not in allowed_sev:
        raise SystemExit(f"{rid}: bad severity {row['severity']}")

contracts = {
    "MP-SHIP": {"severity": "high", "action_sub": "Vercel"},
    "WIRE-G3": {"severity": "medium", "action_sub": "g3"},
    "B-001": {"severity": "medium", "action_sub": "ARCHITECT"},
}
for row in rows:
    rid = row["id"]
    spec = contracts[rid]
    if row["severity"] != spec["severity"]:
        raise SystemExit(f"{rid}: severity {row['severity']} != {spec['severity']}")
    if spec["action_sub"].lower() not in row["action"].lower():
        raise SystemExit(f"{rid}: action missing {spec['action_sub']}")

# hub projection ids must be subset of canonical set when ops_blockers runs
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from sina_command_lib import ops_blockers  # noqa: E402

cards = ops_blockers({}, {"g3_tailscale": "pending"}, {"milestones": {"MP-SHIP": "open"}})
proj_ids = {c["id"] for c in cards if c.get("id") in set(expected)}
if not {"MP-SHIP", "WIRE-G3"}.issubset(proj_ids):
    raise SystemExit(f"ops_blockers projection missing canonical ids: {proj_ids}")

for card in cards:
    if card.get("id") not in expected:
        continue
    for key in ("id", "severity", "title", "action", "status", "founder_actions"):
        if key not in card:
            raise SystemExit(f"projection {card.get('id')}: missing {key}")

print(f"OK: ops_blocker contracts · registry={len(rows)} rows · projection ids={sorted(proj_ids)}")
PY

echo "OK: validate-h2-ops-blocker-row-contracts-v1 · sa-0821"
