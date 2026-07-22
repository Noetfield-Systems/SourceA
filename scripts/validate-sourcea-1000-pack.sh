#!/usr/bin/env bash
# Validate sourcea-1000 locked pack — count, registry, sample files
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACK="$ROOT/brain-os/plan-registry/sourcea-1000"
REG="$PACK/REGISTRY.json"

echo "=== validate-sourcea-1000-pack ==="

python3 <<PY
import json, sys
from pathlib import Path

root = Path("$ROOT")
reg_path = root / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
reg = json.loads(reg_path.read_text(encoding="utf-8"))
plans = reg.get("plans") or []
count = len(plans)
if count != 1000:
    print(f"FAIL: expected 1000 plans got {count}")
    sys.exit(1)
if not reg.get("locked"):
    print("FAIL: registry locked must be true")
    sys.exit(1)
if reg.get("library") != "sourcea-1000-locked":
    print("FAIL: library id mismatch")
    sys.exit(1)
print(f"OK: REGISTRY.json count={count} locked=true")

missing = 0
for pl in plans[:20] + plans[500:505] + plans[-5:]:
    p = root / "brain-os/plan-registry/sourcea-1000" / pl["path"]
    if not p.is_file():
        print(f"FAIL: missing {p}")
        missing += 1
    elif "agent_tag: AGENT-AUTO-SOURCEA" not in p.read_text(encoding="utf-8"):
        print(f"FAIL: {p} missing agent_tag")
        missing += 1
if missing:
    sys.exit(1)
print("OK: sample prompt files present and tagged")

md_count = len(list((root / "brain-os/plan-registry/sourcea-1000/prompts").rglob("sa-*.md")))
if md_count != 1000:
    print(f"FAIL: expected 1000 md files got {md_count}")
    sys.exit(1)
print(f"OK: {md_count} prompt markdown files on disk")

done = sum(1 for pl in plans if pl.get("status") == "done")
backlog = sum(1 for pl in plans if pl.get("status") == "backlog")
print(f"OK: status done={done} backlog={backlog}")
PY

for f in SOURCEA-1000-LOCK.md SOURCEA-PRIORITY.md; do
  if [[ ! -f "$ROOT/brain-os/plan-registry/$f" ]]; then
    echo "FAIL: missing brain-os/plan-registry/$f"
    exit 1
  fi
done
echo "OK: LOCK + PRIORITY index present"

python3 "$ROOT/scripts/validate-sourcea-pick-order-v1.py"
bash "$ROOT/scripts/validate-goal-hierarchy-enforce-v1.sh"
bash "$ROOT/scripts/validate-founder-busy-operating-model-v1.sh"
bash "$ROOT/scripts/validate-gatekeeper-v1.sh"
bash "$ROOT/scripts/validate-agent-loop-gate-receipt-v1.sh"

echo "SOURCEA-1000 PACK VALID count=1000"
